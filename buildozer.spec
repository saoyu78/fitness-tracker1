[app]

# 应用标题
title = 健身记录

# 包名（Android需要）
package.name = fitnesstracker

# 包域名
package.domain = org.fitness

# 源代码目录
source.dir = .

# 源文件（主文件）
source.include_exts = py,png,jpg,kv,atlas,json,ttf,ttc

# 应用版本
version = 1.0

# 应用需要的权限
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# 支持的Android架构
android.archs = arm64-v8a

# Python依赖
requirements = python3==3.11.9,kivy

# 应用图标（可选，需要自己准备图标文件）
# icon.filename = %(source.dir)s/data/icon.png

# 启动画面（可选）
# presplash.filename = %(source.dir)s/data/presplash.png

# Android API级别
android.api = 31

# 最小Android API级别
android.minapi = 21

# Android NDK版本
android.ndk = 25b

# Android SDK版本
android.sdk = 31

# 是否接受Android SDK许可证
android.accept_sdk_license = True

# 方向支持
orientation = portrait

# 全屏显示
fullscreen = 0

# 日志等级
log_level = 2

# 警告等级
warn_on_root = 1

[buildozer]

# 日志等级
log_level = 2

# 警告在安装依赖时显示
warn_on_root = 1
