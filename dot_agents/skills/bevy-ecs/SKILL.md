---
name: bevy-ecs
description: Bevy 0.15+ ECS 性能优化指南。当项目使用 Bevy 引擎或其他 Archetype ECS 时使用。涵盖存储策略、Archetype 碎片化、变更检测、Run Conditions、Observers、并行迭代、实战优化清单、微优化技巧和 profiling 基础设施。
---

# Bevy ECS 性能优化

> 适用于 Bevy 0.15+，核心原则通用于所有 Archetype ECS。

## 1. 存储策略选择

```rust
#[derive(Component)]  // 默认 Table（SoA 连续内存），迭代快
struct Transform { /* ... */ }

#[derive(Component)]
#[component(storage = "SparseSet")]  // 频繁增删的临时标记
struct Poisoned;
```

| 策略 | 迭代 | 增删 | 适用 |
|------|------|------|------|
| Table（默认） | 快(连续内存) | 慢(archetype 迁移) | 稳定组件：Transform, Mesh, Health |
| SparseSet | 慢 | 快(无迁移) | 临时标记：Buff、状态 Flag |

> **判断标准**：组件生命周期 < 实体生命周期的 10% → SparseSet。

## 2. Archetype 碎片化（最常见性能杀手）

每种**唯一的组件组合**产生一个 Archetype，Archetype 越多，每个 Table 越小，迭代连续性越差。

```rust
// ❌ 每种敌人一个标记组件 → archetype 爆炸
#[derive(Component)] struct Goblin;
#[derive(Component)] struct Skeleton;
#[derive(Component)] struct Dragon;
// Archetype: (Enemy, Goblin, Transform, ...)
// Archetype: (Enemy, Skeleton, Transform, ...)
// Archetype: (Enemy, Dragon, Transform, ...)

// ✅ 用枚举字段 → 共享一个 archetype
#[derive(Component)]
enum EnemyType { Goblin, Skeleton, Dragon }
// Archetype: (Enemy, EnemyType, Transform, ...) ← 只有一个
```

```rust
// ❌ Optional 组件拆分成两个 Query → 碎片化
fn sys(
    q1: Query<(&A, &B), Without<C>>,
    q2: Query<(&A, &B, &C)>,
) { ... }

// ✅ 一个 Query + Option → 减少碎片
fn sys(query: Query<(&A, &B, Option<&C>)>) {
    for (a, b, maybe_c) in &query {
        if let Some(c) = maybe_c { /* ... */ }
    }
}
```

## 3. 变更检测（减少无效工作）

```rust
// 只处理本帧变化的实体，跳过未变化的整个 archetype chunk
fn sync_physics(query: Query<&Transform, Changed<Transform>>) {
    for transform in &query {
        // 10000 个实体可能只有 10 个变了
    }
}

// 资源级变更检测
fn update_ui(settings: Res<Settings>) {
    if !settings.is_changed() { return; }
    // ...
}
```

> `Changed<T>` 的粒度是 archetype table chunk，不是单个实体。同一 chunk 内任一实体变化，整个 chunk 都会被遍历。

## 4. Run Conditions（跳过整个 System）

```rust
app.add_systems(
    Update,
    (
        player_input.run_if(in_state(GameState::Playing)),
        pause_menu.run_if(in_state(GameState::Paused)),
        // 条件不满足 → system 完全不执行，零开销
        expensive_ai.run_if(any_enemies_alive),
    ),
);

// 自定义 run condition
fn any_enemies_alive(query: Query<(), With<Enemy>>) -> bool {
    !query.is_empty()
}
```

## 5. Observers vs 轮询（事件驱动优于每帧遍历）

```rust
// ❌ 每帧轮询新增实体
fn detect_new_enemies(query: Query<&Enemy, Added<Enemy>>) {
    for enemy in &query { /* ... */ }
}

// ✅ Observer：精确触发，实体多时差距巨大
app.add_observer(on_add_enemy);

fn on_add_enemy(trigger: Trigger<OnAdd, Enemy>, query: Query<&Transform>) {
    let entity = trigger.target();
    // 只在实际添加时触发
}
```

| 方式 | 10 万实体 0 变化 | 10 万实体 1 变化 |
|------|-----------------|-----------------|
| `Added<T>` 轮询 | 遍历全表（慢） | 遍历全表找到 1 个 |
| Observer | 不执行 | 精确触发 1 次 |

## 6. Query 过滤优化

```rust
// With/Without 在 archetype 匹配阶段过滤，迭代时零开销
fn move_players(query: Query<&mut Transform, (With<Player>, Without<Dead>)>) { ... }

// 用 AnyOf 代替多个 Optional
fn sys(query: Query<&Transform, AnyOf<(&A, &B, &C)>>) {
    // 至少有 A/B/C 其中一个的实体
}
```

