# PDF to Markdown Converter (Obsidian-Ready)

A powerful, cross-platform application that converts PDFs — including scanned ones — into clean, well-formatted Markdown optimized for **Obsidian** and other note-taking tools.

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)
![Version](https://img.shields.io/badge/version-v2.0.0-blue)
[![Download EXE](https://img.shields.io/badge/Download-Windows%20EXE-brightgreen)](https://github.com/M1ck4/pdf_to_md/releases/latest/download/PDF_to_MD.exe)

## 📸 Screenshot

![PDF to Markdown Converter Interface](doc/Screenshot 2025-11-11 173246.png)

---

## ✨ Features

### 🧠 Smart Text Processing

* **Intelligent heading detection** — Uses font size, ALL-CAPS, and pattern recognition to find headings.
* **Paragraph reconstruction** — Merges wrapped lines and fixes hyphenation (e.g., `trans-\nform` → `transform`).
* **Orphan merging** — Joins short stray lines into previous paragraphs.
* **Drop cap handling** — Ignores oversized decorative initials.

### 🎨 Formatting Preservation

* **Bold** and *italic* text from source PDF.
* Bullet lists (•, ◦, ·, -, —) and numbered lists (1. 2. 3.).
* Lettered outlines (a) b) c)).
* URLs auto-linkified and punctuation normalized.

### 🧼 Automatic Cleanup

* **Header/footer detection** — Removes repeating headers and footers.
* **Punctuation normalization** — Fixes smart quotes, ellipses, and em dashes.
* **Whitespace cleanup** — Ensures neat formatting.

### 🧩 OCR Integration (Tesseract & OCRmyPDF)

* Converts **scanned PDFs** into searchable Markdown.
* Supports **auto**, **tesseract**, and **ocrmypdf** modes.
* Automatically detects when OCR is needed.

| Mode        | Description                               |
| ----------- | ----------------------------------------- |
| `off`       | Fastest mode for text-based PDFs.         |
| `auto`      | Detects if OCR is required automatically. |
| `tesseract` | Uses local Tesseract OCR for conversion.  |
| `ocrmypdf`  | Uses OCRmyPDF for complete document OCR.  |

> 💡 **Windows users:** If Tesseract is not on PATH, set it manually:
>
> ```python
> opts = Options(tesseract_cmd=r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe")
> ```

---

## 📦 Installation

### Option 1: Python (All Platforms)

1. **Install Python 3.8+**
2. **Install dependencies:**

   ```bash
   pip install pymupdf pillow pytesseract
   ```
3. *(Optional)* for OCRmyPDF support:

   ```bash
   pip install ocrmypdf
   ```
4. **Clone the repository:**

   ```bash
   git clone https://github.com/M1ck4/pdf_to_md.git
   cd pdf_to_md
   ```
5. **Run the GUI app:**

   ```bash
   python -m pdfmd.app_gui
   ```

### Option 2: Windows Executable (No Python Needed)

