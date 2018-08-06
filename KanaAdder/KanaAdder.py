from PyQt4 import QtGui, QtCore
from aqt import mw
from anki.hooks import addHook, wrap
from aqt.qt import *
from aqt.addcards import AddCards

READING_FIELD = 'Reading'
KANA_FIELD = 'Kana'
VOCAB_MODEL = 'JapaneseThreeWayVocab'

def isKanji(char):
    """ return true if char is a kanji or false if not """
    code = ord(char)
    return 0x4E00 <= code <= 0x9FFF

def getKana(note):
    kana = note[READING_FIELD]
    hasKanji = False
    for char in kana:
        if char == '[' or char == ']' or char == ' ' or isKanji(char):
            kana = kana.replace(char, "")

        if isKanji(char):
            hasKanji = True
            
    if hasKanji:
        return kana
    else:
        return ''

def addCardsBulk(nids):
    """ bulk add kanji notes from selected cards """
    mw.checkpoint("Bulk-add Kanji")
    mw.progress.start()

    for nid in nids:
        note = mw.col.getNote(nid)
        note[KANA_FIELD] = getKana(note)
        note.flush()
    
    mw.progress.finish()
    mw.reset()

def setupBrowserMenu(browser):
    """ set up the button in the browser """
    a = QAction("Bulk make Kana", browser)
    browser.connect(a, SIGNAL("triggered()"), lambda e=browser: onRegenerate(e))
    browser.form.menuEdit.addSeparator()
    browser.form.menuEdit.addAction(a)

def onRegenerate(browser):
    addCardsBulk(browser.selectedNotes())

def onAddCards(self):
    note = mw.col.getNote(self.history[0][0])
    if note.model()['name'] == VOCAB_MODEL:
        note[KANA_FIELD] = getKana(note)
        note.flush()        
        
#Main-----------------------------------------------------------------------
addHook("browser.setupMenus", setupBrowserMenu)
AddCards.addCards = wrap(AddCards.addCards, onAddCards)
