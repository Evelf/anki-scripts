#! /home/eve/Documents/Linguistique/coréen/anki-prog/bin/python

import bleach
import html
import re
from ankisync2.anki import Apkg, db


apkg = Apkg("tmp-dir/All_Decks.apkg")


top_100_core_words = db.Notes.select(db.Notes, db.Models) \
                     .switch(db.Notes) \
                     .join(db.Models, on=(db.Models.id == db.Notes.mid)) \
                     .where(db.Models.name == "Basic-Core 100")

dedup_notes = {}
# 판매원<br><br>panmaewon[sound:277613.mp3]
pattern_front = re.compile(r"""
            (?P<korean>.+)
            <br(?: )?(?:/)?><br(?: )?(?:/)?>
            (?P<romanization>[^[]+)
            .sound:(?P<audio>.+)\]
        """, re.X)
# <img src='9477_96square.jpg'><br><br>salesman
pattern_back = re.compile(r"""
            # ^<img src="(?P<image>.+)">
            # <br(?:.)?(?:/)?><br(?:.)?(?:/)?>
            # (<br\s?/><br\s?/> | <br><br>)
            # <img src='9477_96square.jpg'><br><br>salesman
            # ^.img src=.(?P<image>.+)..
            ^(?P<image>.+)
            <br.?.?><br.?.?>
            (?P<translation>.+)$
        """, re.X)
for note in top_100_core_words:
    korean = ""
    audio = ""
    image = ""
    translation = ""

    front = note.flds[0]
    back = note.flds[1]
    rev = False
    front_matches = pattern_front.match(front)
    if front_matches:
        res = front_matches.groupdict()
        korean = res['korean']
        audio = res['audio']

        back_matches = pattern_back.match(back)
        if back_matches:
            res = back_matches.groupdict()
            image = res['image']
            translation = res['translation']
        else:
            print('Front matches, but no back matches?')
            print(front)
            print(back)
    else:
        rev = True
        front_matches = pattern_front.match(back)
        if front_matches:
            res = front_matches.groupdict()
            korean = res['korean']
            audio = res['audio']

            back_matches = pattern_back.match(front)
            if back_matches:
                res = back_matches.groupdict()
                image = res['image']
                translation = res['translation']
            else:
                print('Reversed front matches, but no back matches?')
                print(front)
                print(back)
        else:
            print('No front match at all?')
            print(front)
            print(back)

    if korean in dedup_notes:
        previous_note = dedup_notes[korean]
        if korean != previous_note['korean'] or \
                translation != previous_note['translation'] or \
                audio != previous_note['audio'] or \
                image != previous_note['image']:
            # print("dup soucy:", previous_note, korean, translation, audio, image)
            pass
        note.tags = ["to_delete"]
        note.save()
    elif korean and audio and image and translation:
        dedup_notes[korean] = {
            'korean': korean,
            'translation': translation,
            'audio': audio,
            'image': image}

        note.fields['Korean'] = korean
        note.fields['Translation'] = translation
        note.fields['Audio'] = "[sound:" + audio + "]"
        note.fields['Image'] = image
        note.tags = ["Top::100_Core_Words"]
        note.save()
    else:
        print("soucy:", korean, translation, audio, image)

apkg.zip(output="tmp-dir/updated-deck.apkg")
apkg.close()
