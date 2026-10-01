"""
REBUILD V4 — SHARED CONSTANTS FOR REPRODUCIBILITY
=====================================================================================
One definition, used by every v4 script and by the clean-clone check, of which lines in
an emitted artifact are allowed to differ between runs.

THE RULE
--------
DATA artifacts - CSV, the ledger, constants JSON - carry NO run timestamp at all. They
must be byte-identical across runs, and the clean-clone diff compares them byte for byte
with no exemptions whatsoever.

NARRATIVE artifacts - the .md run logs - may carry a run timestamp, but ONLY in a
declared header line matching one of VOLATILE_LINE_PATTERNS below. The clean-clone diff
ignores exactly those lines and nothing else: a difference anywhere else in a .md is a
real difference and fails the check.

The patterns are deliberately anchored and narrow. A loose pattern would let a genuine
change hide behind an exemption, which is the whole failure this guards against.
"""
import re

# Anchored at the start of the line. Each must match a HEADER line only - never a line
# that could carry a result. Adding a pattern here widens what the clean-clone check
# forgives, so it needs the same scrutiny as changing a result.
VOLATILE_LINE_PATTERNS = (
    r"^- run \(UTC\): ",              # 212, 214: report header
    r"^- generated \d{4}-\d{2}-\d{2}T",  # 213 extra-ciks header
    r"^- finished \(UTC\): ",         # 213 run log
    r"^- pull (started|finished) \(UTC\): ",  # 211 pull log
    r"^# generated \d{4}-\d{2}-\d{2}T",      # commented headers in .txt lists
)

VOLATILE_RE = re.compile("|".join(VOLATILE_LINE_PATTERNS))

# Artifacts that must be byte-identical across runs, with NO exemptions.
NO_TIMESTAMP_SUFFIXES = (".csv", ".json")


def is_volatile(line):
    """True iff this line is a declared, exempt header line."""
    return bool(VOLATILE_RE.match(line))


def strip_volatile(text):
    """Drop exactly the declared volatile header lines, for diffing narrative logs."""
    return "\n".join(ln for ln in str(text).splitlines() if not is_volatile(ln))


def assert_no_timestamp(path, text):
    """Data artifacts must carry no run timestamp. -> list of offending lines."""
    if not str(path).endswith(NO_TIMESTAMP_SUFFIXES):
        return []
    return [ln for ln in str(text).splitlines() if is_volatile(ln)]
