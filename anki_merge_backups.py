#! /home/eve/Documents/coréen/prog/anki-venv/bin/python

from ankisync2.anki import Apkg, db

"""
Not sure this works, this file wasn't commited
"""

apkg_primary = Apkg("tmp-dir/All Decks-20200727-Primary_deck.apkg")
apkg_secondary = Apkg("tmp-dir/All Decks-20200722-Save_before_import.apkg")
output_filename = "tmp-dir/updated-decks.apkg"

main_deck_name = "Default"
main_note_type = "Ko + Translation + Dictation (opt)"
models_fields = {
    "Ko + Translation + Dictation (opt)": {
        0: ('Korean', None),
        1: ('Formatted Korean', '<br>'),
        2: ('Translation', '<br>'),
        3: ('Alternative Translation', '<br>'),
        4: ('Formatted Translation', '<br>'),
        5: ('Audio', ' '),
        6: ('Image', '<br>'),
        7: ('Dictation', ' '),
        8: ('Dictation Hint', ' '),
        9: ('Hanja', '<br>'),
        10: ('Notes', '<br>'),
        11: ('Priority', ' '),
        12: ('Source', '<br>'),
        13: ('Target Language', ' '),
    },
    "Retro-Mango-Idioms-Treasury": {
        0: ('Korean', None),
        1: ('Formatted Korean', '<br>'),
        2: ('Translation', '<br>'),
        3: ('Formatted Translation', '<br>'),
        4: ('Audio', ' '),
        5: ('Image', '<br>'),
        6: ('Notes', '<br>'),
        7: ('Priority', ' '),
        8: ('Source', '<br>'),
        9: ('Target Language', ' '),
    }
}
models_names = list(models_fields.keys())
models = db.Models.select().where(db.Models.name.in_(models_names))
for model in models:
    model.fix_sfld_key()

all_cards = db.Cards.select(db.Cards, db.Decks, db.Notes, db.Models) \
                     .join(db.Decks, on=(db.Decks.id == db.Cards.did)) \
                     .join(db.Notes, on=(db.Notes.id == db.Cards.nid)) \
                     .switch(db.Notes) \
                     .join(db.Models, on=(db.Models.id == db.Notes.mid)) \
                     .where(db.Models.name.in_(models_names))


class MergeException(Exception):
    pass


def add_to_notes(card, deck_notes):
    sfld = card.note.sfld
    note_id = card.note.id
    if sfld in deck_notes:
        if note_id in deck_notes[sfld]:
            deck_notes[sfld][note_id].append(card)
        else:
            deck_notes[sfld][note_id] = [card]
    else:
        deck_notes[sfld] = {note_id: [card]}

def fill_note_fields(note, note_fields):
    if note.model.name not in models_fields:
        raise MergeException("Model error: " + note.model.name)
    for (idx, (field_name, _)) in models_fields[note.model.name].items():
        if not(len(note.flds) > idx):
            msg = "Field error: {name}, {idx}, {note_flds}".format(
                name=field_name, idx=idx, note_flds=note.flds)
            raise MergeException(msg)
        if field_name not in note_fields:
            note_fields[field_name] = set()
        # maybe we should split note.flds[idx] using the separator
        note_fields[field_name] |= set([note.flds[idx]])

def clean_note_fields(note_fields):
    for (field_name, fields) in note_fields.items():
        fields -= set([""])

def update_note_fields(note, note_fields):
    if note.model.name not in models_fields:
        raise MergeException("Model error: " + note.model.name)
    for (idx, (field_name, sep)) in models_fields[note.model.name].items():
        if field_name not in note_fields:
            msg = "Missing field: {name}, {note_id}".format(
                name=field_name, note_id=note.id)
            raise MergeException(msg)
        if sep:
            note.fields[field_name] = sep.join(list(note_fields[field_name]))

