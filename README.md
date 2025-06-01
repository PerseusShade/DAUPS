# DAUPS README (English)

[![GitHub](https://img.shields.io/badge/GitHub-Repo-blue?logo=github)](https://github.com/PerseusShade/DAUPS-ext)

🌐 **Available languages**:
[English](README.md) | [Français](README.fr.md)

## Description

This is the README for the **DAUPS** extension, which provides support for the custom language **daups** — a simple, pseudocode-like language used for teaching and experimenting with algorithmic concepts.

## 📦 Extension Information

This Visual Studio Code extension includes:

- Syntax highlighting for **daups** code.
- Hover information for functions and variables.
- Code completion for keywords and user-defined symbols.
- Inline decorations and diagnostics.
- Script execution via an embedded Python-based interpreter.

Documentation of the **daups** language: [https://perseusshade.github.io/DAUPS-docs/EN.html](https://perseusshade.github.io/DAUPS-docs/EN.html)

## ⚙️ Requirements

You must have **Python 3.x** installed. The execution of `daups` scripts relies on a Python interpreter included with the extension.

To check your Python version:

```bash
python3 --version
```

If not installed, download it from: [https://www.python.org/downloads/](https://www.python.org/downloads/)

## 🔧 Extension Settings

This extension contributes the following settings:

- `daups.enableUnusedVariableHighlight`: Enable/disable highlighting of unused variables (default: `true`)
- `daups.pythonInterpreterPath`: Path to the Python interpreter (optional, default: `python3`)
- `daups.showExecutionOutput`: Automatically display the output panel after script execution (default: `true`)

## 🐞 Known Issues

- No real-time type error checking is currently implemented.
- Some errors might not be handled properly.
- Occasional issues may arise when running `daups` files.
- Minor inconsistencies may exist in how the language is interpreted.

## 📦 Release Notes

### 1.0.0

Initial release of the **DAUPS** extension.

## 👤 About the Author

This extension was developed by a student as a personal project during free time. It aims to help learners of algorithmic thinking by making pseudocode more interactive and accessible within a modern code editor like Visual Studio Code.

Source code and updates: [https://github.com/PerseusShade/DAUPS-ext](https://github.com/PerseusShade/DAUPS-ext)

Full project : [https://github.com/PerseusShade/DAUPS](https://github.com/PerseusShade/DAUPS)

If you encounter errors, have questions, or want to suggest improvements, feel free to open an issue:
👉 [https://github.com/PerseusShade/DAUPS-ext/issues](https://github.com/PerseusShade/DAUPS-ext/issues)

---

**Enjoy using DAUPS in Visual Studio Code!**