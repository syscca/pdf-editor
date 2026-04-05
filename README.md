# PDF 编辑器 (Windows 11)

这是一个基于 Python、PyQt6 和 PyMuPDF 开发的轻量级 PDF 编辑器，专为 Windows 11 环境优化，支持全中文界面。它提供了一些核心的 PDF 页面管理功能，如删除、添加、打印和打印预览。

## 🌟 主要功能

- **PDF 页面预览**：以缩略图形式清晰展示 PDF 的每一页。
- **页面管理**：
  - **删除页面**：支持单选或多选页面并进行批量删除。
  - **添加页面**：支持从另一个 PDF 文件中追加页面到当前文档。
- **打印与预览**：
  - **打印预览**：在正式打印前查看页面排版效果。
  - **打印选定页**：支持将选中的页面发送到本地打印机或“Microsoft Print to PDF”。
- **文件保存**：支持将修改后的 PDF 文件保存或另存为新文件。

## 📋 环境要求

在开始之前，请确保您的系统中已安装以下环境：

- **操作系统**：Windows 10 或 Windows 11 (推荐)
- **Python**：Python 3.8 或更高版本
- **依赖库**：PyQt6, PyMuPDF (fitz)

## 🚀 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/syscca/pdf-editor.git
cd pdf-editor
```

### 2. 安装依赖

```powershell
pip install -r requirements.txt
```

### 4. 运行程序

```powershell
python pdf_editor.py
```

## 📄 开源协议

本项目采用 [MIT](LICENSE) 协议。

---

如果有任何问题或建议，欢迎提交 Issue 或 Pull Request！
