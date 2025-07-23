-- Pull in the wezterm API
local wezterm = require("wezterm")

-- This will hold the configuration.
local config = wezterm.config_builder()

-- Set color scheme
config.color_scheme = "Apple System Colors"

-- Set font and font size
config.font = wezterm.font("JetBrainsMono NF")
config.font_size = 12.0 -- 设置字体大小

-- Set default window size (columns and rows)
config.initial_cols = 140 -- 设置初始列数
config.initial_rows = 30 -- 设置初始行数

config.enable_wayland = false

-- and finally, return the configuration to wezterm
return config
