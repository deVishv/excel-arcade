"""Shipped content in play order. Each task that adds a world appends it here."""
from .s1_navigate import WORLD as S1
from .f1_basics import WORLD as F1

WORLDS: tuple = (S1, F1,)
FINAL = None