1. Download the latest `.exe` from the [Releases page](https://github.com/M1ck4/pdf_to_md/releases/latest).
2. Run it directly — no installation required.

---

## 📘 OCR Requirements

OCR is **optional**, but required if you want to extract text from **scanned PDFs**.

### 🔹 Tesseract OCR (for `tesseract` or `auto` mode)

**Required:** Only if you want OCR for scanned documents.

#### 🪟 Windows

1. Download the Windows installer from: [Tesseract at UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)
2. Install to the default path (e.g. `C:\Program Files\Tesseract-OCR\`)
3. Ensure it’s added to PATH, or specify it manually:

   ```python
   opts = Options(tesseract_cmd=r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe")
   ```

#### 🍎 macOS

```bash
brew install tesseract
```

#### 🐧 Linux (Debian/Ubuntu)

```bash
sudo apt install tesseract-ocr -y
```

> 💬 You can test your installation by running `tesseract --version` in the terminal.

### 🔹 OCRmyPDF (for `ocrmypdf` mode)

**Optional**, but useful for full-document OCR including images, layout, and metadata.

Install via pip:

```bash
pip install ocrmypdf
```

Or system package manager:

```bash
sudo apt install ocrmypdf -y
```

---

## 🚀 Usage

### 🖥️ GUI Mode

1. **Launch the app** (`python -m pdfmd.app_gui` or `PDF_to_MD.exe`).
2. **Select input PDF** and **choose output Markdown file**.
3. Configure options (OCR mode, preview, export images, etc.).
4. **Click Convert**.

### 🧰 CLI Mode

Run from terminal:

```bash
python -m pdfmd.cli input.pdf --ocr auto --export-images
```

| Option                      | Description                           |           |            |          |
| --------------------------- | ------------------------------------- | --------- | ---------- | -------- |
| `--ocr [off                 | auto                                  | tesseract | ocrmypdf]` | OCR mode |
| `--preview`                 | Converts first 3 pages only           |           |            |          |
| `--export-images`           | Exports images to `_assets/`          |           |            |          |
| `--insert-page-breaks`      | Adds `---` between pages              |           |            |          |
| `--remove-headers`          | Removes repeating headers/footers     |           |            |          |
| `--heading-size-ratio 1.15` | Font-size ratio for heading detection |           |            |          |
| `--orphan-max-len 45`       | Max chars for orphan merging          |           |            |          |

---

## 📂 Example Output

**Input PDF:**

```
CHAPTER 1: INTRODUCTION

This is a paragraph that wraps across
multiple lines in the PDF file.

• First bullet point
• Second bullet point
```

**Output Markdown:**

```markdown
# CHAPTER 1: INTRODUCTION

This is a paragraph that wraps across multiple lines in the PDF file.

- First bullet point
- Second bullet point
```

---

## 🎯 Use Cases

* Academic papers → editable Markdown.
* Books and eBooks → annotated notes.
* Documentation → searchable Markdown archives.
* Obsidian vaults → import PDFs directly.
* Markdown workflows → use with VS Code, Typora, etc.

---

## 🧠 Configuration Reference

| Option                   | Description                                | Default |
| ------------------------ | ------------------------------------------ | ------- |
| `ocr_mode`               | OCR engine: off, auto, tesseract, ocrmypdf | `off`   |
| `ocr_dpi`                | OCR render DPI                             | `300`   |
| `preview_ocr_dpi`        | OCR DPI in preview mode                    | `200`   |
| `ocr_timeout_sec`        | Timeout for OCRmyPDF                       | `1800`  |
| `caps_to_headings`       | Promote ALL-CAPS lines                     | `True`  |
| `defragment_short`       | Merge short fragments                      | `True`  |
| `heading_size_ratio`     | Font size ratio                            | `1.15`  |
| `orphan_max_len`         | Max orphan chars                           | `45`    |
| `remove_headers_footers` | Remove headers/footers                     | `True`  |
| `insert_page_breaks`     | Add page breaks                            | `False` |
| `export_images`          | Save images to `_assets/`                  | `False` |

---

## 🧰 Building the EXE

If you wish to build your own standalone version:

```bash
pip install pyinstaller
pyinstaller --noconsole --onefile --name PDF_to_MD pdfmd/app_gui.py
```

The generated EXE will appear in `dist/`.

---

## ⚠️ Limitations

* Complex tables and multi-column PDFs may not convert perfectly.
* OCR accuracy depends on scan quality and language data.
* Embedded math or diagrams are not interpreted.

---

## 🔖 Latest Release

**Version:** [v2.0.0](https://github.com/M1ck4/pdf_to_md/releases/tag/v2.0.0)
**Released:** November 2025

**SHA-256 checksum:**
`E4FE880E1A00494D31255328A45225118ACF0085BB99C0867C74DF9881B1F085`

Verify your download:

```powershell
Get-FileHash .\PDF_to_MD.exe -Algorithm SHA256
```

[👉 Download the latest release](https://github.com/M1ck4/pdf_to_md/releases/latest)

---

## 🤝 Contributing

You can help by:

* Reporting issues and sharing sample PDFs.
* Suggesting OCR or formatting improvements.
* Submitting pull requests for new features.

### Development Setup

```bash
git clone https://github.com/M1ck4/pdf_to_md.git
cd pdf_to_md
pip install -r requirements.txt
python -m pdfmd.app_gui
```

---

## 📝 License

This project is licensed under the **MIT License**. See [LICENSE](LICENSE).

---

## 🙏 Acknowledgments

* Built with [PyMuPDF](https://pymupdf.readthedocs.io/), [Pillow](https://python-pillow.org/), [Tesseract OCR](https://github.com/tesseract-ocr/tesseract), and [OCRmyPDF](https://github.com/ocrmypdf/OCRmyPDF).
* Designed for seamless integration with [Obsidian](https://obsidian.md/).

---

## 📧 Contact

* **Issues:** [GitHub Issues](https://github.com/M1ck4/pdf_to_md/issues)
* **Discussions:** [GitHub Discussions](https://github.com/M1ck4/pdf_to_md/discussions)

---

**Made with ❤️ for the Obsidian and Markdown communities**
