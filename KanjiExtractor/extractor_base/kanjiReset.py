from kanjiExtractor import KanjiExtractor
from PyQt4 import QtGui, QtCore
from aqt import mw
from aqt.qt import *
from aqt.addcards import AddCards
from anki.hooks import addHook, wrap, runHook
from aqt.utils import showInfo
import codecs
import os
import xml.etree.ElementTree

class KanjiReset(KanjiExtractor):
    def __init__(self):
        super(KanjiReset, self).__init__() 
        self.Fields = {
                "OnYomi": False,
                "KunYomi": False,
                "KMeaning": False,
                "ExampleWords": False,
                "ExampleWordsMeaning": False,
                "Radical": False, 
                "StrokeNumber" : False
            }

    def Reset(self):
        model = mw.col.models.byName(self.kanjiNote["KModel"])
        nids = mw.col.models.nids(model)

        mw.checkpoint("Bulk-add Kanji")
        mw.progress.start()

        tree = xml.etree.ElementTree.parse(os.path.join(mw.pm.addonFolder(), 'extractor_base/kanjidic2.xml'))
        self.root = tree.getroot()

        for nid in nids:
            note = mw.col.getNote(nid)
            note = self.updateFields(note, self.getInfo(note[self.kanjiNote['Kanji']]))
            note.flush()
        mw.progress.finish()
        mw.reset()


    def updateFields(self, note, info):
        if self.Fields["OnYomi"]:
            note[self.kanjiNote['OnYomi']] = info['onYomi']

        if self.Fields["KunYomi"]:
            note[self.kanjiNote['KunYomi']] = info['meanings']

        if self.Fields["KMeaning"]:
            note[self.kanjiNote['KMeaning']] = info['radical']

        if self.Fields["Radical"]:
            note[self.kanjiNote['Radical']] = info['radical']

        if self.Fields["StrokeNumber"]:
            note[self.kanjiNote['StrokeNumber']] = info['strokeNumber']

        if self.Fields["ExampleWords"] or self.Fields["ExampleWords"]:
            s1, s2 = self.findExamples(note[self.kanjiNote['Kanji']])
            
            if self.Fields["ExampleWords"]:
                note[self.kanjiNote['ExampleWords']] = s2

            if self.Fields["ExampleWordsMeaning"]:
                note[self.kanjiNote['ExampleWordsMeaning']] = s1

        return note
