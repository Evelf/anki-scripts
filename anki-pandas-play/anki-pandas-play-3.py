from __future__ import annotations
import pandas as pd
from ankipandas import Collection
import matplotlib.pyplot as plt

col = Collection("/home/eve/.local/share/Anki2/", user="Eve")

selected = col.cards[col.cards.cdeck.isin(["Coréen"])]

print(selected)

# plt.show()
