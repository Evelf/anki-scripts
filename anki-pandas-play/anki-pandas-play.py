from ankipandas import Collection
import matplotlib.pyplot as plt

col = Collection("/home/eve/.local/share/Anki2/", user="Eve")
cards = col.cards.merge_notes()
counts = cards[cards.has_tag("leech")]["cdeck"].value_counts()
counts.plot.pie(title="Leeches per deck")

# pour sauvegarder en SVG, à utiliser AVANT plt.show()
# parce que plt.show() flush l'image
plt.savefig("test.svg", format="svg")

# Si on appelle pas plt.show() ça n'affiche rien..
plt.show()
