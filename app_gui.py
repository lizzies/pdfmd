#!/usr/bin/env python3
"""
GUI for PDF → Markdown (pdf_to_md)

Run one of:
  • python -m pdf_to_md.gui
  • python gui.py          (when run from the repo folder next to models.py, pipeline.py, etc.)

Features:
  - Choose input/output paths
  - OCR modes: off/auto/tesseract/ocrmypdf
  - Preview first 3 pages
  - Export images to <output>_assets/
  - Insert page breaks (---)
  - Remove repeating headers/footers
  - Promote ALL-CAPS to headings
  - Defragment orphan lines
  - Heading size ratio & orphan max length controls
  - Aggressive hyphen unwrap toggle
  - Protect fenced code blocks toggle
  - Live logs + determinate progress bar
"""

from __future__ import annotations

import threading
import traceback
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# ---------- Robust imports: package or script ----------
try:
    # When installed / run as a package module
    from pdf_to_md.models import Options
    from pdf_to_md.pipeline import pdf_to_markdown
    from pdf_to_md.utils import os_display_path
except Exception:
    # Fallback to local imports when running as a loose script
    import os, sys
    _HERE = os.path.dirname(os.path.abspath(__file__))
    if _HERE not in sys.path:
        sys.path.insert(0, _HERE)
    from models import Options  # type: ignore
    from pipeline import pdf_to_markdown  # type: ignore
    from utils import os_display_path  # type: ignore

OCR_CHOICES = ["off", "auto", "tesseract", "ocrmypdf"]


class PdfMdApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("PDF → Markdown")
        self.geometry("860x560")
        self.minsize(820, 520)

        self._worker: threading.Thread | None = None
        self._build_vars()
        self._build_ui()
        self._wire_events()

    # ------------------------------- State -------------------------------
    def _build_vars(self) -> None:
        self.in_path_var = tk.StringVar()
        self.out_path_var = tk.StringVar()

        self.ocr_var = tk.StringVar(value=OCR_CHOICES[0])
        self.preview_var = tk.BooleanVar(value=False)
        self.export_images_var = tk.BooleanVar(value=False)
        self.page_breaks_var = tk.BooleanVar(value=False)

        self.rm_edges_var = tk.BooleanVar(value=True)
        self.caps_to_headings_var = tk.BooleanVar(value=True)
        self.defrag_var = tk.BooleanVar(value=True)

        self.orphan_len_var = tk.IntVar(value=45)
        self.heading_ratio_var = tk.DoubleVar(value=1.15)

        self.aggressive_hyphen_var = tk.BooleanVar(value=False)
        self.protect_code_var = tk.BooleanVar(value=True)

        # internal
        self._progress_max = 100

    # ------------------------------- UI -------------------------------
    def _build_ui(self) -> None:
        pad = {"padx": 10, "pady": 8}

        root = ttk.Frame(self)
        root.pack(fill=tk.BOTH, expand=True)

        # Paths
        paths = ttk.LabelFrame(root, text="Paths")
        paths.pack(fill=tk.X, **pad)

        ttk.Label(paths, text="Input PDF:").grid(row=0, column=0, sticky="w")
        in_entry = ttk.Entry(paths, textvariable=self.in_path_var)
        in_entry.grid(row=0, column=1, sticky="ew", padx=(8, 8))
        in_btn = ttk.Button(paths, text="Browse…", command=self._choose_input)
        in_btn.grid(row=0, column=2, sticky="e")

        ttk.Label(paths, text="Output .md:").grid(row=1, column=0, sticky="w")
        out_entry = ttk.Entry(paths, textvariable=self.out_path_var)
        out_entry.grid(row=1, column=1, sticky="ew", padx=(8, 8))
        out_btn = ttk.Button(paths, text="Browse…", command=self._choose_output)
        out_btn.grid(row=1, column=2, sticky="e")

        paths.columnconfigure(1, weight=1)

        # Options
        opts = ttk.LabelFrame(root, text="Options")
        opts.pack(fill=tk.X, **pad)

        # Row 0
        ttk.Label(opts, text="OCR:").grid(row=0, column=0, sticky="w")
        ocr_combo = ttk.Combobox(
            opts, textvariable=self.ocr_var, values=OCR_CHOICES, state="readonly", width=12
        )
        ocr_combo.grid(row=0, column=1, sticky="w", padx=(6, 18))

        ttk.Checkbutton(opts, text="Preview first 3 pages", variable=self.preview_var).grid(row=0, column=2, sticky="w")
        ttk.Checkbutton(opts, text="Export images", variable=self.export_images_var).grid(row=0, column=3, sticky="w")
        ttk.Checkbutton(opts, text="Insert page breaks (---)", variable=self.page_breaks_var).grid(row=0, column=4, sticky="w")

        # Row 1
        ttk.Checkbutton(opts, text="Remove repeating header/footer", variable=self.rm_edges_var).grid(row=1, column=0, columnspan=2, sticky="w")
        ttk.Checkbutton(opts, text="Promote CAPS to headings", variable=self.caps_to_headings_var).grid(row=1, column=2, sticky="w")
        ttk.Checkbutton(opts, text="Defragment short orphans", variable=self.defrag_var).grid(row=1, column=3, sticky="w")

        # Row 2
        ttk.Label(opts, text="Heading size ratio").grid(row=2, column=0, sticky="w")
        hs = ttk.Spinbox(opts, from_=1.0, to=2.5, increment=0.05, textvariable=self.heading_ratio_var, width=6)
        hs.grid(row=2, column=1, sticky="w")

        ttk.Label(opts, text="Orphan max length").grid(row=2, column=2, sticky="w")
        om = ttk.Spinbox(opts, from_=10, to=200, increment=1, textvariable=self.orphan_len_var, width=6)
        om.grid(row=2, column=3, sticky="w")

        # Row 3
        ttk.Checkbutton(opts, text="Aggressive hyphen unwrap", variable=self.aggressive_hyphen_var).grid(row=3, column=0, columnspan=2, sticky="w")
        ttk.Checkbutton(opts, text="Protect fenced code blocks", variable=self.protect_code_var).grid(row=3, column=2, columnspan=2, sticky="w")

        for c in range(5):
            opts.columnconfigure(c, weight=1)

        # Controls
        controls = ttk.Frame(root)
        controls.pack(fill=tk.X, **pad)
        self.go_btn = ttk.Button(controls, text="Convert → Markdown", command=self._on_convert)
        self.go_btn.pack(side=tk.RIGHT)

        # Progress + log
        prog = ttk.LabelFrame(root, text="Progress")
        prog.pack(fill=tk.BOTH, expand=True, **pad)

        self.pbar = ttk.Progressbar(prog, orient=tk.HORIZONTAL, mode="determinate", maximum=self._progress_max)
        self.pbar.pack(fill=tk.X, padx=8, pady=6)

        self.log_txt = tk.Text(prog, height=16, wrap="word")
        self.log_txt.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))
        self.log_txt.configure(state=tk.DISABLED)

    # ------------------------------ Events ------------------------------
    def _wire_events(self) -> None:
        self.in_path_var.trace_add("write", lambda *_: self._suggest_output())

    # ------------------------------ Helpers ------------------------------
    def _choose_input(self) -> None:
        path = filedialog.askopenfilename(
            title="Select PDF",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
        )
        if not path:
            return
        self.in_path_var.set(os_display_path(path))

    def _choose_output(self) -> None:
        initial = self.out_path_var.get().strip() or ""
        path = filedialog.asksaveasfilename(
            title="Save Markdown As",
            defaultextension=".md",
            initialfile=(Path(initial).name if initial else None),
            filetypes=[("Markdown", "*.md"), ("All files", "*.*")],
        )
        if not path:
            return
        self.out_path_var.set(os_display_path(path))

    def _suggest_output(self) -> None:
        """When input changes, suggest a matching .md beside it (if empty)."""
        inp = self.in_path_var.get().strip()
        if not inp:
            return
        try:
            p = Path(inp)
            if p.suffix.lower() == ".pdf":
                out = p.with_suffix(".md")
            else:
                out = Path(str(p) + ".md")
            if not self.out_path_var.get().strip():
                self.out_path_var.set(os_display_path(out))
        except Exception:
            pass

    def _append_log(self, msg: str) -> None:
        self.log_txt.configure(state=tk.NORMAL)
        self.log_txt.insert(tk.END, msg.rstrip() + "\n")
        self.log_txt.see(tk.END)
        self.log_txt.configure(state=tk.DISABLED)

    def _set_progress(self, val: int) -> None:
        self.pbar["value"] = max(0, min(self._progress_max, int(val)))

    def _map_progress(self, done: int, total: int) -> None:
        # Pipeline may call progress as arbitrary (done, total) within stages; map to 0..100
        try:
            pct = 0
            if total > 0:
                pct = int((done / total) * 100)
            self.after(0, lambda: self._set_progress(pct))
        except Exception:
            pass

    # ------------------------------ Actions ------------------------------
    def _on_convert(self) -> None:
        if self._worker and self._worker.is_alive():
            messagebox.showinfo("Busy", "Conversion already in progress.")
            return

        inp = self.in_path_var.get().strip()
        out = self.out_path_var.get().strip()
        if not inp:
            messagebox.showerror("Missing input", "Please choose an input PDF.")
            return
        if not out:
            messagebox.showerror("Missing output", "Please choose an output Markdown path.")
            return

        # Disable button during work
        self.go_btn.configure(state=tk.DISABLED)
        self._set_progress(0)
        self._clear_log()
        self._append_log(f"Input : {inp}")
        self._append_log(f"Output: {out}")

        # Build Options for the engine
        opts = Options(
            ocr_mode=self.ocr_var.get().strip().lower(),
            preview_only=bool(self.preview_var.get()),
            export_images=bool(self.export_images_var.get()),
            insert_page_breaks=bool(self.page_breaks_var.get()),
            remove_headers_footers=bool(self.rm_edges_var.get()),
            caps_to_headings=bool(self.caps_to_headings_var.get()),
            defragment=bool(self.defrag_var.get()),
            heading_size_ratio=float(self.heading_ratio_var.get()),
            orphan_max_len=int(self.orphan_len_var.get()),
            aggressive_hyphen=bool(self.aggressive_hyphen_var.get()),
            protect_code_blocks=bool(self.protect_code_var.get()),
        )

        def worker():
            try:
                # Progress + log callbacks must be thread-safe via .after
                def log_cb(s: str):
                    self.after(0, lambda: self._append_log(s))

                def prog_cb(done: int, total: int):
                    self._map_progress(done, total)

                pdf_to_markdown(
                    input_pdf=inp,
                    output_md=out,
                    options=opts,
                    progress_cb=prog_cb,
                    log_cb=log_cb,
                )
                self.after(0, lambda: self._append_log("Done."))
            except Exception as e:
                tb = traceback.format_exc(limit=6)
                self.after(0, lambda: self._append_log(f"Error: {e}\n{tb}"))
                self.after(0, lambda: messagebox.showerror("Conversion error", f"{e}"))
            finally:
                self.after(0, lambda: self.go_btn.configure(state=tk.NORMAL))
                self.after(0, lambda: self._set_progress(100))

        self._worker = threading.Thread(target=worker, daemon=True)
        self._worker.start()

    def _clear_log(self) -> None:
        self.log_txt.configure(state=tk.NORMAL)
        self.log_txt.delete("1.0", tk.END)
        self.log_txt.configure(state=tk.DISABLED)


def main() -> None:
    app = PdfMdApp()
    app.mainloop()


if __name__ == "__main__":
    main()
