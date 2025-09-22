#!/usr/bin/env bash
# 文件名：apt_proxy_upgrade.sh
# 功能：通过 proxychains 走代理执行
#   sudo proxychains apt update &&
#   sudo proxychains apt full-upgrade -y &&
#   sudo apt autoremove --purge -y
# 备注：默认临时强制 APT 走 IPv4，避免部分环境 IPv6 失败

set -euo pipefail

#======== 配置 ========#
force_ipv4="${FORCE_IPV4:-1}"     # 1=开启临时IPv4, 0=关闭
proxychains_bin="${PROXYCHAINS_BIN:-proxychains}"  # 可改为 proxychains4 等
apt_bin="${APT_BIN:-apt}"
#=====================#

need_cmd() { command -v "$1" >/dev/null 2>&1 || { echo "缺少命令：$1" >&2; exit 127; }; }

need_cmd sudo
need_cmd "$proxychains_bin"
need_cmd "$apt_bin"

tmp_conf=""
cleanup() {
  # 恢复 APT 配置
  if [[ -n "${tmp_conf:-}" && -f "$tmp_conf" ]]; then
    sudo rm -f "$tmp_conf" || true
  fi
}
trap cleanup EXIT

# 临时强制 APT 使用 IPv4（避免 IPv6 失败）
if [[ "$force_ipv4" == "1" ]]; then
  tmp_conf="/etc/apt/apt.conf.d/99-force-ipv4-tmp-$(date +%s)"
  echo 'Acquire::ForceIPv4 "true";' | sudo tee "$tmp_conf" >/dev/null
fi

# 更新索引
sudo "$proxychains_bin" "$apt_bin" update

# 全量升级
sudo "$proxychains_bin" "$apt_bin" full-upgrade -y

# 清理无用包
sudo "$apt_bin" autoremove --purge -y



