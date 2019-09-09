#! /home/eve/Documents/Linguistique/coréen/anki-prog/bin/python

import bleach
import html
from ankisync2.anki import Apkg, db


apkg = Apkg("tmp-dir/Korean_Retro_Sentences.apkg")

# iter_apkg = iter(apkg)
# n0 = n1 = n2 = n3 = 1
# for card in iter_apkg:
#     splited = card['note']['flds'][2].split('-')
#     n0 = max(n0, int(splited[0]))
#     n1 = max(n1, int(splited[1]))
#     n2 = max(n2, int(splited[2]))
#     n3 = max(n3, int(splited[3]))

# last_n0 = last_n1 = '0'
# t0 = t1 = 0
# for note in db.Notes.select(db.Notes, db.Models) \
#                 .switch(db.Cards) \
#                 .join(db.Models, on=(db.Models.id == db.Notes.mid)) \
#                 .order_by(db.Notes.sfld.asc()):
#     spl = note.flds[2].split('-')
#     new_sort_values = [
#         spl[0].rjust(2, '0'),
#         spl[1].rjust(2, '0'),
#         spl[2].rjust(3, '0'),
#         spl[3]
#     ]
#     note.fields['Sort'] = "-".join(new_sort_values)
# 
#     if spl[0] != last_n0:
#         t0 += 1
#         t1 = 1
#     elif spl[1] != last_n1:
#         t1 += 1
#     last_n0 = spl[0]
#     last_n1 = spl[1]
# 
#     t0_str = str(t0)
#     t1_str = str(t1)
#     tag = '::'.join([
#         'Retro_Sentences',
#         t0_str.rjust(2, '0'),
#         t1_str.rjust(2, '0')])
#     note.tags.append(tag)
# 
#     note.save()
#     print(note.tags)

# 01-02-015-1

for note in db.Notes.select(db.Notes, db.Models) \
                .switch(db.Notes) \
                .join(db.Models, on=(db.Models.id == db.Notes.mid)):

    note.fields['Formatted Korean'] = note.flds[0]
    
    note.fields['Target Language'] = 'En'

    better_text = bleach.clean(note.flds[0], tags=[], strip=True, strip_comments=True)
    better_text = html.unescape(better_text)
    note.fields['Korean'] = better_text.strip()

    better_audio = bleach.clean(note.flds[2], tags=[], strip=True, strip_comments=True)
    better_audio = html.unescape(better_audio)
    better_image = note.flds[2].replace(better_audio, '')
    better_image = html.unescape(better_image)
    note.fields['Audio'] = better_audio.strip()
    note.fields['Image'] = better_image.strip()

    note.save()

apkg.zip(output="example1.apkg")
apkg.close()