## 7. 并行迭代

```rust
// 多线程并行，按 archetype table 分片
fn move_system(mut query: Query<(&mut Transform, &Velocity)>) {
    query.par_iter_mut().for_each(|(mut transform, velocity)| {
        transform.translation += velocity.0 * dt;
    });
}
```

> **注意**：`par_iter` 是任务并行（多线程），不是数据并行（SIMD）。每个线程内仍然逐实体迭代。

## 8. Bevy 没有的（已知局限）

| 缺失能力 | 说明 | 替代方案 |
|----------|------|---------|
| 列级裸指针访问 | 无法拿到 `*const T` + count 做 SIMD | 热路径数据放 ECS 外的 `Vec<T>`，手动 SIMD |
| 向量批处理 API | `iter_batches()` 拿到的仍是单个引用 | 用 `unsafe` 访问内部 `Table::Column`（脆弱） |
| Zero-copy 跨 System 共享 | System 间通过调度器隔离 | `Res<T>` 共享只读数据 |

> 对于 UI 应用和常规游戏逻辑，以上局限不构成实际瓶颈。只有粒子系统、大规模物理模拟（10 万+ 同质实体）才需要绕过。

## 9. 性能瓶颈排查优先级

```
1. Archetype 碎片化    → 合并标记组件为枚举，减少 Optional 拆分
2. 不必要的每帧轮询    → 改用 Changed / Observer / run_if
3. Entity 数量爆炸     → 合批渲染，虚拟滚动
4. System 串行化       → 检查读写冲突，拆分 Query 解除依赖
5. 组件频繁增删        → 改用 SparseSet 存储
6. 缺少 SIMD 批处理   → 热路径提到 ECS 外部处理
```

## 10. 实战优化清单（从实际评审提炼）

### ❌ 无脑 `.chain()` 是最大的反模式

```rust
// ❌ 全部串行，浪费多核
.add_systems(Update, (
    targeting, fire, move_proj, detect_hits, damage, status, visuals,
).chain())

// ✅ 按真实数据依赖用 .after()
.add_systems(Update, (
    targeting,
    fire.after(targeting),
    move_proj,  // 与 fire 无数据依赖，并行执行（1 帧延迟可接受）
    detect_hits.after(fire).after(move_proj),
    damage.after(detect_hits),
    status.after(damage),
    visuals.after(status),
))
```

> **判断标准**：两个 system 读写的组件不重叠 → 不该串行。  
> **可接受的延迟**：弹道移动和目标获取差 1 帧，玩家感知不到。

### ✅ 每个 System 开头加快速路径

```rust
// ✅ 空集合快速返回，省掉调度开销
fn tick_status_effects(mut query: Query<&mut StatusEffects>) {
    if query.is_empty() { return; }
    // ...
}

fn tick_auras(towers: Query<...>, enemies: Query<...>) {
    if towers.is_empty() || enemies.is_empty() { return; }
    // ...
}
```

### ✅ 高频组件的 `Vec<T>` 改 `SmallVec`

```rust
use smallvec::SmallVec;

// ❌ 每帧 tick 都可能触发堆分配
pub struct StatusEffects(pub Vec<StatusEffect>);

// ✅ 内联 4 个（覆盖 95% 场景），溢出才堆分配
pub struct StatusEffects(pub SmallVec<[StatusEffect; 4]>);
```

**判断标准**：
- 组件在热路径（每帧遍历所有实体）→ 必须 SmallVec
- 组件稳定（创建后不变）→ 保持 Vec，别过度优化
- 容量 = P95 实际长度（不是最大值）

### ✅ 空间索引代替 O(M×N)

```rust
// ❌ 每塔遍历所有敌人
for tower in &towers {
    for enemy in &enemies { ... }
}

// ✅ Uniform Grid（XZ 平面，cell_size ≈ 最大攻击半径）
pub struct SpatialGrid {
    cells: HashMap<CellKey, SmallVec<[GridEntry; 4]>>,
    cell_size: f32,
}

for tower in &towers {
    grid.query_radius(tower.pos, tower.range, |enemy| { ... });
}
```

**复用查询结果**：多层/多效果共用同一次网格查询，不要每个效果都查一次。

### ✅ 死亡/状态变更用 `Changed<T>` 代替轮询

```rust
// ❌ 每帧遍历所有敌人检查血量
fn check_death(query: Query<(Entity, &Health)>) { ... }

// ✅ 只在 Health 变化时检查
fn check_death(query: Query<(Entity, &Health), Changed<Health>>) { ... }
```

### ✅ 资源句柄预加载

