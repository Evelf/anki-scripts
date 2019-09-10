#! /home/eve/Documents/Linguistique/coréen/anki-prog/bin/python

import bleach
import html
import re
from ankisync2.anki import Apkg, db


apkg = Apkg("tmp-dir/All_Decks.apkg")


new_model = db.Models.get(db.Models.name == "Basic-Retro Grammar")

mango_notes = db.Notes.select(db.Notes, db.Models) \
                     .switch(db.Notes) \
                     .join(db.Models, on=(db.Models.id == db.Notes.mid)) \
                     .where(db.Models.name == "Basic-Mango")

# <img src='9477_96square.jpg'><br><br>salesman
pattern_back = re.compile(r"""
            ^(?P<formatted_korean>.+)<br.?.?>(?P<audio>.+)(?:<br.?.?>)$
        """, re.X)
for note in mango_notes:
    korean = ""
    formatted_korean = ""
    translation = ""
    formatted_translation = ""
    audio = ""

    formatted_translation = note.flds[0]
    translation = bleach.clean(formatted_translation, tags=[], strip=True, strip_comments=True)
    translation = html.unescape(translation).strip()

    back = note.flds[1]
    back_matches = pattern_back.match(back)
    if back_matches:
        res = back_matches.groupdict()
        audio = res['audio']
        formatted_korean = res['formatted_korean']
        korean = bleach.clean(formatted_korean, tags=[], strip=True, strip_comments=True)
        korean = html.unescape(korean).strip()

    # print(note.flds, translation, korean, audio)
    print(translation, "---", korean, "---", audio)
    if korean and audio:
        note.model = new_model
        note.fields = {
            "Korean": korean,
            "Formatted Korean": formatted_korean,
            "Translation": translation,
            "Formatted Translation": formatted_translation,
            "Audio": audio,
            "Image": "",
            "Source": "Korean sentences with Audio - Updated 2016-01-31",
            "Target Language": "En",
        }
        note.save()

apkg.zip(output="tmp-dir/updated-deck.apkg")
apkg.close()
