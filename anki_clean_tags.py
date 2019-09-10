#! /home/eve/Documents/Linguistique/coréen/anki-prog/bin/python

from ankisync2.anki import Apkg, db
import re


tag_transformations = [
    (re.compile(r"TTMIK-(?P<unit>\d).(?P<lesson>\d\d)"), "TTMIK::Unit-{unit}::{lesson}"),
    (re.compile(r"level(?P<unit>\d)lesson(?P<lesson>\d\d)"), "TTMIK::Unit-{unit}::{lesson}"),
    (re.compile(r"level(?P<unit>\d)lesson(?P<lesson>\d)"), "TTMIK::Unit-{unit}::0{lesson}"),
    (re.compile(r"Iyagi::(?P<lesson>\d\d)"), "TTMIK::Iyagi::{lesson}"),
    (re.compile(r"Iyagi_(?P<lesson>\d\d)"), "TTMIK::Iyagi::{lesson}"),
    (re.compile(r"NIK-(?P<date>\d\d\d\d-\d\d-\d\d)"), "TTMIK::NIK::{date}"),
    (re.compile(r"dif(?P<difficulty>\d)"), "Difficulty::dif{difficulty}"),
    (re.compile(r"#(?P<difficulty>\d)"), "Difficulty::#{difficulty}"),
    ]

def transform_tag(tag):
    for (pattern, target) in tag_transformations:
        matches = pattern.match(tag)
        if matches:
            variables = matches.groupdict()
            return target.format(**variables)
    return tag


apkg = Apkg("tmp-dir/All_Decks.apkg")

notes = db.Notes.select()

for note in notes:
    new_tags = set()
    old_tags = set(note.tags) - set([""])
    for tag in old_tags:
        res = transform_tag(tag)
        if res != tag:
            print(tag, "=>", res)
        new_tags.add(res)
    if new_tags ^ old_tags:
        note.tags = list(new_tags)
        note.save()

apkg.zip(output="tmp-dir/updated-deck.apkg")
apkg.close()
