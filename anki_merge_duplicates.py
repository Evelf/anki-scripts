#! /home/eve/Documents/Linguistique/coréen/anki-prog/bin/python

from ankisync2.anki import Apkg, db


apkg = Apkg("tmp-dir/All_Decks.apkg")


all_notes = db.Notes.select(db.Notes, db.Models) \
                     .switch(db.Notes) \
                     .join(db.Models, on=(db.Models.id == db.Notes.mid))

dedup_notes = {}
for note in all_notes:
    if note.model.get_sfld_key() != "Korean":
        continue
    if note.sfld in dedup_notes:
        dedup_notes[note.sfld].append(note)
    else:
        dedup_notes[note.sfld] = [note]

for (idx, notes) in dedup_notes.items():
    if len(notes) == 1:
        note = notes.pop()
        tags = set(note.tags)
        note.tags = list((tags - set(["", "duplicate"])))
        note.save()
        print("* unchanged:", note.sfld, note.flds, note.tags)
    else:
        tags = set()
        translation = set()
        image = set()
        priority = set()
        audio = set()
        for note in notes:
            tags |= set(note.tags)
            translation |= set([note.flds[1]])
            audio |= set([note.flds[2]])
            image |= set([note.flds[3]])
            priority |= set([note.flds[4]])
        tags -= set(["duplicate"])
        tags |= set(["to_review"])
        translation -= set([""])
        audio -= set([""])
        image -= set([""])
        priority -= set([""])

        to_keep = notes.pop()
        to_keep.tags = list(tags)
        to_keep.fields['Translation'] = "<br>".join(list(translation))
        to_keep.fields['Audio'] = " ".join(list(audio))
        to_keep.fields['Image'] = " ".join(list(image))
        to_keep.fields['Priority'] = " ".join(list(priority))
        to_keep.save()
        print("** updated to_keep:", to_keep.sfld, to_keep.flds, to_keep.tags)

        for note in notes:
            note.tags = list((set(note.tags) - set(["duplicate"])) | set(["to_delete"]))
            note.save()
            print("--- to_trash:", note.sfld, note.flds, note.tags)

apkg.zip(output="tmp-dir/updated-deck.apkg")
apkg.zip(output="tmp-dir/updated-deck-2.apkg")
apkg.close()
