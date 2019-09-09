#! /home/eve/Documents/Linguistique/coréen/anki-prog/bin/python

from ankisync2.anki import Apkg, db


apkg = Apkg("tmp-dir/All_Decks.apkg")

# col = db.Col.get()
# print(col.tags)

# for note in db.Notes.select(db.Notes, db.Models) \
#                 .switch(db.Notes) \
#                 .join(db.Models, on=(db.Models.id == db.Notes.mid)):
#     print(note.tags)


# decks = db.Decks.select()
# for deck in decks:
#     print(deck.id, deck.name)

# top_verbs_deck = db.Decks.get(db.Decks.name == "Korean::Top 100 Verbs")
# top_verbs_notes = db.Notes.select(db.Notes, db.Models) \
#                     .switch(db.Notes) \
#                     .join(db.Models, on=(db.Models.id == db.Notes.mid)) \
#                     .where(db.Models.name == "Basic (and reversed card)-3d88a") \
#                     .limit(10).offset(10)
# 
# for note in top_verbs_notes:
#     print(note.sfld, ":")
#     duplicates = db.Notes.select(db.Notes, db.Models) \
#                    .switch(db.Notes) \
#                    .join(db.Models, on=(db.Models.id == db.Notes.mid)) \
#                    .where(db.Notes.sfld == note.sfld)
#     for dnote in duplicates:
#         print("   -", dnote.model.name, "-", dnote.flds[0])


top_words = db.Notes.select(db.Notes, db.Models) \
                     .switch(db.Notes) \
                     .join(db.Models, on=(db.Models.id == db.Notes.mid)) \
                     .where(db.Models.name == "Top-Words")

dedup_notes = {}
for note in top_words:
    if note.sfld in dedup_notes:
        dedup_notes[note.sfld][int(note.flds[1])] = note
    else:
        dedup_notes[note.sfld] = {int(note.flds[1]) : note}


for (idx, notes) in dedup_notes.items():
    if len(notes) > 1:
        print(idx, ":")
        priorities = list(notes.keys())
        priorities.sort()
        low_p = priorities[0]
        to_keep = notes.get(low_p)
        del notes[low_p]
        print("   - to_keep:", low_p, to_keep.sfld, to_keep.flds, to_keep.tags)
        
        priority_list = [to_keep.flds[1]]
        audio_list = [to_keep.flds[2]]
        tag_list = set(to_keep.tags)
        for (priority, note) in notes.items():
            print("   - to_trash:", note.sfld, note.flds, note.tags)
            priority_list.append(note.flds[1])
            audio_list.append(note.flds[2])
            tag_list |= set(note.tags)

        priority_list.sort()
        to_keep.fields["No"] = " ".join(priority_list)
        to_keep.fields["Audio"] = " ".join(audio_list)
        to_keep.tags = list(
            (tag_list - set(["duplicate", "1000common"])) | set(["Top::1000CommonWords"]))
        to_keep.save()
        print("   ** updated to_keep:", to_keep.sfld, to_keep.flds, to_keep.tags)
        



