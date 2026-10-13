"""Shipped content in play order. Each task that adds a world appends it here."""
from .s1_navigate import WORLD as S1
from .f1_basics import WORLD as F1
from .s2_edit import WORLD as S2
from .f2_logic import WORLD as F2
from .s3_format import WORLD as S3
from .f3_conditional import WORLD as F3
from .s4_organize import WORLD as S4
from .f4_lookups import WORLD as F4
from .f5_text import WORLD as F5
from .f6_dates import WORLD as F6

WORLDS: tuple = (S1, F1, S2, F2, S3, F3, S4, F4, F5, F6)
FINAL = None
