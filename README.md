# PicarroAveCalc（均值数据统计工具）

🎯 一个基于 PyQt5 的桌面应用程序，支持对 CSV/XLSX 等格式的数据按时间进行分组均值统计，并导出为 Excel 文件。

![screenshot](https://user-images.githubusercontent.com/yourusername/screenshot.png) <!-- 可选加截图 -->

---

## 🧩 功能介绍

- 支持批量读取 `.csv`, `.dat`, `.xlsx`, `.xls` 文件（文件夹或单文件）
- 自动识别时间列和数值列
- 提供 30、60、300、3600 秒等可选时间间隔的均值统计
- 生成结果表格并导出为 `.xlsx` 文件
- 内嵌表格预览功能（预览前20行）

---

## 💻 下载可执行程序（Windows）

点击下方链接，下载 `.exe` 文件，双击运行即可（无需安装）：

👉 [点击前往 Release 页面下载 `.exe`](https://github.com/Simonwang5529/PicarroAveCalc/releases/latest)

---

## 🚀 本地运行（开发者）

### 1. 安装依赖
确保你已安装 Python 3.8+，然后：

```bash
pip install -r requirements.txt
