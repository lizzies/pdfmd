"""
Hyphenation & line-reflow helpers for PDF -> Markdown pipelines.
Drop-in, pure-Python. Safe defaults; configurable via kwargs.
"""
from __future__ import annotations
import re
from typing import Iterable


#* ===================== Helpers: Reflow linebreaks =====================

# Unicode line separators:
_LINESEP = r"(?:\r?\n|\u2028|\u2029)"
#* Memo to future me: Find the time to finally fix this annoying \\n reformating issue in this damn code reformater!

# Unicode hyphens
_HYPHENS = r"[\-\u2010\u2011\u2012\u2013\u2014]"  # -, ‐, -, ‒, –, —


# Step 1: unwrap hyphens: "...trans-\\nport" -> "transport"
# (Default) logic: only unwrap if next token starts lower-case.
_SAFE_HYPHEN_UNWRAP = re.compile(rf"(?<=[A-Za-z]){_HYPHENS}\s*{_LINESEP}(?=[a-z])")

# (Optional) aggressive unwrap: also join if next token is TitleCase, but avoid when the left side is 
# ALLCAPS (== likely an acronym split).
#// _AGGR_HYPHEN_UNWRAP = re.compile(rf"(?<![A-Z]{{2,}})(?<=[A-Za-z]){_HYPHENS}\s*{_LINESEP}(?=[A-Z][a-z])")
_AGGR_HYPHEN_UNWRAP = re.compile(rf"(\b[A-Za-z]+)({_HYPHENS})\s*({_LINESEP})(?=[A-Z][a-z])")



#* ===================== Helpers: Reflow linebreaks =====================

# Common non–sentence-ending abbreviations (extends easily).
# Includes English + German academic/tech abbreviations. 
# If you can think of more or want to add lang support, please feel free...  
#! NOTE: keep it all lowercase; tokens will be converted to lowercase matching. 

_NON_BREAKING_ABBREVS = {
    # English
    "mr.", "mrs.", "ms.", "dr.", "prof.", "sr.", "jr.", "vs.", "etc.",
    "e.g.", "i.e.", "fig.", "eq.", "ref.", "sec.", "no.", "art.",
    "al.", "ca.", "approx.", "dept.", "est.", "tab.",
    # German
    "z. b.", "z.b.", "vgl.", "usw.", "nr.", "s.", "abb.", "bsp.", "tab.",
}

# Single-token non-breaking abbreviations (extend as needed)
_NON_BREAKING_ABBREVS = {
    # English
    "mr.", "mrs.", "ms.", "dr.", "prof.", "sr.", "jr.",
    "e.g.", "i.e.", "etc.", "fig.", "eq.", "ref.", "sec.", "no.", "art.", "al.", "vs.",
    # German
    "vgl.", "usw.", "nr.", "s.", "abb.", "bsp.", "tab.",
}

# Multi-token patterns that must not cause a break before next line
# NOTE: case-insensitive, supports normal space, NBSP (U+00A0), NNBSP (U+202F)
# NOTE: This became necessary as I found a number of common german abbrevations being separated by spaces 
_MULTI_ABBREV_PATTERNS = [
    re.compile(r"(?i)\bz\.\s*[\u00A0\u202F]?\s*b\.\s*" + _LINESEP + r"(?=\S)"),
    #TODO Add more as needed, e.g. (?i)\bu\.\s*a\.\s* for "u. a."
]

def _token_is_nonbreaking(word: str) -> bool:
    return word.lower() in _NON_BREAKING_ABBREVS 

def _fix_false_sentence_breaks(text: str) -> str:
    """
    Prevent reflow break after abbreviations like 'e.g.' or 'z. B.'
    by changing 'e.g.\nNext' -> 'e.g. Next' (space). We only touch
    cases where a single newline follows the abbreviation.
    """
    # First handle multi-token patterns
    for pat in _MULTI_ABBREV_PATTERNS:
        text = pat.sub(lambda m: m.group(0).replace("\n", " ").replace("\r", " "), text)

    # Then handle single-token cases: "Fig.\n2" -> "Fig. 2"
    def repl(m: re.Match) -> str:
        token = m.group(1)
        if token.lower() in _NON_BREAKING_ABBREVS:
            return token + " "
        return token + m.group(2)  # original newline
    # capture token and the actual newline sequence as group(2)
    text = re.sub(rf"(\b[\w\.]+)\s*({_LINESEP})(?=\S)", repl, text)
    return text


# Characters that *end* sentences (keep newline after these)
_SENT_END = set(".!?" + "…" + "\"»”" + ")]}")

# Precompiled tests for "structural" next-line starters we must NOT join into
_NEXT_IS_STRUCTURAL = re.compile(
    r"""^[ \t]*([\-\*\+]              # bullet list: -, *, +
        | \d{1,3}[.)]                 # ordered list: 1.  1)
        | [A-Za-z][.)]                # alpha list:  a.  a)
        | >                           # blockquote
        | \#{1,6}                     # heading
        | \|                          # table row
        | (?:-{3,}|_{3,}|\*{3,})$     # hr-like line (--- *** ___)
    )\b""",
    re.X
)

