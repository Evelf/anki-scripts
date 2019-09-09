#! /home/eve/Documents/Linguistique/coréen/anki-prog/bin/python


# from ankisync2.anki import Anki2, Apkg
from ankisync2.anki import Apkg, db


apkg = Apkg("tmp-dir/Korean_Food.apkg")
apkg = Apkg("tmp-dir/updated-deck.apkg")

# old_card = next(iter_apkg)
# old_card_o = db.Cards.get(db.Cards.id == old_card['id'])
# model = db.Models.get(db.Models.id == old_card['note']['model']['id'])
# decks = db.Decks.select().where(db.Decks.id == old_card['deck']['id'])
# deck = db.Decks.get(db.Decks.id == old_card['deck']['id'])
# templates = db.Templates.select().where(db.Templates.mid == model)

col = db.Col.get()
print(col.tags)

for note in db.Notes.select(db.Notes, db.Models) \
                .switch(db.Notes) \
                .join(db.Models, on=(db.Models.id == db.Notes.mid)):
    print(note.tags)

# new_note = db.Notes.create(
#     mid=old_card['note']['model']['id'],
#     flds=["front_titi", "back_toto"])
# 
# o = [
#     db.Cards.create(nid=new_note.id, did=deck.id, ord=i)
#     for i, _ in enumerate(templates)
# ]

