# VocabUnlocker
VocabUnlocker is an Anki addon, which "unlocks" new japanese vocabulary by suspending and unsuspending notes, if you have learned the kanji of this word.

Setup:
1. Download the files and put only the VocabUnlocker.py files into the addon folder of Anki, which is normally located at "documents\Anki\addons"

2. Now open the file with the editor of your choise. In line 7 change the value of KANJI_MODEL to the model for your cards, you use for kanji. For KANJI_FIELD enter the field name, which contains only the kanji. Do the same for the vocabulary model and the field.

3. Now restart Anki and a new button "Unlock Vocab" should have appeared in the tools menu. With this button you can manually unlock the vocabulary, but normaly this is done after everytime you finish a deck.
