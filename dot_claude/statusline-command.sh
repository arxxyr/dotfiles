#!/usr/bin/env bash
# ~/.claude/statusline-command.sh
# 基于 oh-my-zsh robbyrussell 主题风格的 Claude Code 状态栏
# robbyrussell: ➜  <basename> git:(branch) ✗

input=$(cat)

# --- 目录信息 ---
cwd=$(echo "$input" | jq -r '.cwd // .workspace.current_dir // ""')
dir_name=$(basename "$cwd")

# --- Git 信息（跳过可选锁，失败静默）---
git_branch=""
git_dirty=""
if git -C "$cwd" rev-parse --is-inside-work-tree --no-optional-locks >/dev/null 2>&1; then
    git_branch=$(git -C "$cwd" symbolic-ref --short HEAD --no-optional-locks 2>/dev/null \
                 || git -C "$cwd" rev-parse --short HEAD --no-optional-locks 2>/dev/null)
    if ! git -C "$cwd" diff --quiet --no-optional-locks 2>/dev/null || \
       ! git -C "$cwd" diff --cached --quiet --no-optional-locks 2>/dev/null; then
        git_dirty="1"
    fi
fi

# --- Claude 会话信息 ---
model=$(echo "$input" | jq -r '.model.display_name // ""')
used_pct=$(echo "$input" | jq -r '.context_window.used_percentage // empty')

# --- 组装输出 ---
# 颜色定义（ANSI）
RESET='\033[0m'
BOLD='\033[1m'
RED='\033[31m'
GREEN='\033[32m'
YELLOW='\033[33m'
BLUE='\033[34m'
CYAN='\033[36m'

# 箭头：有上下文用量时根据用量着色（>80% 红，>50% 黄，否则绿）
arrow_color="$GREEN"
if [ -n "$used_pct" ]; then
    pct_int=$(printf '%.0f' "$used_pct")
    if [ "$pct_int" -ge 80 ]; then
        arrow_color="$RED"
    elif [ "$pct_int" -ge 50 ]; then
        arrow_color="$YELLOW"
    fi
fi

# 构建各段
part_arrow=$(printf "${BOLD}${arrow_color}➜${RESET}")
part_dir=$(printf "  ${BOLD}${CYAN}%s${RESET}" "$dir_name")

part_git=""
if [ -n "$git_branch" ]; then
    if [ -n "$git_dirty" ]; then
        part_git=$(printf "  ${BOLD}${BLUE}git:(${RESET}${RED}%s${BOLD}${BLUE})${RESET} ${YELLOW}✗${RESET}" "$git_branch")
    else
        part_git=$(printf "  ${BOLD}${BLUE}git:(${RESET}${RED}%s${BOLD}${BLUE})${RESET}" "$git_branch")
    fi
fi

part_model=""
if [ -n "$model" ]; then
    part_model=$(printf "  ${BLUE}%s${RESET}" "$model")
fi

part_ctx=""
if [ -n "$used_pct" ]; then
    pct_int=$(printf '%.0f' "$used_pct")
    part_ctx=$(printf "  ctx:%s%d%%%s" "$arrow_color" "$pct_int" "$RESET")
fi

printf "%b%b%b%b%b\n" \
    "$part_arrow" \
    "$part_dir" \
    "$part_git" \
    "$part_model" \
    "$part_ctx"
