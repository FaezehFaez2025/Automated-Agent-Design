"""
Momentum state dynamics (SkillGrad paper Figure 5 style)
=====================================================

Reads ``train/iter_*/momentum_memory.md`` (pattern record ``M_t``) and plots:

  * Cumulative patterns (purple line)
  * New patterns (red bars)
"""

from __future__ import annotations

import argparse
import math
import re
from pathlib import Path


PATTERN_RE = re.compile(r"^###\s+(\S+)\s*\|", re.MULTILINE)


# ---------------------------------------------------------------------------
# 1. Data: read momentum memories and count patterns
# ---------------------------------------------------------------------------

