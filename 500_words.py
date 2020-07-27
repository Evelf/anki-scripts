#! /home/eve/Documents/coréen/anki-python-files/anki-venv/bin/python

import bleach
import html
import re
import json
from ankisync2.anki import Apkg, db
from os.path import dirname, join
import shutil
from itertools import permutations


apkg = Apkg("tmp-dir/All_Decks.apkg")
wordlist_filename = "../TTMIK/My_First_500_Korean_Words/Day 02-vocabulary.txt"
model_name = 'Ko + Translation + Dictation (opt)'

print("Deck?")
deck = db.Decks.get(db.Decks.name == "Default")
model = db.Models.get(db.Models.name == model_name)
model.fix_sfld_key()
templates = db.Templates.select().where(db.Templates.mid == model)

# model.name: 'Minimal-Pair-Sound'
# * PS-Key
# * Audio
# * PS-Choices
# * PS-Answer

def update_or_create_note(notes, field_value, related, page, day):
    print(field_value + ", related " + str(related) + ", page " + str(page) + ", day " + str(day))

    filtered_notes = notes.where(db.Notes.sfld == field_value)
    if len(filtered_notes) > 1:
        # throw exception
        print("more than one!")
        pass

    if len(filtered_notes) == 1:
        note = filtered_notes.get()
        print("exists")
    else:
        # create note
        note = db.Notes.create(mid=model.id, fields={"Korean": field_value})
        for i, _ in enumerate(templates):
            db.Cards.create(nid=note.id, did=deck.id, ord=i)
        print("created")

    # update note with "TTMIK::First500Words::Day01::Related"
    tag = "TTMIK::First500Words::Day" + day
    if related:
        tag += "::Related"
    note.tags.append(tag)

    # update note.Notes with page number
    field_notes = note.flds[2]
    if field_notes:
        note.fields['Notes'] = note.flds[2] \
                               + "<br>TTMIK My First 500 Korean Words, p. " \
                               + page
    else:
        note.fields['Notes'] = "TTMIK My First 500 Korean Words, p. " + page

    print(note.tags)
    print(note.fields['Notes'])
    note.save()


pattern = re.compile("^# Day (.+)$|^## p\.(.+)$")
day = ""
page = -1
related = False

notes = db.Notes.select(db.Notes, db.Models) \
          .switch(db.Notes).join(db.Models, on=(db.Models.id == db.Notes.mid)) \
          .filter(db.Models.name == model_name)
with open (wordlist_filename, "r") as myfile:
    for full_line in myfile:
        line = full_line.strip()
        if "" == line:
            related = False
        else:
            matches = pattern.match(line)
            if matches:
                if matches.group(1):
                    day = matches.group(1)
                elif matches.group(2):
                    page = matches.group(2)
            else:
                update_or_create_note(notes, line, related, page, day)
                related = True


apkg.zip(output="tmp-dir/updated-deck-2.apkg")
apkg.close()
