#! /home/eve/Documents/Linguistique/coréen/anki-prog/bin/python


# from ankisync2.anki import Anki2, Apkg
from ankisync2.anki import Apkg, db
import ipdb


apkg = Apkg("tmp3/Korean_Retro_Sentences.apkg")
iter_apkg = iter(apkg)
for i in range(5):
    print(next(iter_apkg))
apkg.zip(output="example1.apkg")
apkg.close()
