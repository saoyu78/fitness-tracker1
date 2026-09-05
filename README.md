# 健身记录应用 - Fitness Tracker

这是一个使用 Python + Kivy 开发的健身记录应用，可以打包成 APK 在 Android 手机上使用。

## 功能特性

### 1. 日历视图系统
- **周视图**：默认首页，显示本周一到周日
- **月视图**：显示整月日历，网格布局
- **年视图**：显示全年12个月的概览
- 支持前后导航切换周/月/年
- 首次使用需要设置起始年份
- 日历上标记训练日（绿色✓）和休息日（橙色"休"）
- 当天日期用蓝色高亮显示

### 2. 训练记录功能
- 点击日期进入记录页面
- 自动显示完整日期和星期
- 选择"训练日"或"休息日"
- **训练日功能**：
  - 添加多个动作分组
  - 预设动作：全蹲、高翻、引体、划船、卧推
  - 支持自定义动作名称
  - 每个动作可添加多组训练
  - 记录每组的重量（kg）和次数
  - 自动计算：总组数、总次数、总重量、最大重量
  - 每个动作可添加备注
- **休息日功能**：
  - 添加简单的文字备注

### 3. 进步对比功能
- 自动对比该动作上一次训练的最大重量
- 对比总重量（所有组的重量×次数之和）
- 显示进步差值（例如：+5kg、-2kg）
- 实时显示"上次"和"本次"的对比

### 4. 图表展示
- 在记录页面底部显示趋势图表
- 显示最近10次该动作的训练记录
- 绿色折线：最大重量变化趋势
- 蓝色折线：总重量变化趋势
- 直观展示训练进步情况

### 5. 数据持久化
- 使用本地 JSON 文件保存所有数据
- 数据存储在应用目录的 `fitness_data.json` 文件中
- 关闭应用后数据不会丢失
- 支持跨会话访问历史记录

### 6. UI设计
- 现代化简洁界面
- 绿色主题：训练日
- 橙色主题：休息日
- 蓝色主题：当天日期
- 响应式布局，适配手机屏幕
- 完整中文界面

## 安装使用

### 方法一：在电脑上运行测试

1. **安装 Python 3.8+**
   ```bash
   # 检查 Python 版本
   python --version
   ```

2. **安装依赖**
   ```bash
   cd fitness_tracker
   pip install -r requirements.txt
   ```

3. **运行应用**
   ```bash
   python main.py
   ```

### 方法二：打包成 Android APK

由于 Buildozer 工具只支持 Linux 环境，最推荐且最方便的方式是使用 **GitHub Actions 云端自动打包**（无需在电脑上配置 Linux、WSL 或下载庞大的 SDK/NDK）。

#### 🚀 推荐：使用 GitHub Actions 云端自动打包（免费、全自动）

1. **登录并创建 GitHub 仓库**：
   - 访问 [GitHub](https://github.com/)，点击右上角 **+** -> **New repository**。
   - 仓库名称填写 `fitness-tracker`，**必须选择 Public（公开）**。
   - 点击 **Create repository**。

2. **上传项目文件**：
   - 在仓库页面点击 **Add file** -> **Upload files**。
   - 将本项目目录中的所有文件直接拖拽上传（必须包含 `.github/`、`main.py`、`buildozer.spec`、`requirements.txt`）。
   - 点击 **Commit changes**。

3. **等待自动打包**：
   - 提交后，点击顶部的 **Actions** 标签页。
   - GitHub 服务器会自动启动 Ubuntu 环境下载依赖并编译，耗时约 15~25 分钟。

4. **下载 APK**：
   - 构建完成后（绿勾），点击该工作流运行记录。
   - 页面底部 **Artifacts** 区域会生成 **fitness-tracker-apk**，点击下载解压即可得到 APK。

---

#### 选项 B：使用本地 WSL2（如果你有 Linux / WSL 环境）
1. 在 Ubuntu/WSL 中安装依赖：
   ```bash
   sudo apt update
   sudo apt install -y python3-pip build-essential git python3 python3-dev \
       ffmpeg libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev \
       libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev zlib1g-dev \
       openjdk-17-jdk fonts-wqy-microhei
   pip install buildozer "cython<3.0"
   ```
2. 运行打包：
   ```bash
   buildozer android debug
   ```
3. 生成的 APK 位于 `bin/` 目录下。

## 安装到手机

1. 将生成的 APK 文件传输到手机
2. 在手机上开启"允许安装未知来源应用"
3. 点击 APK 文件安装
4. 首次打开输入起始年份
5. 开始记录你的健身训练！

## 使用技巧

1. **快速导航**：在周视图中最方便查看和记录
2. **数据对比**：记录时会自动显示与上次训练的对比
3. **趋势分析**：查看图表了解长期进步情况
4. **自定义动作**：在动作选择中选择"自定义..."输入任何动作名称
5. **备份数据**：定期备份 `fitness_data.json` 文件

## 常见问题

### Q1: 打包时间很长？
A: 首次打包需要下载 Android SDK、NDK 等工具，可能需要 30-60 分钟，之后打包会快很多。

### Q2: 打包失败？
A: 确保：
- 使用 Linux 环境（不是 Windows）
- Python 版本 3.8+
- 有足够磁盘空间（至少 5GB）
- 网络连接稳定

### Q3: 应用闪退？
A: 检查 Android 版本是否 ≥ 5.0（API 21+）

### Q4: 数据会丢失吗？
A: 不会，所有数据保存在本地 JSON 文件中，除非卸载应用或清除数据。

## 数据格式

数据存储在 `fitness_data.json` 中，格式如下：

```json
{
  "start_year": 2026,
  "records": {
    "2026-09-03": {
      "type": "training",
      "groups": [
        {
          "exercise": "全蹲",
          "sets": [
            {"weight": 100, "reps": 5},
            {"weight": 100, "reps": 5}
          ],
          "note": "感觉不错"
        }
      ]
    },
    "2026-09-04": {
      "type": "rest",
      "note": "恢复日"
    }
  }
}
```

## 开发说明

- **开发框架**：Kivy 2.3.0
- **编程语言**：Python 3.8+
- **打包工具**：Buildozer
- **支持平台**：Android 5.0+（API 21+）
- **应用大小**：约 15-20 MB

## 许可证

本项目仅供个人学习使用。

## 技术支持

如有问题，请检查：
1. Python 和 Kivy 是否正确安装
2. 终端中的错误信息
3. Kivy 官方文档：https://kivy.org/doc/stable/

---

祝你训练进步！💪
