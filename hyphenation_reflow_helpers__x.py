"""
Fence-aware hyphen unwrap + soft reflow for Markdown.

Key additions:
- Detects fenced code blocks opened by ``` or ~~~ (length >= 3).
- Skips BOTH hyphen unwrapping and paragraph reflow inside fences.
- Supports variable fence length; closing fence must match the opener char and length.

Other preserved behaviors:
- Structural guards for lists, headings, blockquotes, code fences, tables, hr lines, and "Label:" lines.
- Non-breaking abbreviations via explicit set + multi-dot patterns.
- Fixed-width, lookahead-only regexes (no variable-width lookbehinds).

Public API:
- unwrap_hyphenation(text: str, aggressive_hyphen: bool = False) -> str
- reflow_non_sentence_linebreaks(text: str) -> str
- two_pass_unwrap(text: str, aggressive_hyphen: bool = False) -> str
"""
from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Final, Iterable, List, Tuple


# -------------------------
# Abbreviations / tokens
# -------------------------
_NON_BREAKING_ABBREVS: Final[set[str]] = {
    # English
    "e.g.", "i.e.", "vs.", "etc.", "Mr.", "Mrs.", "Ms.", "Dr.", "Prof.",
    "Sr.", "Jr.", "St.", "No.", "Nos.", "Fig.", "Figs.", "Eq.", "Eqs.",
    "pp.", "p.",
    # German
    "z.B.", "bzw.", "bspw.", "ca.", "usw.", "Nr.", "S.",
}

_MULTI_ABBREV_PATTERNS: Final[tuple[re.Pattern[str], ...]] = (
    re.compile(r"(?:[A-Za-z]\.){2,}$"),  # U.S., e.g., i.e., z.B.
    re.compile(r"(?:Nr|No|S|Fig|Eq|pp|p)\.$", re.IGNORECASE),
)

# -------------------------
# Hyphen unwrap (safe)
# -------------------------
_BASIC_HYPHEN_JOIN = re.compile(r"([A-Za-z])-\n(?=[a-z])")
_TITLECASE_JOIN = re.compile(r"([a-z])-\n(?=[A-Z][a-z])")  # Trans-\nAtlantic

# -------------------------
# Structure guards
# -------------------------
_LIST_START = re.compile(
    r"^\s*(?:[*+-]\s|\d+\.\s|[A-Za-z]\)\s|[IVXLCDM]+\.\s)",
    re.IGNORECASE,
)
_HEADING = re.compile(r"^\s{0,3}#{1,6}\s")
_BLOCKQUOTE = re.compile(r"^\s{0,3}>\s")
# Accept both backticks and tildes; variable length (>=3)
_CODE_FENCE_LINE = re.compile(r"^\s{0,3}(`{3,}|~{3,})")
_TABLE_ROW = re.compile(r"^\s*\|")  # Markdown table row
_HR_LINE = re.compile(r"^\s*(?:-{3,}|_{3,}|\*{3,})\s*$")  # --- ___ *** whole line
_LABEL_LINE = re.compile(r"^\s*[A-Za-z][\w /-]{0,24}:\s*$")  # e.g., "Cost:"

# Sentence end chars (with trailing quotes/brackets/braces common in PDFs)
_SENTENCE_END_CORE = ".!?…"
_SENTENCE_TRAILING = "\"»”')]}"
_POSSIBLE_ENDING_PUNCTUATION = tuple(_SENTENCE_END_CORE + _SENTENCE_TRAILING)


