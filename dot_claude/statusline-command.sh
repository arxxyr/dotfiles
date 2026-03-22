#!/usr/bin/env bash
# 基于 oh-my-zsh robbyrussell 主题风格的 Claude Code 状态栏
# robbyrussell: ➜  <basename> git:(branch) ✗

input=$(cat)

# --- 简易 JSON 提取（无需 jq）---
# 提取字符串值: "key": "value"
json_str() {
    echo "$input" | grep -o "\"$1\"[[:space:]]*:[[:space:]]*\"[^\"]*\"" | head -1 | sed 's/.*:[[:space:]]*"\(.*\)"/\1/'
}
# 提取数字值: "key": 123.45
json_num() {
    echo "$input" | grep -o "\"$1\"[[:space:]]*:[[:space:]]*[0-9.]*" | head -1 | sed 's/.*:[[:space:]]*//'
}

# --- 目录信息 ---
cwd=$(json_str 'cwd')
dir_name=$(basename "$cwd" 2>/dev/null)

# --- Git 信息 ---
git_branch=""
git_dirty=""
if [ -n "$cwd" ] && git --no-optional-locks -C "$cwd" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    git_branch=$(git --no-optional-locks -C "$cwd" symbolic-ref --short HEAD 2>/dev/null)
    git_hash=$(git --no-optional-locks -C "$cwd" rev-parse --short HEAD 2>/dev/null)
    # detached HEAD 时 symbolic-ref 为空，直接用 hash
    [ -z "$git_branch" ] && git_branch="$git_hash"
    if ! git --no-optional-locks -C "$cwd" diff --quiet 2>/dev/null || \
       ! git --no-optional-locks -C "$cwd" diff --cached --quiet 2>/dev/null; then
        git_dirty="1"
    fi
fi

# --- Python 环境检测 ---
py_env=""
if [ -n "$cwd" ]; then
    if [ -f "$cwd/uv.lock" ] || [ -f "$cwd/pyproject.toml" ] && command -v uv >/dev/null 2>&1; then
        # 检测 uv 项目：优先用 uv 获取 python 版本
        py_ver=$(cd "$cwd" && uv run python --version 2>/dev/null | grep -o '[0-9]\+\.[0-9]\+\.[0-9]\+')
        [ -n "$py_ver" ] && py_env="uv:${py_ver}"
    fi
    if [ -z "$py_env" ] && [ -n "$VIRTUAL_ENV" ]; then
        # 通用 venv（可能由 uv venv 创建）
        py_ver=$(python3 --version 2>/dev/null | grep -o '[0-9]\+\.[0-9]\+\.[0-9]\+')
        if [ -f "$VIRTUAL_ENV/pyvenv.cfg" ] && grep -q 'uv' "$VIRTUAL_ENV/pyvenv.cfg" 2>/dev/null; then
            [ -n "$py_ver" ] && py_env="uv:${py_ver}"
        else
            [ -n "$py_ver" ] && py_env="venv:${py_ver}"
        fi
    fi
    if [ -z "$py_env" ] && [ -n "$CONDA_DEFAULT_ENV" ]; then
        py_ver=$(python3 --version 2>/dev/null | grep -o '[0-9]\+\.[0-9]\+\.[0-9]\+')
        py_env="conda:${CONDA_DEFAULT_ENV}"
        [ -n "$py_ver" ] && py_env="conda:${CONDA_DEFAULT_ENV}:${py_ver}"
    fi
fi

# --- Claude 会话信息 ---
model=$(json_str 'display_name')
used_pct=$(json_num 'used_percentage')

# --- 颜色定义 ---
RESET='\033[0m'
BOLD='\033[1m'
RED='\033[31m'
GREEN='\033[32m'
YELLOW='\033[33m'
BLUE='\033[34m'
CYAN='\033[36m'

# 箭头颜色：>80% 红，>50% 黄，否则绿
arrow_color="$GREEN"
if [ -n "$used_pct" ]; then
    pct_int=$(printf '%.0f' "$used_pct" 2>/dev/null)
    if [ "${pct_int:-0}" -ge 80 ] 2>/dev/null; then
        arrow_color="$RED"
    elif [ "${pct_int:-0}" -ge 50 ] 2>/dev/null; then
        arrow_color="$YELLOW"
    fi
fi

# --- 构建各段 ---
part_arrow=$(printf "${BOLD}${arrow_color}➜${RESET}")
part_dir=$(printf "  ${BOLD}${CYAN}%s${RESET}" "$dir_name")

part_git=""
if [ -n "$git_branch" ]; then
    branch_label="${git_branch}"
    # 只有在有分支名（非 detached）时才追加 hash
    [ -n "$git_hash" ] && [ "$git_branch" != "$git_hash" ] && branch_label="${git_branch}@${git_hash}"
    if [ -n "$git_dirty" ]; then
        part_git=$(printf "  ${BOLD}${BLUE}git:(${RESET}${RED}%s${BOLD}${BLUE})${RESET} ${YELLOW}✗${RESET}" "$branch_label")
    else
        part_git=$(printf "  ${BOLD}${BLUE}git:(${RESET}${RED}%s${BOLD}${BLUE})${RESET}" "$branch_label")
    fi
fi

part_py=""
if [ -n "$py_env" ]; then
    part_py=$(printf "  ${YELLOW}🐍 %s${RESET}" "$py_env")
fi

part_model=""
if [ -n "$model" ]; then
    part_model=$(printf "  ${BLUE}%s${RESET}" "$model")
fi

part_ctx=""
if [ -n "$used_pct" ]; then
    pct_int=$(printf '%.0f' "$used_pct" 2>/dev/null)
    part_ctx=$(printf "  ctx:%s%d%%%s" "$arrow_color" "${pct_int:-0}" "$RESET")
fi

printf "%b%b%b%b%b%b\n" \
    "$part_arrow" \
    "$part_dir" \
    "$part_git" \
    "$part_py" \
    "$part_model" \
    "$part_ctx"