```rust
// ❌ 每次生成实体都 load
fn spawn_projectile(asset_server: Res<AssetServer>, ...) {
    let scene = asset_server.load("models/proj.glb#Scene0");  // 每次都查缓存
    commands.spawn(SceneRoot(scene));
}

// ✅ 游戏启动时预加载，运行时克隆句柄
#[derive(Resource)]
struct ProjectileAssets { scene: Handle<Scene> }

fn preload(mut commands: Commands, server: Res<AssetServer>) {
    commands.insert_resource(ProjectileAssets {
        scene: server.load("models/proj.glb#Scene0"),
    });
}

fn spawn_projectile(assets: Res<ProjectileAssets>, ...) {
    commands.spawn(SceneRoot(assets.scene.clone()));  // 只 clone Arc
}
```

## 11. 代码级微优化

### sqrt 延迟计算

```rust
// ❌ 不管距离多远都算 sqrt
let dist = pos.distance(other);
if dist < range { damage *= 1.0 - dist / range; }

// ✅ 先用 distance_squared 筛选，通过的才算 sqrt
let range_sq = range * range;
let dist_sq = pos.distance_squared(other);
if dist_sq > range_sq { continue; }  // 大多数敌人在这里被筛掉
let dist = dist_sq.sqrt();  // 只有少数需要算

// ✅✅ 完全避免 sqrt：用平方比设计衰减曲线
let ratio_sq = dist_sq / range_sq;
damage *= 1.0 - ratio_sq * 0.5;  // 衰减曲线变陡，但游戏体感仍合理
```

### 多次 `.iter().any()` 合并为单次遍历

```rust
// ❌ 4 次扫描同一个 Vec
let frozen = effects.iter().any(|e| matches!(e, Frozen { .. }));
let burning = effects.iter().any(|e| matches!(e, Burning { .. }));
let shocked = effects.iter().any(|e| matches!(e, Shocked { .. }));
let poisoned = effects.iter().any(|e| matches!(e, Poisoned { .. }));

// ✅ 单次遍历，match 分发
let (mut frozen, mut burning, mut shocked, mut poisoned) = (false, false, false, false);
for e in effects {
    match e {
        Frozen { .. } => frozen = true,
        Burning { .. } => burning = true,
        Shocked { .. } => shocked = true,
        Poisoned { .. } => poisoned = true,
    }
}
```

### 常量参数预计算到实体组件

```rust
// ❌ 每帧/每次开火都重算权重和
fn fire(towers: Query<&SkillLayers>) {
    for skills in &towers {
        let total: f32 = skills.iter().map(|s| s.weight).sum();  // 权重不变，浪费
        // 用 total 做加权随机...
    }
}

// ✅ 塔创建时计算一次，存入组件
#[derive(Component)]
struct PrecomputedWeight { total: f32 }

fn on_tower_spawn(mut commands: Commands, skills: &SkillLayers, entity: Entity) {
    let total = skills.iter().map(|s| s.weight).sum();
    commands.entity(entity).insert(PrecomputedWeight { total });
}
```

### Handle / Arc 数据避免频繁 clone

```rust
// ❌ 每次开火 clone 整个特效列表
for layer in &attack_layers {
    let effects: Vec<Effect> = layer.on_hit_effects.clone();  // 可能是 Vec<Arc<T>>
    spawn_projectile_with_effects(effects);
}

// ✅ 用 Arc<Vec<T>>，clone 只增引用计数
#[derive(Clone)]
struct AttackLayer {
    on_hit_effects: Arc<[Effect]>,  // 不可变共享数据
}
```

## 12. Profiling 基础设施（早建晚省）

项目超过 5000 行就应该建：

```rust
// 1. 自定义诊断点，覆盖每个热路径 system
pub const TARGETING_MS: DiagnosticPath = DiagnosticPath::const_new("targeting_ms");
pub const DAMAGE_MS: DiagnosticPath = DiagnosticPath::const_new("damage_ms");

fn targeting(mut diagnostics: Diagnostics, ...) {
    let t0 = Instant::now();
    // ... system 逻辑
    diagnostics.add_measurement(&TARGETING_MS, || t0.elapsed().as_secs_f64() * 1000.0);
}

// 2. FPS 叠加层（像素级绘制曲线，避免 UI 节点堆砌）
//    记录 600 帧历史 + 0.1% Low 百分位
//    F10 切换显示

// 3. 控制台定期输出（1 秒一次，按需打开）
```

**什么时候该建**：出现"感觉卡但不知道卡哪"时。自己猜瓶颈十次有九次猜错，上诊断点直接定位。

## 13. 评审时的六步检查法

```
1. grep .chain() → 检查是否过度串行，能否改 .after()
2. grep "pub struct.*Vec<" 组件定义 → 高频组件是否该用 SmallVec
3. grep "distance(" → 是否可改 distance_squared()
4. grep "asset_server.load" → 是否在热路径而非预加载
5. grep "Query<" + 看系统开头 → 是否加了 is_empty() 快速路径
6. 看 Query filter → 是否该加 Changed<T>
```
