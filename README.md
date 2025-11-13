# PDF to Markdown Converter (Obsidian‑Ready)

A refined, privacy‑first desktop and CLI tool that converts PDFs, including scanned documents, into clean, structured, Markdown. Built for researchers, professionals, and creators who demand accuracy, speed, and absolute data privacy.

**Fast. Local. Intelligent. Fully offline.**

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)
![Version](https://img.shields.io/badge/version-v1.2.0-purple)

---

## 🛡️ Privacy & Security

Many PDF converters silently upload documents to remote servers. This tool does **not**.

* **No uploads**
* **No telemetry**
* **No cloud processing**
* **No background requests**

Every step, extraction, OCR, reconstruction, and rendering happens **locally on your machine**.

### Trusted for Sensitive Workflows

This project is intentionally designed for environments where confidentiality is non‑negotiable:

* **Medical:** clinical notes, diagnostic reports
* **Legal:** case files, evidence bundles, sworn statements
* **Government:** policy drafts, restricted documents
* **Academic research:** paywalled journals, unpublished materials, field papers
* **Corporate:** financials, architecture documents, IP‑sensitive designs

If your documents must remain under your control, this tool meets that standard.

---

## 🖼️ Interface Preview

A focused, distraction‑free workspace designed around clarity and professional workflows.

### **Dark Mode (default)**

![Dark Mode](doc/Screenshot_dark.png)

> *Light mode is also available inside the application.*

---

## ✨ Key Features

### **Accurate Markdown From Any PDF**

* Smart paragraph reconstruction
* Heading inference based on font metrics
* Bullet list detection
* Inline hyphen unwrap + clean reflow
* Callout and structure‑aware output

### **Scanned PDF Support (OCR)**

* Tesseract (Windows)
* OCRmyPDF (macOS/Linux)
* Auto‑engine selection based on platform and availability
* Fallback systems ensure reliable extraction

### **Modern GUI Experience**

* Polished Dark/Light themes
* Live progress with error‑aware logging
* “Open Output Folder” quick link
* Non‑blocking threaded conversion
* Smooth stop/cancel workflow

### **Profiles System**

Preset workflows:

* **Default** — balanced settings
* **Academic Article** — clean body text, no images, header/footer removal
* **Slides/Handouts** — preserve images + page structure
* **Scan‑Heavy** — OCR‑first focus

User profiles:

* Save your own presets
* Rename or delete user‑defined profiles
* Perfect for repeated workflows

### **Persistent Personalization**

The application remembers:

* Theme preference
* Last used input/output paths
* All toggles and numeric settings
* Last selected profile

### **Productivity Hotkeys**

* **Ctrl+O** — Select input PDF
* **Ctrl+Shift+O** — Select output
* **Ctrl+Enter** — Convert
* **Esc / Ctrl+Shift+X** — Stop

---

## 🧠 Architecture Overview

A modular pipeline ensures clarity, stability, and extensibility.

| Module           | Purpose                                                            |
| ---------------- | ------------------------------------------------------------------ |
| **extract.py**   | PDF extraction + OCR fallback/selection                            |
| **transform.py** | Text cleaning, paragraphing, hyphen logic, heading inference       |
| **render.py**    | Markdown output generation + asset handling                        |
| **pipeline.py**  | Orchestrates the full extraction → transform → render sequence     |
| **utils.py**     | Platform helpers, OCR checks, filesystem tools, structured logging |
| **models.py**    | Typed configuration + document models                              |
| **app_gui.py**   | The polished Tkinter interface with profiles, themes, persistence  |
| **cli.py**       | Command-line interface for automation and batch workflows          |

**Design Philosophy:** small modules with single responsibilities — easy to read, test, and extend.

---

## 🧩 OCR Strategy — Dual‑Engine Intelligence

| Platform    | Default OCR Engine | Notes                                            |
| ----------- | ------------------ | ------------------------------------------------ |
| **Windows** | Tesseract          | Lightweight and reliable for mixed PDFs          |
| **macOS**   | OCRmyPDF           | High‑fidelity layout preservation                |
| **Linux**   | OCRmyPDF           | Strong for research servers and batch automation |

### Auto‑OCR Behavior

* Detects installed engines
* Chooses the best available
* Falls back safely and automatically

---

## ⚙️ Installation

### Python (All Platforms)

```bash
pip install pymupdf pillow pytesseract ocrmypdf
```

```bash
git clone https://github.com/M1ck4/pdf_to_md.git
cd pdf_to_md
python app_gui.py
```

### Windows Executable

Download the EXE from Releases and run. No Python needed.

---

## 🚀 Usage

### GUI

```bash
python app_gui.py
```

Or launch the standalone EXE.

### CLI

```bash
python cli.py input.pdf --ocr auto --export-images
```

---

## 🗂️ Example Output

**Input PDF:** multi‑line wrapped text, bullets, headings.

**Converted Markdown:**

```markdown
# CHAPTER 1: INTRODUCTION

This is a paragraph rebuilt cleanly across lines.

- First bullet
- Second bullet
```

---

## 🦯 Performance Tips

* Use `--preview` for large PDFs
* Lower OCR DPI for slower systems
* Disable OCR entirely for text‑based documents

---

## 🤗 Contributing

You can contribute by:

* Submitting tricky PDFs for testing
* Enhancing OCR heuristics
* Improving formatting logic
* Expanding the profiles system

Developer setup:

```bash
git clone https://github.com/M1ck4/pdf_to_md.git
cd pdf_to_md
pip install -r requirements.txt
python app_gui.py
```

---

## 📜 License

MIT License. Free for personal and commercial use.

---

### ❤️ Built for researchers, creators, professionals and anyone who values privacy.

**Free. Open. Useful. Private. Always.**