def merge_notes(to_keep, to_delete):
    note = to_keep[0].note
    note_fields = {}
    fill_note_fields(note, note_fields)
    tags = set(note.tags)
    exec_log = "# to_update: {sfld}, {note_id}, {fields}, {tags} -~- ".format(
        sfld=note.sfld, note_id=note.id, fields=str(note_fields), tags=str(tags))
    for cards in to_delete.values():
        d_note = cards[0].note
        fill_note_fields(d_note, note_fields)
        d_note_tags = set(d_note.tags) - set(["duplicate"]) - set("")
        tags |= d_note_tags
        d_note_tags |= set(["to_delete"])
        d_note.tags = list(d_note_tags)
        d_note.save()
        to_trash_log = "-- to_trash: {note_id}, {fields}, {tags} ".format(
            note_id=d_note.id, fields=str(d_note.flds), tags=str(d_note.tags))
        exec_log += to_trash_log

    clean_note_fields(note_fields)
    tags -= set(["duplicate"])
    tags |= set(["to_review"])
    update_note_fields(note, note_fields)
    note.tags = list(tags)
    note.save()
    updated_log = "-~- after update: {fields}, {tags}".format(
        fields=str(note.flds), tags=str(note.tags))
    exec_log += updated_log
    print(exec_log)


main_deck_notes = {}
other_decks_notes = {}
for card in all_cards:
    sfld = card.note.sfld
    if not sfld:
        # the "Korean" field is not set, let's ignore those notes
        continue
    note_id = card.note.id
    if card.deck.name == main_deck_name:
        add_to_notes(card, main_deck_notes)
    else:
        add_to_notes(card, other_decks_notes)


for (sfld, notes) in main_deck_notes.items():
    if len(notes) == 1:
        (note_id, cards) = notes.popitem()
        if sfld not in other_decks_notes:
            # maybe a few cards, but only one note
            # and every cards are in the main deck
            note = cards[0].note
            print("* unchanged:", note.sfld, note.id, note.flds, note.tags)
        else:
            if note_id in other_decks_notes[sfld]:
                # cards for the same notes in other decks, let's clean this!
                other_cards = other_decks_notes[sfld].pop(note_id)
                for card in other_cards:
                    card.deck.name = main_deck_name
                    card.save()
                    cards.append(card)
                print("-- card moved:", note.sfld, note.id, card.id)
            if other_decks_notes[sfld] == {}:
                del(other_decks_notes[sfld])
                note = cards[0].note
                print("* unchanged note:", note.sfld, note.id, note.flds, note.tags)
            else:
                merge_notes(cards, other_decks_notes[sfld])
                del(other_decks_notes[sfld])
    else:
        # if only one of the note has due cards, merge everything into that note
        notes_with_due = {}
        notes_without_due = {}
        for (note_id, cards) in notes.items():
            for card in cards:
                if card.due > 0:
                    add_to_notes(card, notes_with_due)
                else:
                    add_to_notes(card, notes_without_due)
        if len(notes_with_due[sfld]) > 1:
            raise MergeException("!!! multiple notes with due cards -->" + sfld + "<--")
        else:
            other_notes = notes_without_due[sfld]
            if note_id in other_decks_notes[sfld]:
                other_notes.update(other_decks_notes[sfld])
                del(other_decks_notes[sfld])
            merge_notes(notes_with_due[sfld], other_notes)

print("----------------- Other decks ---------------")

for (sfld, notes) in other_decks_notes.items():
    if len(notes) == 1:
        (note_id, cards) = notes.popitem()
        note = cards[0].note
        print("* unchanged, not in main:", note.sfld, note.id, note.flds, note.tags)
    else:
        # notes with type "Retro-Mango-Idioms-Treasury" can be merged into 
        # type "Ko + Translation + Dictation (opt)" notes, but not the other way around
        to_keep_id = None
        for (note_id, cards) in notes.items():
            if cards[0].note.model.name == main_note_type:
                to_keep_id = note_id
                break
        if to_keep_id:
            cards = notes.pop(to_keep_id)
        else:
            (_, cards) = notes.popitem()
        merge_notes(cards, notes)



apkg.zip(output=output_filename)
apkg.close()
