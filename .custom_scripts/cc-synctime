#!/usr/bin/env bash
set -euo pipefail

log() { printf "[%s] %s\n" "$(date '+%F %T')" "$*"; }

# 1) 设置时区 UTC+8
log "set timezone: Asia/Shanghai"
sudo timedatectl set-timezone Asia/Shanghai

# 2) 安装 chrony（持续同步）+ ntpdate（单次同步兜底）
log "apt update"
sudo apt-get update -y

log "install chrony + ntpdate"
sudo apt-get install -y chrony
sudo apt-get install -y ntpdate || sudo apt-get install -y ntpsec-ntpdate

# 3) 配置 chrony NTP 源
log "write /etc/chrony/chrony.conf"
sudo tee /etc/chrony/chrony.conf >/dev/null <<'EOF'
# Minimal chrony config
driftfile /var/lib/chrony/chrony.drift

# NTP servers (fallback list)
server time.cloudflare.com iburst
server ntp.aliyun.com iburst
server ntp.tencent.com iburst
server pool.ntp.org iburst

# Step the clock in the first 3 updates if offset is large
makestep 1.0 3

# Sync system time to RTC periodically (if RTC exists)
rtcsync

# Logs (optional)
log tracking measurements statistics
logdir /var/log/chrony
EOF

log "enable + restart chrony"
sudo systemctl enable --now chrony
sudo systemctl restart chrony

# 4) 避免两个服务抢时间：停掉 timesyncd（有就停）
log "stop systemd-timesyncd (if exists)"
sudo systemctl stop systemd-timesyncd 2>/dev/null || true
sudo systemctl disable systemd-timesyncd 2>/dev/null || true

# 5) 立刻对时：优先 chrony，失败再 ntpdate 兜底
log "sync time now"
if ! sudo chronyc -a makestep >/dev/null 2>&1; then
  sudo ntpdate -u time.cloudflare.com || \
  sudo ntpdate -u ntp.aliyun.com || \
  sudo ntpdate -u ntp.tencent.com || \
  sudo ntpdate -u pool.ntp.org
fi

# 6) 写入硬件时钟：自动识别容器；容器直接跳过
virt="$(systemd-detect-virt -c 2>/dev/null || true)"
if [[ "$virt" == "none" || -z "$virt" ]]; then
  log "non-container detected, try hwclock --systohc"
  if ! command -v hwclock >/dev/null 2>&1; then
    log "install util-linux for hwclock"
    sudo apt-get install -y util-linux
  fi
  sudo hwclock --systohc || true
else
  log "container detected ($virt), skip hwclock"
fi

# 7) 输出状态确认
log "timedatectl"
timedatectl

log "chrony tracking"
chronyc tracking || true

log "chrony sources"
chronyc sources -v || true

log "done"
