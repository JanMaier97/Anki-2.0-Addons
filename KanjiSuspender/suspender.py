# -*- coding: utf-8 -*-
from aqt import mw
from aqt import *
from aqt.utils import showInfo


mainVocabTag = 'vocab'
otherVocabTag = 'other_vocab'
kanjiTag = 'kanji'

vocabField = 'Expression'
kanjiField = 'KanjiField'


def isKanji(char):
    return 0x4E00 <= ord(char) <= 0x9FFF

def getKanjiFromNote(nid):
    vocab = mw.col.getNote(nid)[vocabField]
    return [char for char in vocab if isKanji(char)]

def suspendCards():
    suspendingKanji = []
    keepingKanji = []

    # find all kanji in the vocabulary notes
    for nid in mw.col.findNotes('tag:' + otherVocabTag):
        suspendingKanji += getKanjiFromNote(nid) 
    
    for nid in mw.col.findNotes('tag:' + mainVocabTag):
        keepingKanji += getKanjiFromNote(nid) 

    # remove duplicates from the lists
    suspendingKanji = list(set(suspendingKanji))
    keepingKanji = list(set(keepingKanji))

    showInfo("%r sus and %r keeping kanjis have been found" % (len(suspendingKanji), len(keepingKanji)))

    # remove keepingKanji from the supsendingKaji list
    kanjiList = [kanji for kanji in suspendingKanji if kanji not in keepingKanji]
    showInfo("%r kanji notes will be suspended" % len(kanjiList))

    # find card ids and suspend cards
    cids = []
    for nid in mw.col.findNotes('tag:' + kanjiTag):
        if mw.col.getNote(nid)[kanjiField] in kanjiList:
            cids += [card.id for card in mw.col.getNote(nid).cards()]

    mw.col.sched.unsuspendCards(mw.col.findNotes('tag:'+kanjiTag))
    mw.col.sched.suspendCards(cids)



def setupButton():
    action = QAction("Suspend Kanji Cards", mw)
    mw.connect(action, SIGNAL('triggered()'), suspendCards)
    mw.form.menuTools.addAction(action)

setupButton()