def reflow_non_sentence_linebreaks(text: str) -> str:
    """
    Collapse single newlines that are *not* sentence endings *and* whose next line
    is not a structural Markdown starter (`_NEXT_IS_STRUCTURAL`). Preserve paragraph breaks (blank lines).
    """
    lines = text.splitlines(True)
    out = []
    for i, line in enumerate(lines):
        out.append(line)
        # If this line ends with a newline and there is a next line...
        if line.endswith(("\n", "\r")) and i + 1 < len(lines):
            curr = line.rstrip("\r\n")
            nxt  = lines[i + 1]
            # If it's a blank line => paragraph break, keep as-is
            if nxt.strip() == "":
                continue
            # If sentence-ending punctuation -> keep newline
            if curr and curr[-1] in _SENT_END:
                continue
            # If the next line starts with structural Markdown -> keep newline
            if _NEXT_IS_STRUCTURAL.match(nxt):
                continue
            # Otherwise: replace the *single* newline with a space by swallowing the newline we just appended:
            out[-1] = curr + " "
    return "".join(out)

#* ===================== Helper: hyphen unwrap =====================

def unwrap_hyphenation(text: str, aggressive: bool = False) -> str:
    """
    Remove hyphen + newline wraps. If aggressive=True, also join
    'Trans-\nAtlantic' -> 'TransAtlantic' with safeguards.
    """
    
    text = _SAFE_HYPHEN_UNWRAP.sub("", text)

    if aggressive:
        def _aggr_repl(m: re.Match) -> str:
            left = m.group(1)
            hyph = m.group(2)   # original hyphen (could be unicode)
            nl   = m.group(3)   # original newline sequence
            # If left token is ALLCAPS (len >=2), keep the hyphen+newline
            if len(left) >= 2 and left.isupper():
                return left + hyph + nl
            # else join (drop hyphen+newline)
            return left
        text = _AGGR_HYPHEN_UNWRAP.sub(_aggr_repl, text)

    return text

#* ===================== mask codeblocks from reflow =====================

def _split_fenced_blocks(md: str):
    """
    Yield (is_code, segment) tuples. Detects ``` and ~~~ fences with optional lang.
    Keeps fences in the code segments.
    """
    
    out = []
    i = 0
    n = len(md)
    fence_re = re.compile(r'^(?P<indent>\s*)(?P<fence>`{3,}|~{3,})(?P<info>[^\n]*)\n', re.M)
    pos = 0
    while True:
        m = fence_re.search(md, pos)
        if not m:
            out.append((False, md[pos:]))
            break
        start = m.start()
        # non-code span before the fence
        if start > pos:
            out.append((False, md[pos:start]))
        fence = m.group('fence')
        # find closing fence of same type
        close_re = re.compile(rf'^[ \t]*{re.escape(fence)}[ \t]*\n', re.M)
        close = close_re.search(md, m.end())
        end = (close.end() if close else n)
        out.append((True, md[m.start():end]))
        pos = end
    return out

def _split_indented_code(md: str):
    """
    Coarse split for indented code blocks (>=4 spaces or a tab at line start).
    This is optional; fenced detection above already covers most cases.
    """
    parts = []
    buf = []
    in_code = False
    for line in md.splitlines(True):
        is_code_line = bool(re.match(r'^(?:\t| {4,})', line)) and not line.strip() == ''
        if is_code_line or (in_code and (line.strip() != '' and re.match(r'^(?:\t| {4,})', line))):
            if not in_code:
                # flush text buffer
                if buf:
                    parts.append((False, ''.join(buf)))
                    buf = []
                in_code = True
            buf.append(line)
        else:
            if in_code:
                parts.append((True, ''.join(buf)))
                buf = []
                in_code = False
            buf.append(line)
    if buf:
        parts.append((in_code, ''.join(buf)))
    return parts

def _mask_code_regions(md: str):
    """
    First split by fenced blocks, then inside non-code chunks split out indented blocks.
    Returns list of (is_code, segment).
    """
    final = []
    for is_code, seg in _split_fenced_blocks(md):
        if is_code:
            final.append((True, seg))
        else:
            for is_code2, seg2 in _split_indented_code(seg):
                final.append((is_code2, seg2))
    return final


#* ===================== Wrapper function =====================

#* NOOP This version of `two_pass_unwrap()` ignores `_mask_code_regions()`. 
# def two_pass_unwrap(text: str, aggressive_hyphen: bool = False) -> str:
#     """
#     Convenience wrapper: hyphen unwrap (1st pass) + reflow (2nd pass).
#     """
#     return reflow_non_sentence_linebreaks(unwrap_hyphenation(text, aggressive=aggressive_hyphen))

def two_pass_unwrap(text: str, aggressive_hyphen: bool = False, protect_code: bool = True) -> str:
    """
    Convenience wrapper: hyphen unwrap (1st pass) + reflow (2nd pass).
    If protect_code=True, skip fenced/indented code blocks.
    """
    if not protect_code:
        return reflow_non_sentence_linebreaks(unwrap_hyphenation(text, aggressive=aggressive_hyphen))

    pieces = _mask_code_regions(text)
    out = []
    for is_code, seg in pieces:
        if is_code:
            out.append(seg)
        else:
            seg = unwrap_hyphenation(seg, aggressive=aggressive_hyphen)
            seg = reflow_non_sentence_linebreaks(seg)
            out.append(seg)
    return "".join(out)


#NOTE If you also want a CLI post-processor for existing .md files, you can use:

def process_lines(lines: Iterable[str], aggressive_hyphen: bool = False) -> str:
    """
    If you already have a list of markdown/plain lines, stitch and clean.
    """
    return two_pass_unwrap("\n".join(lines), aggressive_hyphen=aggressive_hyphen)
