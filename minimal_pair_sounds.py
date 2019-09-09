#! /home/eve/Documents/Linguistique/coréen/anki-prog/bin/python

import bleach
import html
import re
import json
from ankisync2.anki import Apkg, db
from os.path import dirname, join
import shutil
from itertools import permutations


apkg = Apkg("tmp-dir/Korean_Minimal_Pair_Sounds.apkg")
note2_dump_filename = "tmp-dir/minimal_pair-2.json"
note3_dump_filename = "tmp-dir/minimal_pair-3.json"
sound_dir = "tmp-dir/minimal_pair_media/"
sound_dir = "/home/eve/Documents/Linguistique/coréen/anki-python-files/tmp-dir/minimal_pair_media/"

deck = db.Decks.get(db.Decks.name == "Korean Minimal Pair Sounds")
model = db.Models.get(db.Models.name == 'Minimal-Pair-Sound')
model.fix_sfld_key()
# print(model.name)
templates = db.Templates.select().where(db.Templates.mid == model)


# model.name: 'Basic'
# Front: "Do you hear&nbsp;겁, 껍, or 컵?<div><br></div><div>[sound:겁.mp3]</div>"
# Back: "You heard 겁."
# other Front: "Do you hear 서 or 써?<div><br /></div><div>[sound:써.mp3]</div>"

# model.name: 'Minimal-Pair-Sound'
# * PS-Key
# * Audio
# * PS-Choices
# * PS-Answer

notes = {}
cats = []
media = []

dedup_choices = []
bad_sounds = [
    ["도", "또", "토"], ["배", "빼", "패"], 
    ["벼", "뼈", "펴"], ["발", "빨", "팔"],
    ["불", "뿔", "풀"]]

pattern_front = re.compile(r"""
            Do\ you\ hear(?:\&nbsp;|\ )(?P<c1>[^,]+)(?:,\ (?P<c3>.+),)?\ or\ (?P<c2>.+)\?
            .*sound:(?P<audio>.*)\].*
        """, re.X)
pattern_back = re.compile(r"You heard (.+)\.")
for note in db.Notes.select(db.Notes, db.Models) \
                .switch(db.Notes) \
                .join(db.Models, on=(db.Models.id == db.Notes.mid)) \
                .filter(db.Models.name == 'Basic'):
    audio = ''
    choices = []
    answer = ''

    front = note.flds[0]
    matches = pattern_front.match(front)
    if matches:
        res = matches.groupdict()
        audio = res['audio']
        choices = [res['c1'], res['c2']]
        if 'c3' in res and res['c3']:
            choices.append(res['c3'])
        choices.sort()
    else:
        print('No front match?')

    back = note.flds[1]
    matches = pattern_back.match(back)
    if matches:
        answer = matches.group(1)
        if audio != answer + '.mp3':
            print('Inconsistency!! answer:', answer, '- audio:', audio)
        elif answer not in choices:
            print('Inconsistency!! answer:', answer, '- choices:', choices)
    else:
        print('No back match?')
    
    key_start = '-'.join(choices)
    if key_start in dedup_choices:
        continue
    dedup_choices.append(key_start)

    # print('Choices:', choices, '- Audio:', audio, '- Answer:', answer)
    if len(choices) == 2:
        # * PS-Key
        # * Audio
        # * PS-Choices
        # * PS-Answer
        perms = list(map(lambda x: (x, "dif_1.1"), list(permutations(choices))))
        # we need to concat thoses sound files
        for (perm, _) in perms:
            audio_sources = " ".join(tuple(map(lambda x: x + ".mp3", perm)))
            audio = "-".join(perm) + ".mp3"
            command_line = "cat " + audio_sources + " > " + audio
            cats.append(command_line)
        # We also need the notes for unique sounds 
        perms.extend(list(map(lambda x: (x, "dif_2.1"), choices)))
        # Now we create the data for notes
        for (perm, dif) in perms:
            idx_perm = "-".join(perm)
            audio = idx_perm + ".mp3"
            key = key_start + "_" + idx_perm
            notes[key] = {
                "audio": "[sound:" + audio + "]",
                "choices": " ".join(choices),
                "answer": " ".join(perm),
                "tags": ["PairSounds::" + dif]}
            media.append(audio)
    elif len(choices) == 3 and choices not in bad_sounds:
        perms = list(map(lambda x: (x, "dif_1.2"), list(permutations(choices))))
        perms.extend(list(map(lambda x: (x, "dif_2.2"), list(permutations(choices, 2)))))
        # we need to concat thoses sound files
        for (perm, _) in perms:
            audio_sources = " ".join(tuple(map(lambda x: x + ".mp3", perm)))
            audio = "-".join(perm) + ".mp3"
            command_line = "cat " + audio_sources + " > " + audio
            cats.append(command_line)
        # We also need the notes for unique sounds 
        perms.extend(list(map(lambda x: (x, "dif_3"), choices)))
        # Now we create the data for notes
        for (perm, dif) in perms:
            idx_perm = "-".join(perm)
            audio = idx_perm + ".mp3"
            key = key_start + "_" + idx_perm
            notes[key] = {
                "audio": "[sound:" + audio + "]",
                "choices": " ".join(choices),
                "answer": " ".join(perm),
                "tags": ["PairSounds::" + dif]}
            media.append(audio)
    elif choices in bad_sounds:
        # print("bad sounds:", choices)
        pass

# print(" ; ".join(cats))


for key, note in notes.items():
    print(key, ":", note["answer"], note["tags"])
    new_note = db.Notes.create(
        mid=model.id,
        fields={
            "PS-Key": key,
            "Audio": note["audio"],
            "PS-Choices": note["choices"],
            "PS-Answer": note["answer"]},
        tags=note['tags'])
    print(new_note.tags)
    for i, _ in enumerate(templates):
        db.Cards.create(nid=new_note.id, did=deck.id, ord=i)

media_dir = dirname(apkg.media_path)
# for media in apkg.iter_media():
#     media_source = join(media_dir, media['path'])
#     media_target = join(sound_dir, media['name'])
#     # print(media_source, media_target)
#     # shutil.copyfile(media_source, media_target, follow_symlinks=False)

for audio in media:
    audio_location = join(sound_dir, audio)
    # print(audio_location)
    apkg.add_media(audio_location)

#for media in apkg.iter_media():
    # print(media)
    # shutil.copyfile(media_source, media_target, follow_symlinks=False)

apkg.zip(output="tmp-dir/updated-deck.apkg")
apkg.close()
