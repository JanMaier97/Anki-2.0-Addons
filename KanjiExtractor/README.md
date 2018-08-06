# KanjiExtractor
KanjiExtractor is an anki addon, which creates Kanji notes based on your vocabulary notes

0. If you don't have the addon Japanese support installed, do it now. It will be needed for example words.

1. Put the kanjiExtractorMain.py file and extractor_base folder in the folder AnkiDataFolder/addons.

2. Now download the dictionary file. This addon uses the KANJIDIC dictionary file. The file is the property of the Electionic Dicitonary Research and Development Group, and is used in conformance with the Group's licence. You can find the download on the kanjiDic2 homepage: http://www.edrdg.org/kanjidic/kanjd2index.html (look at position f).
Also see http://www.csse.monash.edu.au/~jwb/kanjidic.html , http://www.edrdg.org/ and http://www.edrdg.org/edrdg/licence.html . for more information look into the _init_.py file in the extractor_base folder.

3. Unzip the downloaded file and put the kanjidic2.xml file in the extractor_base folder.

4. Start Anki go to "Tools -> Kanji Extractor -> Settings" and select the fields in each tab as needed. You have to select at least the following:  Vocabulary: model, Expression
            Kanji:      deck, model, Kanji
Everything else can be set to "nothing".

5. Now you can create kanji notes. For this there are 2 options. For the first one simply go to "Tools -> Kanji Extractor -> create kanji cards" and new notes will be created. However the addon wil only use new vocabulary cards, cards you haven't reviewed yet. This means, that kanji of old vocabulary notes will not be added as new notes. Also, if you your PC is slow or if you have a lot of new cards you are risking that Anki stops working, because the process may take too long.
For the second option open the browser and select the vocabulary notes, which need to have the same model as you selected in the settings. Now press "Edit -> Bulk-Add Kanji-Cards" to start extracting all kanji characters.
