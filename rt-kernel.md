# PREEMPT_RT 实时内核编译与调优指南

> 最后更新：2026-03-17
> 覆盖平台：x86_64 / RK3588 (ARM64) / Jetson Thor & Orin (ARM64)

---

## 重要更新：PREEMPT_RT 已合入主线内核

自 Linux 6.12（2024 年 9 月 20 日）起，PREEMPT_RT 已正式合入主线内核（x86、ARM64），不再需要额外打补丁。

- **6.12+**: 直接在 menuconfig 中启用即可
- **6.6 LTS / 6.1 LTS**: 仍需外部补丁（官方维护中，见 [RT Wiki](https://wiki.linuxfoundation.org/realtime/preempt_rt_versions)）
- **5.x 及以下**: 需外部补丁

对于新项目，优先选择 6.12+ 主线内核，省去补丁维护的麻烦。

---

## 一、通用编译流程（x86）

### 1.1 查看当前内核版本

```bash
uname -r
```

### 1.2 下载内核与 RT 补丁

**方式 A：使用 6.12+ 主线内核（推荐，无需补丁）**

```bash
# 下载主线稳定版
git clone --depth 1 -b linux-6.12.y \
    https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
cd linux
```

**方式 B：使用旧版内核 + RT 补丁（6.6 LTS / 6.1 LTS / 5.x）**

去 [内核官网](https://mirrors.edge.kernel.org/pub/linux/kernel/) 下载内核，去 [RT 补丁官网](https://mirrors.edge.kernel.org/pub/linux/kernel/projects/rt/) 下载对应补丁。

以 6.6.x 为例：

```bash
wget https://mirrors.edge.kernel.org/pub/linux/kernel/v6.x/linux-6.6.72.tar.xz
wget https://mirrors.edge.kernel.org/pub/linux/kernel/projects/rt/6.6/older/patch-6.6.72-rt41.patch.gz

tar -xf linux-6.6.72.tar.xz
gunzip patch-6.6.72-rt41.patch.gz
cd linux-6.6.72
patch -p1 < ../patch-6.6.72-rt41.patch
```

> ⚠️ 补丁版本必须精确匹配内核版本。`patch-6.6.72-rt41` 只能用于 `linux-6.6.72`。
> 用 `patch --dry-run` 先测试是否能干净应用。

<details>
<summary>📜 旧版示例（4.14.x，仅供参考）</summary>

```bash
wget https://mirrors.edge.kernel.org/pub/linux/kernel/v4.x/linux-4.14.12.tar.gz
wget https://mirrors.edge.kernel.org/pub/linux/kernel/projects/rt/4.14/older/patch-4.14.12-rt9.patch.gz
tar -zxvf linux-4.14.12.tar.gz
gunzip patch-4.14.12-rt9.patch.gz
cd linux-4.14.12
patch -p1 < ../patch-4.14.12-rt9.patch
```

</details>

### 1.3 安装编译依赖

```bash
sudo apt-get install build-essential kernel-package fakeroot \
    libncurses5-dev libssl-dev ccache bison flex libelf-dev
```

### 1.4 配置内核

```bash
# 以当前运行内核配置为基础（推荐）
cp /boot/config-$(uname -r) .config

# 或使用发行版默认配置
# make defconfig

make menuconfig
```

**必须启用的选项：**

```
# 启用完全可抢占（PREEMPT_RT 核心）
 -> General Setup
  -> Preemption Model (Fully Preemptible Kernel (Real-Time))
   (X) Fully Preemptible Kernel (Real-Time)

# 高精度定时器
 -> General setup
  -> Timers subsystem
   [*] High Resolution Timer Support

# 无 Tick 模式（隔离核心不产生时钟中断）
 -> General setup
  -> Timers subsystem
   -> Timer tick handling (Full dynticks system (tickless))
    (X) Full dynticks system (tickless)

# 1000Hz 定时器频率
 -> Processor type and features
  -> Timer frequency (1000 HZ)
   (X) 1000 HZ

# 默认 CPU 频率策略设为 performance
 -> Power management and ACPI options
  -> CPU Frequency scaling
   -> Default CPUFreq governor
    (X) performance
```

### 1.5 编译安装

```bash
make -j$(nproc)
sudo make modules_install
sudo make install
sudo reboot
```

### 1.6 验证

```bash
uname -r          # 确认内核版本
uname -v          # 应显示 "PREEMPT RT"
```

---

## 二、平台特定指南

### 2.1 Rockchip RK3588 (ARM64)

#### 方式一：使用瑞芯微 SDK 补丁（推荐，稳定）

瑞芯微官方 SDK 内置 PREEMPT_RT 补丁，路径：
`SDK/docs/Patches/Real-Time-Performance/PREEMPT_RT/`

适用于 RK3506/RK3562/RK3568/RK3576/RK3588 全系列。

```bash
# 进入 SDK 内核源码
cd kernel

# 应用 RT 补丁
patch -p1 < ../docs/Patches/Real-Time-Performance/PREEMPT_RT/patch-5.10.xxx-rtXXX.patch

# 使用 Rockchip 默认配置为基础
make ARCH=arm64 rockchip_linux_defconfig

# 进入配置（启用与通用 x86 相同的 RT 选项）
make ARCH=arm64 menuconfig

# 交叉编译
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- -j$(nproc)
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- modules_install INSTALL_MOD_PATH=./output
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- dtbs
```

#### 方式二：使用主线内核 6.12+（需验证外设支持）

```bash
git clone --depth 1 -b linux-6.12.y \
    https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
cd linux

# 使用 Armbian 社区维护的 RK3588 配置
wget -O .config https://raw.githubusercontent.com/armbian/linux-rockchip/main/arch/arm64/configs/rockchip64_defconfig

make ARCH=arm64 menuconfig    # PREEMPT_RT 直接可选，无需补丁
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- -j$(nproc)
```

> ⚠️ 主线内核对 RK3588 的支持还在完善中（NPU、部分 GPU 特性可能缺失）。
> 如果只需要 CPU + CAN + 以太网 + GPIO，主线够用。

### 2.2 NVIDIA Jetson Thor / Orin (ARM64)

NVIDIA 提供预编译 RT 内核，**不需要自己编译**：

```bash
# JetPack 6.x 自带 RT 内核包
sudo apt install nvidia-l4t-rt-kernel \
                 nvidia-l4t-rt-kernel-headers \
                 nvidia-l4t-rt-kernel-oot-modules \
                 nvidia-l4t-display-rt-kernel \
                 nvidia-l4t-rt-kernel-openrm

sudo reboot

# 验证
uname -a    # 应显示 PREEMPT_RT
```

如需自行编译（定制配置）：

```bash
# 下载 NVIDIA 内核源码
# 参考 https://developer.nvidia.com/embedded/jetson-linux
git clone -b jetpack-6.x https://...

export CROSS_COMPILE=aarch64-buildroot-linux-gnu-
export KERNEL_OUT=build_rt
make O=$KERNEL_OUT tegra_defconfig
make O=$KERNEL_OUT menuconfig    # 启用 PREEMPT_RT
make O=$KERNEL_OUT -j$(nproc)
```

---

## 三、实时性调优（编译安装后必做！）

编译安装 RT 内核只是第一步。**不调优的 RT 内核和标准内核差距不大。**

### 3.1 内核启动参数

编辑 GRUB（x86）或 extlinux.conf（ARM）的内核启动行，添加：

```bash
# === 基本参数（必加） ===
isolcpus=managed_irq,domain,2-3    # 隔离 CPU 2-3 给实时任务
nohz_full=2-3                       # 隔离核心无 tick 中断
rcu_nocbs=2-3                       # RCU 回调不在隔离核心执行
irqaffinity=0-1                     # 硬件中断只发到非隔离核心
skew_tick=1                         # 错开 RCU 定时器，减少冲突

# === 进阶参数（追求极限延迟时加） ===
processor.max_cstate=0              # 禁用 CPU 深度睡眠（x86）
intel_idle.max_cstate=0             # 禁用 Intel idle（x86）
nosoftlockup                        # 禁用 soft lockup 检测
tsc=reliable                        # TSC 时钟可信（x86）
```

> ⚠️ **内核 6.6+ 的 `isolcpus` 语法变了**，需要 `managed_irq,domain` 前缀。
> 旧版（6.5 及以前）只写 `isolcpus=2-3` 即可。

### 3.2 用户态实时线程配置

在你的实时应用代码中：

```c
#include <sched.h>
#include <sys/mlock.h>

// 1. 锁定内存（防止缺页导致不确定延迟）
mlockall(MCL_CURRENT | MCL_FUTURE);

// 2. 设置 SCHED_FIFO 最高优先级（99 留给看门狗）
struct sched_param param = { .sched_priority = 98 };
sched_setscheduler(0, SCHED_FIFO, &param);

// 3. 绑定到隔离的 CPU 核心
cpu_set_t cpuset;
CPU_ZERO(&cpuset);
CPU_SET(2, &cpuset);
sched_setaffinity(0, sizeof(cpuset), &cpuset);
```

### 3.3 /etc/security/limits.conf

```
@realtime   -   rtprio     99
@realtime   -   memlock    unlimited
@realtime   -   nice       -20
```

```bash
sudo groupadd realtime
sudo usermod -aG realtime <your_user>
```

### 3.4 CPU 频率锁定脚本

```bash
#!/bin/bash
# fix-cpufreq.sh — 锁定所有 CPU 到最高频率
for cpu in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do
    echo performance > "$cpu"
done
echo "All CPUs set to performance governor"
cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_cur_freq
```

---

## 四、验证与基准测试

### 4.1 cyclictest（黄金标准）

```bash
# 安装
sudo apt install rt-tests

# 基本测试（10 分钟）
sudo cyclictest -a2-3 -t2 -m -p98 -i100 -h1000 -D10m

# 参数解释：
#   -a2-3    绑定到 CPU 2-3
#   -t2      2 个测试线程
#   -m       锁定内存
#   -p98     优先级 98
#   -i100    100μs 间隔
#   -h1000   直方图到 1000μs
#   -D10m    运行 10 分钟

# 加压力负载测试（更真实）
# 终端 1：
stress-ng --cpu 4 --io 2 --vm 2 --vm-bytes 256M --timeout 600s
# 终端 2：
sudo cyclictest -a2-3 -t2 -m -p98 -i100 -D10m
```

### 4.2 预期结果参考

| 平台 | 无负载 Max | 有负载 Max | 评价 |
|------|----------|----------|------|
| x86 标准内核 | 500-5000μs | 10000+μs | ❌ 不可用 |
| x86 RT 内核 (未调优) | 50-200μs | 200-1000μs | ⚠️ 凑合 |
| x86 RT 内核 (调优后) | 10-30μs | 20-80μs | ✅ 工业级 |
| RK3588 RT 内核 | 30-80μs | 50-200μs | ✅ 机器人够用 |
| Jetson Thor RT 内核 | 20-50μs | 30-100μs | ✅ 优秀 |

### 4.3 目标参考

- **1kHz 控制循环**：Max Latency < 500μs ✅（轻松达到）
- **EtherCAT 250μs 循环**：Max Latency < 100μs（需精心调优）
- **CAN-FD 1ms 循环**：Max Latency < 300μs ✅（几乎不需调优）

---

## 五、机器人场景专用内核配置

在 menuconfig 中，除了基本 RT 配置，还建议开启：

```
# CAN 子系统
-> Networking support
  -> CAN bus subsystem support
    <*> Raw CAN Protocol
    <*> Broadcast Manager CAN Protocol
    -> CAN Device Drivers
      <*> Platform CAN drivers with Netlink support
      [*]   CAN bit-timing calculation
      <*>   Rockchip CAN/CAN-FD controller     # RK3588 选这个
      <*>   Bosch M_CAN devices                 # 通用 MCAN

# EtherCAT（如果用 IgH 主站，不需要内核选项，IgH 自带内核模块）

# 高精度定时器
# 确保 CONFIG_HIGH_RES_TIMERS=y（前面已启用）

# 实时调度调试（开发阶段有用）
-> Kernel hacking
  -> Lock Debugging
    [*] RT Mutex debugging
  -> Tracers
    [*] Scheduling Latency Tracer    # ftrace 延迟追踪
```

---

## 六、网卡适配性参考

**核心原则：RK3588 优先用官方 SDK 的网卡驱动，除非发现重大 bug 才自己搞。**

### 6.1 RK3588 板载网卡（GMAC）

RK3588 内置 2 路 GMAC（Synopsys DWC Ethernet QoS），通过 RGMII 接外部 PHY。

#### 常见 PHY 芯片对比

| PHY 芯片 | 厂商 | 速率 | SDK 支持 | 主线支持 | 价格(￥) | 备注 |
|----------|------|------|---------|---------|---------|------|
| **RTL8211F** | Realtek | 1Gbps | ✅ 官方首选 | ✅ 完善 | 8-12 | 大多数 RK3588 开发板标配，稳定性最好 |
| **YT8531** | 裕太微(Motorcomm) | 1Gbps | ✅ | ✅ 6.x 合入 | 5-8 | 国产替代，性价比高，驱动已进主线 |
| **JL2101** | 景略半导体 | 100Mbps | ⚠️ 需适配 | ❌ 未合入 | 3-5 | 仅百兆，不推荐用于 EtherCAT |
| **RTL8211E** | Realtek | 1Gbps | ✅ | ✅ | 6-10 | 老型号，RTL8211F 的前代 |
| **RTL8125BG** | Realtek | 2.5Gbps | ✅ PCIe | ✅ | 15-25 | PCIe 接口，非 GMAC，ROCK 5B 等用这个 |

#### 官方 SDK vs 主线驱动差异

**强烈建议用官方 SDK 驱动，原因：**

1. **RGMII 延迟线校准**：RK3588 的 GMAC TX/RX 时钟延迟需要精细调整（`tx_delay` / `rx_delay`），SDK 的 `dwmac-rk` 驱动针对不同 PHY 有验证过的默认值
2. **时钟配置**：SDK 驱动正确处理 `mac_clk_rx`、`mac_clk_tx`、`clk_mac_speed` 等时钟，主线 6.1 以前可能缺少部分时钟配置（已知 OpenWrt 6.1 上 RTL8211F TX 有问题）
3. **PHY 复位时序**：不同 PHY 复位延迟不同（RTL8211F 需要 100ms），SDK 默认值已验证

**什么时候才需要自己搞：**
- SDK 驱动有已知重大 bug 且官方没修
- 需要主线不支持的 PHY（如 JL2101）
- 从 SDK 5.10 升级到主线 6.12+ 后网口不通

#### 设备树 RGMII 延迟配置（关键！）

```dts
/* RTL8211F 推荐配置（SDK 默认） */
&gmac0 {
    phy-mode = "rgmii-rxid";   /* RX 延迟由 PHY 内部产生 */
    clock_in_out = "output";
    snps,reset-gpio = <&gpio3 RK_PC7 GPIO_ACTIVE_LOW>;
    snps,reset-active-low;
    snps,reset-delays-us = <0 20000 100000>;  /* RTL8211F: 100ms 复位 */
    tx_delay = <0x45>;         /* SDK 验证值，不要随便改 */
    /* rx_delay 不设，因为用了 rgmii-rxid 模式 */
    phy-handle = <&rgmii_phy0>;
    status = "okay";
};

/* YT8531 推荐配置 */
&gmac1 {
    phy-mode = "rgmii-id";     /* TX/RX 延迟都由 PHY 产生 */
    clock_in_out = "output";
    snps,reset-gpio = <&gpio3 RK_PB7 GPIO_ACTIVE_LOW>;
    snps,reset-active-low;
    snps,reset-delays-us = <0 20000 100000>;
    tx_delay = <0x42>;
    rx_delay = <0x4f>;
    phy-handle = <&rgmii_phy1>;
    status = "okay";
};
```

> ⚠️ `tx_delay` 和 `rx_delay` 的值因板子走线而异。SDK 里的值是官方 EVB 验证过的，
> 如果自己做的板子布线不同，可能需要用瑞芯微的 RGMII Delayline 校准工具重新调。

### 6.2 EtherCAT 主站网卡选择

EtherCAT 主站需要能绕过 Linux 网络栈直接操作网卡的能力。不是所有网卡都支持。

#### 各主站方案的网卡兼容性

| 网卡/驱动 | IgH 原生驱动 | SOEM (Raw Socket) | acontis (atemsys) |
|----------|-------------|-------------------|-------------------|
| **Intel I210** (igb) | ✅ 最佳 | ✅ | ✅ |
| **Intel I225/I226** (igc) | ✅ 社区补丁 | ✅ | ✅ |
| **Intel 82574L** (e1000e) | ✅ | ✅ | ✅ |
| **Realtek RTL8111** (r8169) | ✅ 社区补丁 | ✅ | ⚠️ 需适配 |
| **Realtek RTL8169** (r8169) | ✅ 旧版原生 | ✅ | ⚠️ |
| **RK3588 GMAC** (stmmac) | ⚠️ 需移植 | ✅ | ✅ Intel ECI 有验证 |
| **通用网卡** (generic) | ✅ 性能差 | ✅ | — |

#### 推荐搭配

**RK3588 做 EtherCAT 主站时：**
- **首选**：板载 GMAC + SOEM（用户态 Raw Socket，开发快）
- **次选**：PCIe 转 Intel I210 网卡 + IgH Master（内核态，实时性好）
- **不建议**：USB 网卡（延迟不确定，抖动大）

**Jetson Thor/Orin 做 EtherCAT 主站时：**
- **首选**：板载 MGBE/GMAC + acontis EC-Master（官方适配）
- **次选**：PCIe Intel I210 + IgH Master
- Intel ECI SDK 已验证 stmmac + igb + igc 三种驱动

#### IgH EtherCAT Master 已知支持的原生驱动

截至 2026 年，社区维护的 IgH 已支持（含第三方补丁）：
- **igb** (Intel I210/I350/82575/82576) — 最成熟，**首选**
- **igc** (Intel I225/I226) — 6.5+ 内核社区有补丁
- **e1000e** (Intel 82574L/82573) — 经典稳定
- **r8169** (Realtek RTL8111/8168/8169) — 便宜够用，有 6.5/6.13 补丁
- **generic** — 通用驱动，任何网卡都能跑，但性能最差

GitHub 参考（含 6.13 内核支持）：https://github.com/allzergdead/IGH-ethercat-master

> 💡 **结论：做 EtherCAT 的话，外挂一块 Intel I210 PCIe 小卡（~￥50）是最稳的路线。**
> RK3588 板载 GMAC 跑 EtherCAT 理论可行但需要自己移植 IgH 的 stmmac 驱动，不如花 50 块买个 I210 省心。

### 6.3 CAN-FD 场景

CAN-FD 走的是 RK3588 内置 CAN 控制器 + 外部收发器（TJA1443 等），和以太网网卡完全无关。不需要操心网卡兼容性。唯一要确认的是 CAN 收发器芯片支持 CAN-FD 高速数据段（5-8 Mbps）。

---

## 七、常见问题

### Q: 编译报错 `error: implicit declaration of function 'xxx'`

RT 补丁版本和内核版本不完全匹配。检查补丁文件名里的版本号是否和内核版本精确对应。例如 `patch-5.10.110-rt53` 只能用于 `linux-5.10.110`。

### Q: cyclictest Max Latency 偶尔飙到几毫秒

常见原因：
1. **没有隔离 CPU**：加 `isolcpus` 启动参数
2. **CPU 降频**：锁定 performance governor
3. **SMI 中断**（x86）：BIOS 中禁用 SMM 或使用 `hwlatdetect` 检查
4. **磁盘 I/O 抢占**：确保实时核心没有跑 I/O 任务

### Q: RK3588 的 CAN 驱动在 RT 内核下不稳定

Rockchip 官方 SDK 的 CAN 驱动比主线更稳定。建议用 SDK 内核 + RT 补丁，而非主线内核。

### Q: 打了补丁后无法启动

常见于版本不匹配：
1. 检查 `dmesg` 日志（串口或 recovery 模式）
2. 用 `patch --dry-run` 先测试补丁是否干净应用
3. 确保 `.config` 中没有冲突选项

### Q: RK3588 网口不通（TX 发不出去）

多发于主线内核 6.1 及以前版本 + RTL8211F PHY 组合：
1. 确认 `phy-mode` 和 `tx_delay` / `rx_delay` 设置正确
2. 优先用 SDK 内核的 `dwmac-rk` 驱动
3. 检查 PHY 复位 GPIO 和时序配置
