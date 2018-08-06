# -*- coding: utf-8 -*-
from aqt import mw
from aqt.qt import *
from anki.hooks import addHook
from aqt.utils import showInfo

KANJI_MODEL = 'Kanji'
KANJI_FIELD = 'KanjiField'

VOCAB_MODEL = 'JapaneseVocabulary'
VOCAB_FIELD = 'Expression'

def isKanji(char):
    """ return true if char is a kanji or false if not """
    code = ord(char)
    return 0x4E00 <= code <= 0x9FFF


def hasKanji(word):
    for char in list(word):
        if isKanji(char):
            return True


def findNewKanji():
    """
    finds all new Kanji and puts them in a list
    """
    kanjiList = []
    newNIDs = mw.col.findNotes("is:new")
    
    for nid in newNIDs:
        note = mw.col.getNote(nid)
        if note.model()['name'] == KANJI_MODEL:
            kanjiList.append(note[KANJI_FIELD])
    return kanjiList


def findVocab():
    """
    finds all vocabulary note ids containing kanji
    """
    nids = mw.col.models.nids(mw.col.models.byName(VOCAB_MODEL))
    vocabIDs = []
    
    for nid in nids:
        if hasKanji(mw.col.getNote(nid)[VOCAB_FIELD]):
            vocabIDs.append(nid)
    return vocabIDs


def findSuspendable():
    """
    returns all cids of vocabulary notes, which should be suspended
    """
    kanjiList = findNewKanji()
    vIDs = findVocab()

    nids = []
    for kanji in kanjiList:        
        for vID in vIDs:
            if kanji in list(mw.col.getNote(vID)[VOCAB_FIELD]):
                if vID not in nids:
                    nids.append(vID)                    
    cids = []
    for nid in nids:
        for card in mw.col.getNote(nid).cards():
            cids.append(card.id)
    return cids

def findUnsuspendable():
    """
    retruns all cids of vocabulary notes, which shoulb be unsupended
    """
    kanjiList = findNewKanji()
    suspendedIDs = mw.col.findNotes("is:suspended")
    nids = []
    
    for nid in suspendedIDs:
        if mw.col.getNote(nid).model()['name'] == VOCAB_MODEL:
            for char in list(mw.col.getNote(nid)[VOCAB_FIELD]):
                if char not in kanjiList:                    
                    nids.append(nid)
                    

    cids = []
    for nid in nids:
        for card in mw.col.getNote(nid).cards():
            cids.append(card.id)

    return cids

def Suspending():
    mw.col.sched.unsuspendCards(findUnsuspendable())
    mw.col.sched.suspendCards(findSuspendable())
    mw.reset
    

def setupButton():
    action = QAction("Unlock Vocab", mw)
    mw.connect(action, SIGNAL("triggered()"), Suspending)
    mw.form.menuTools.addAction(action)

setupButton()
addHook("reviewCleanup", Suspending)

"""
The MIT License (MIT)

Copyright (c) 2016 Predator2610

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
