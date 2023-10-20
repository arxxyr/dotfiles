## 编译rt内核

查看内核版本
```
uname -r
```
去[官网](https://mirrors.edge.kernel.org/pub/linux/kernel/)下载对应的内核，例如4.14.12

```
wget https://mirrors.edge.kernel.org/pub/linux/kernel/v4.x/linux-4.14.12.tar.gz
```
去[官网](https://mirrors.edge.kernel.org/pub/linux/kernel/projects/rt/)下载对应的内核补丁，例如4.14.12-rt9

```
wget https://mirrors.edge.kernel.org/pub/linux/kernel/projects/rt/4.14/older/patch-4.14.12-rt9.patch.gz
```
解压内核
```
tar -zxvf linux-4.14.12.tar.gz
```
解压内核补丁
```
gunzip patch-4.14.12-rt9.patch.gz
```
进入内核目录
```
cd linux-4.14.12
```
打补丁
```
patch -p1 < ../patch-4.14.12-rt9.patch
```
安装依赖
```
sudo apt-get install build-essential kernel-package fakeroot libncurses5-dev libssl-dev ccache bison flex libelf-dev
```
配置内核
```
cp /boot/config-4.14.12-generic .config
```
```
make menuconfig
```
选择
```
# Enable CONFIG_PREEMPT_RT
 -> General Setup
  -> Preemption Model (Fully Preemptible Kernel (Real-Time))
   (X) Fully Preemptible Kernel (Real-Time)

# Enable CONFIG_HIGH_RES_TIMERS
 -> General setup
  -> Timers subsystem
   [*] High Resolution Timer Support

# Enable CONFIG_NO_HZ_FULL
 -> General setup
  -> Timers subsystem
   -> Timer tick handling (Full dynticks system (tickless))
    (X) Full dynticks system (tickless)

# Set CONFIG_HZ_1000 (note: this is no longer in the General Setup menu, go back twice)
 -> Processor type and features
  -> Timer frequency (1000 HZ)
   (X) 1000 HZ

# Set CPU_FREQ_DEFAULT_GOV_PERFORMANCE [=y]
 ->  Power management and ACPI options
  -> CPU Frequency scaling
   -> CPU Frequency scaling (CPU_FREQ [=y])
    -> Default CPUFreq governor (<choice> [=y])
     (X) performance
```
保存退出

编译安装
```
make -j `nproc`
```
```
sudo make modules_install
```
```
sudo make install
```
重启
```
sudo reboot
```
查看内核版本
```
uname -r
```
查看内核是否为rt内核
```
uname -v
```
如果显示PREEMPT RT，说明内核已经安装成功
