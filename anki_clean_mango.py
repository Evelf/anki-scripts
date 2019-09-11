#! /home/eve/Documents/Linguistique/coréen/anki-prog/bin/python

import bleach
import html
import re
from ankisync2.anki import Apkg, db


apkg = Apkg("tmp-dir/All_Decks.apkg")


deck = db.Decks.get(db.Decks.name == "Mango Korean")
new_model = db.Models.get(db.Models.name == "Basic-Retro Grammar")
new_model.fix_sfld_key()
templates = db.Templates.select().where(db.Templates.mid == new_model)

mango_notes = db.Notes.select(db.Notes, db.Models) \
                     .switch(db.Notes) \
                     .join(db.Models, on=(db.Models.id == db.Notes.mid)) \
                     .where(db.Models.name == "Basic-Mango")

# <img src='9477_96square.jpg'><br><br>salesman
pattern_back = re.compile(r"""
            ^(?P<formatted_korean>.+?)
            (<br.?.?>(?P<notes>.+?)){0,1}?
            (<br.?.?>(?P<audio>\[sound:.+])){0,1}(<br.?.?>)?$
        """, re.X)
for note in mango_notes:
    korean = ""
    formatted_korean = ""
    translation = ""
    formatted_translation = ""
    audio = ""
    notes = ""

    formatted_translation = note.flds[0].strip()
    translation = bleach.clean(formatted_translation, tags=[], strip=True, strip_comments=True)
    translation = html.unescape(translation).strip()

    back = note.flds[1].strip()
    back_matches = pattern_back.match(back)
    if back_matches:
        res = back_matches.groupdict()
        formatted_korean = res['formatted_korean']
        korean = bleach.clean(formatted_korean, tags=[], strip=True, strip_comments=True)
        korean = html.unescape(korean).strip()
        if 'notes' in res and res['notes']:
            notes = res['notes'].strip()
        if 'audio' in res and res['audio']:
            audio = res['audio'].strip()

    if korean:
        # print(back)
        # print("---", korean, "---", audio, "---", notes)
        new_note = db.Notes.create(
            mid=new_model.id,
            fields={
                "Korean": korean,
                "Formatted Korean": formatted_korean,
                "Translation": translation,
                "Formatted Translation": formatted_translation,
                "Audio": audio,
                "Image": "",
                "Notes": notes,
                "Source": "Korean sentences with Audio - Updated 2016-01-31",
                "Target Language": "En",
            },
            tags=list(set(note.tags) - set([""])))
        new_note.save()
        for i, _ in enumerate(templates):
            db.Cards.create(nid=new_note.id, did=deck.id, ord=i)
        note.tags.append("to_delete")
        note.save()
    else:
        print(back, "---", formatted_korean, "---", korean, "---", audio)

apkg.zip(output="tmp-dir/updated-deck.apkg")
apkg.close()