@dataclass(frozen=True)
class _Line:
    raw: str

    @property
    def is_blank(self) -> bool:
        return not self.raw.strip()

    @property
    def starts_structural_block(self) -> bool:
        s = self.raw
        return any(
            pat.match(s)
            for pat in (
                _LIST_START,
                _HEADING,
                _BLOCKQUOTE,
                _CODE_FENCE_LINE,
                _TABLE_ROW,
                _HR_LINE,
                _LABEL_LINE,
            )
        )

    def _last_token(self) -> str:
        parts = self.raw.rstrip().split()
        return (parts[-1] if parts else "").strip('"\''"”’)]}»")

    def _matches_multi_abbrev(self, token: str) -> bool:
        return any(p.search(token) for p in _MULTI_ABBREV_PATTERNS)

    def ends_sentence(self) -> bool:
        s = self.raw.rstrip()
        if not s:
            return False
        if s[-1] not in _POSSIBLE_ENDING_PUNCTUATION:
            return False

        token = self._last_token()
        if token.endswith("."):
            if token in _NON_BREAKING_ABBREVS:
                return False
            if self._matches_multi_abbrev(token):
                return False
        return True


# ---------------
# Fence handling
# ---------------
def _split_by_fences(text: str) -> List[tuple[bool, str]]:
    """Split text into [(is_code, chunk)] by fenced code blocks (``` / ~~~)."""
    lines = text.splitlines(keepends=True)
    chunks: List[tuple[bool, str]] = []

    buf: list[str] = []
    in_code = False
    fence_char = ""
    fence_len = 0

    def flush(is_code_block: bool) -> None:
        nonlocal buf
        if buf:
            chunks.append((is_code_block, "".join(buf)))
            buf = []

    for ln in lines:
        m = _CODE_FENCE_LINE.match(ln)
        if m:
            fence_seq = m.group(1)
            char = fence_seq[0]
            count = len(fence_seq)

            if not in_code:
                # Entering code fence
                flush(False)
                in_code = True
                fence_char = char
                fence_len = count
                buf.append(ln)
                continue
            else:
                # Potential closing fence: must match the opener char and len >= opener
                closing = re.match(rf"^\s{{0,3}}{re.escape(fence_char)}{{{fence_len},}}\s*$", ln)
                if closing:
                    buf.append(ln)
                    flush(True)
                    in_code = False
                    fence_char = ""
                    fence_len = 0
                    continue
                # Otherwise, it's just another line inside the code block
                buf.append(ln)
                continue
        else:
            buf.append(ln)

    # Flush remainder
    flush(in_code)
    return chunks


# -------------------------
# Public API
# -------------------------
def unwrap_hyphenation(text: str, aggressive_hyphen: bool = False) -> str:
    """Join words broken by hyphen + newline across wrapped lines OUTSIDE fences."""
    parts = _split_by_fences(text)
    out: list[str] = []
    for is_code, chunk in parts:
        if is_code:
            out.append(chunk)
        else:
            tmp = _BASIC_HYPHEN_JOIN.sub(r"\\1", chunk)
            if aggressive_hyphen:
                tmp = _TITLECASE_JOIN.sub(r"\\1", tmp)
            out.append(tmp)
    return "".join(out)


def reflow_non_sentence_linebreaks(text: str) -> str:
    """Replace *soft* single newlines with spaces OUTSIDE fences to form natural paragraphs."""
    parts = _split_by_fences(text)
    out: list[str] = []

    for is_code, chunk in parts:
        if is_code:
            out.append(chunk)
            continue

        lines = [_Line(l) for l in chunk.splitlines()]
        buf: list[str] = []
        i = 0
        while i < len(lines):
            cur = lines[i]
            if cur.is_blank or i == len(lines) - 1:
                buf.append(cur.raw)
                i += 1
                continue

            nxt = lines[i + 1]
            if nxt.is_blank or nxt.starts_structural_block or cur.ends_sentence():
                buf.append(cur.raw)
                i += 1
                continue

            buf.append(cur.raw.rstrip() + " ")
            i += 1

        out.append("\n".join(buf))

    return "".join(out)


def two_pass_unwrap(text: str, aggressive_hyphen: bool = False) -> str:
    """Run hyphen unwrap then reflow, skipping code fences entirely."""
    text = unwrap_hyphenation(text, aggressive_hyphen=aggressive_hyphen)
    text = reflow_non_sentence_linebreaks(text)
    return text
