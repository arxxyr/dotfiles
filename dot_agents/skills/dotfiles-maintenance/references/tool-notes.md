# 工具备忘

## Draw.io：macOS 导出 PNG

旧配置记录的桌面安装路径与两倍缩放导出命令：

```bash
/Applications/draw.io.app/Contents/MacOS/draw.io -x -f png -s 2 input.drawio
```

- 默认样式：`rounded=1`、`spacing=15`、边路由 `orthogonal`。
- 路径只适用于对应 macOS 安装；执行前核对当前可执行文件和输入文件，不复制到其他平台使用。
- 不覆盖已有导出文件，除非用户任务已包含该输出更新。
