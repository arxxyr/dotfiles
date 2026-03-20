# ~/.claude/statusline-command.ps1
# 基于 oh-my-zsh robbyrussell 主题风格的 Claude Code 状态栏（Windows PowerShell 版）
# robbyrussell: ➜  <basename> git:(branch) ✗

# 从 stdin 读取 Claude Code 传入的 JSON
$raw_input = [Console]::In.ReadToEnd()
$json = $raw_input | ConvertFrom-Json

# --- 目录信息 ---
$cwd = if ($json.cwd) { $json.cwd } elseif ($json.workspace.current_dir) { $json.workspace.current_dir } else { "" }
$dir_name = if ($cwd) { Split-Path -Leaf $cwd } else { "" }

# --- Git 信息 ---
$git_branch = ""
$git_dirty = $false
if ($cwd -and (Test-Path $cwd)) {
    try {
        $null = git -C $cwd rev-parse --is-inside-work-tree --no-optional-locks 2>$null
        if ($LASTEXITCODE -eq 0) {
            $git_branch = git -C $cwd symbolic-ref --short HEAD --no-optional-locks 2>$null
            if ($LASTEXITCODE -ne 0) {
                $git_branch = git -C $cwd rev-parse --short HEAD --no-optional-locks 2>$null
            }
            # 检查 unstaged 变更
            $null = git -C $cwd diff --quiet --no-optional-locks 2>$null
            if ($LASTEXITCODE -ne 0) {
                $git_dirty = $true
            }
            # 检查 staged 变更
            $null = git -C $cwd diff --cached --quiet --no-optional-locks 2>$null
            if ($LASTEXITCODE -ne 0) {
                $git_dirty = $true
            }
        }
    } catch {
        # git 不可用，静默跳过
    }
}

# --- Claude 会话信息 ---
$model = if ($json.model.display_name) { $json.model.display_name } else { "" }
$used_pct = if ($null -ne $json.context_window.used_percentage) { $json.context_window.used_percentage } else { $null }

# --- 组装输出（ANSI 转义序列）---
$ESC = [char]0x1B
$RESET = "$ESC[0m"
$BOLD = "$ESC[1m"
$RED = "$ESC[31m"
$GREEN = "$ESC[32m"
$YELLOW = "$ESC[33m"
$BLUE = "$ESC[34m"
$CYAN = "$ESC[36m"

# 箭头：有上下文用量时根据用量着色（>80% 红，>50% 黄，否则绿）
$arrow_color = $GREEN
if ($null -ne $used_pct) {
    $pct_int = [math]::Round([double]$used_pct)
    if ($pct_int -ge 80) {
        $arrow_color = $RED
    } elseif ($pct_int -ge 50) {
        $arrow_color = $YELLOW
    }
}

# 构建各段
$part_arrow = "${BOLD}${arrow_color}→${RESET}"
$part_dir = "  ${BOLD}${CYAN}${dir_name}${RESET}"

$part_git = ""
if ($git_branch) {
    if ($git_dirty) {
        $part_git = "  ${BOLD}${BLUE}git:(${RESET}${RED}${git_branch}${BOLD}${BLUE})${RESET} ${YELLOW}*${RESET}"
    } else {
        $part_git = "  ${BOLD}${BLUE}git:(${RESET}${RED}${git_branch}${BOLD}${BLUE})${RESET}"
    }
}

$part_model = ""
if ($model) {
    $part_model = "  ${BLUE}${model}${RESET}"
}

$part_ctx = ""
if ($null -ne $used_pct) {
    $pct_int = [math]::Round([double]$used_pct)
    $part_ctx = "  ctx:${arrow_color}${pct_int}%${RESET}"
}

Write-Host "${part_arrow}${part_dir}${part_git}${part_model}${part_ctx}"
