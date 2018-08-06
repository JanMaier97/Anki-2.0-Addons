# -*- coding: utf-8 -*-
from aqt import mw
from aqt.qt import *
from aqt.utils import showInfo
from anki.hooks import addHook, wrap, runHook
from kanjiExtractor import KanjiExtractor
from kanjiReset import KanjiReset
import aqt, os


class SettingsDialog(QDialog):
    def __init__(self):
        QDialog.__init__(self, mw)

        self.kanjiFieldKeys = ["Kanji", "OnYomi", "KunYomi", "KMeaning", "ExampleWords", "ExampleWordsMeaning", "Radical", "StrokeNumber"]
        self.vocabFieldKeys = ["Expression", "Reading", "VMeaning"]
        self.vocabNote = {
            "VModel": None,
            "Expression": None,
            "Reading": None,
            "VMeaning": None
            }
        
        self.kanjiNote = {
            "Deck": None,    
            "KModel": None,
            "Kanji": None,
            "OnYomi": None,
            "KunYomi": None,
            "KMeaning": None,
            "ExampleWords": None,
            "ExampleWordsMeaning": None,
            "Radical": None,
            "StrokeNumber" : None
            }

        self.Tags = {
                "jlptTag": None,
                "gradeTag": None,
                "moreTags": None,
                }
        
        # load settings from file
        with open(os.path.join(mw.pm.addonFolder(), 'extractor_base/config.txt'), 'r') as f:
            for line in f:
                line = line.replace("\n", "")
                line = line.split(" ", 1)
                for key in self.vocabNote:
                    if line[0] == key:
                        self.vocabNote[key] = line[1]
                        continue
                for key in self.kanjiNote:
                    if line[0] == key:
                        self.kanjiNote[key] = line[1]
                        continue
                for key in self.Tags:
                   if line[0] == key:
                       self.Tags[key] = line[1]
                       continue
                    
        # variables
        self.allModels = mw.col.models.all()
        self.ModelFields = []
        self.pauseUpdate = False        
        
        # widgets, which are needed later
        # tab for vocabulary settings
        self.vocabTab = QWidget()
        self.vocabModelCombo = QComboBox()
        self.vocabFieldCombo = QComboBox()
        

        # tab for kanji settings
        self.kanjiTab = QWidget()       
        self.kanjiModelCombo = QComboBox()
        self.kanjiDeckCombo = QComboBox()
        self.kanjiFieldCombos = []

        #tab for tags
        self.tagTab = QWidget()
        self.levelTagBox = QCheckBox("JLPT Level")
        self.gradeTagBox = QCheckBox("Kanji Grade")
        self.moreTags = QLineEdit()

        if self.Tags["jlptTag"] == "1":
            self.levelTagBox.setChecked(True)
        if self.Tags["gradeTag"] == "1":
            self.gradeTagBox.setChecked(True)
        self.moreTags.setText(self.Tags["moreTags"])    
        
        self.setVocabTab()
        self.setKanjiTab()
        self.setTagTab()
        self.setup()
        

    def setup(self):
        # layout of the dialog window
        tabLayout = QTabWidget()
        tabLayout.addTab(self.vocabTab, "Vocabulary")
        tabLayout.addTab(self.kanjiTab, "Kanji")
        tabLayout.addTab(self.tagTab, "Tags")
        
        # apply and close button
        applyButton = QPushButton("Apply")
        cancelButton = QPushButton("Cancel")
        
        self.connect(applyButton, SIGNAL("clicked()"), self.onApply)
        self.connect(cancelButton, SIGNAL("clicked()"), self.close)
        
        # add buttons to horizontal box
        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(applyButton)
        hbox.addWidget(cancelButton)
        
        # add horizontalbox to vertical box
        vbox = QVBoxLayout()
        vbox.addWidget(tabLayout)
        vbox.addLayout(hbox)
        
        # set the layout of the dialog window
        self.setLayout(vbox)
        self.setWindowTitle("Kanj Extractor Settings")
        self.show()


    def setVocabTab(self):
        # combobox for the vocab model, add times, select saved model and connect to function
        self.vocabModelCombo.addItems([model['name'] for model in self.allModels] + [_("Nothing")])
        self.vocabModelCombo.setCurrentIndex(self.vocabModelCombo.findText(self.vocabNote["VModel"]))
        self.connect(self.vocabModelCombo, SIGNAL("activated(int)"), self.onVocabModelChanged)

        grid = self.buildGrid(self.vocabModelCombo, "vocab")

        # create the layout for the tab
        vBoxlayout = QVBoxLayout()
        vBoxlayout.addWidget(QLabel("Select the card model for the japanese vocabulary"))
        vBoxlayout.addWidget(self.vocabModelCombo)
        vBoxlayout.addLayout(grid)
        vBoxlayout.addStretch(1)
        self.vocabTab.setLayout(vBoxlayout)
        

    def setKanjiTab(self):
        # select the model for the kanji cards and connect the combobox with a signal, which changes the selectable fields        
        self.kanjiModelCombo.addItems([model['name'] for model in self.allModels])
        self.kanjiModelCombo.setCurrentIndex(self.kanjiModelCombo.findText(self.kanjiNote["KModel"]))
        self.connect(self.kanjiModelCombo, SIGNAL("activated(int)"), self.onKanjiModelChanged)

        self.kanjiDeckCombo.addItems(mw.col.decks.allNames())
        self.kanjiDeckCombo.setCurrentIndex(self.kanjiDeckCombo.findText(self.kanjiNote["Deck"]))

        # create grid layout
        grid = self.buildGrid(self.kanjiModelCombo, "kanji")

        # set layout for the Tab
        vBoxlayout = QVBoxLayout()
        vBoxlayout.addWidget(QLabel("Select deck for the kanji cards"))
        vBoxlayout.addWidget(self.kanjiDeckCombo)
        vBoxlayout.addWidget(QLabel("Select model for the kanji cards"))
        vBoxlayout.addWidget(self.kanjiModelCombo)
        vBoxlayout.addWidget(QLabel("Select the fields"))
        vBoxlayout.addLayout(grid)
        self.kanjiTab.setLayout(vBoxlayout)


    def setTagTab(self):
        vBoxLayout = QVBoxLayout()
        vBoxLayout.addWidget(QLabel("Select tags"))
        vBoxLayout.addWidget(self.levelTagBox)
        vBoxLayout.addWidget(self.gradeTagBox)
        vBoxLayout.addWidget(QLabel("Additional Tags:"))
        vBoxLayout.addWidget(self.moreTags)        
        vBoxLayout.addStretch(1)
        self.tagTab.setLayout(vBoxLayout)


    # creates the grid layout in the vocabulary and kanji tab
    # key is either "kanji" or "vocab"
    # if rebuild is true, all FieldCombos are cleared and new items are added
    def buildGrid(self, modelCombo, key, rebuild = False):
        targets =  [_("Nothing")]
        if modelCombo.currentText() != _("Nothing"):
            targets = [ x['name'] for x in self.allModels[modelCombo.currentIndex()]["flds"]] + [_("Nothing")]

        indices = {}

        if not rebuild:
            combos = []
            grid = QGridLayout()
            for i, fieldName in enumerate(getattr(self, key + "FieldKeys")):
                grid.addWidget(QLabel(fieldName), i, 0)
                cb = QComboBox()                
                cb.addItems(targets)
                cb.setCurrentIndex(cb.findText(getattr(self, key + "Note")[fieldName]))               
                indices[cb] = cb.currentIndex()
                self.connect(cb, SIGNAL("currentIndexChanged(int)"), lambda i, cb=cb, key=key: self.onComboChanged(i, cb, key))
                grid.addWidget(cb, i, 1)
                combos.append(cb)

            setattr(self, key+"FieldCombos", combos)
            setattr(self, key+"indices", indices)
            return grid

        if rebuild:
            
            combos = getattr(self, key+"FieldCombos")
            for i, cb  in enumerate(combos):
                
                cb = combos[i]
                cb.clear()
                cb.addItems(targets)
                idx = min(i,len(targets)-1)
                cb.setCurrentIndex(idx)
                indices[cb] = idx
            setattr(self, key+"indices", indices)
        
        
    def onVocabModelChanged(self):
        self.pauseUpdate = True
        self.buildGrid(self.vocabModelCombo, "vocab", True)
        self.pauseUpdate = False
        

    def onKanjiModelChanged(self):
        self.pauseUpdate = True
        self.buildGrid(self.kanjiModelCombo, "kanji", True)
        self.pauseUpdate = False

        
    def onComboChanged(self, i, cb, key):
        # i is not needed here, but if i is not a parameter, cb will become an interger, not a QCombobox object
        if self.pauseUpdate:
            return
        
        indices = getattr(self, key+"indices")          
        combos = getattr(self, key+"FieldCombos")
        
        for c in combos:
            if c == cb:
                continue
            if c.currentText() == _("Nothing"):
                continue
            if c.currentIndex() == cb.currentIndex():
                self.pauseUpdate = True
                c.setCurrentIndex(indices[cb])
                self.pauseUpdate = False
                break
        indices[cb] = cb.currentIndex()
                

    def onApply(self):
        # write file with all current selected models and fields
        with open(os.path.join(mw.pm.addonFolder(), 'extractor_base/config.txt'), 'w') as f:
            f.write("{0} {1}{2}".format("VModel", self.vocabModelCombo.currentText(), "\n"))
            for i, field in enumerate(self.vocabFieldKeys):
                f.write("{0} {1}{2}".format(field, self.vocabFieldCombos[i].currentText(), "\n"))
            f.write("{0} {1}{2}".format("KModel", self.kanjiModelCombo.currentText(), "\n"))
            f.write("{0} {1}{2}".format("Deck", self.kanjiDeckCombo.currentText(), "\n"))
            for i, field in enumerate(self.kanjiFieldKeys):
                f.write("{0} {1}{2}".format(field, self.kanjiFieldCombos[i].currentText(), "\n"))
            if self.levelTagBox.isChecked():
                f.write("{0} {1}{2}".format("jlptTag", "1", "\n"))
            else:
                f.write("{0} {1}{2}".format("jlptTag", "0", "\n"))
            if self.levelTagBox.isChecked():
                f.write("{0} {1}{2}".format("gradeTag", "1", "\n"))
            else:
                f.write("{0} {1}{2}".format("gradeTag", "0", "\n"))
            f.write("{0} {1}{2}".format("moreTags", self.moreTags.text(), "\n"))

            
        f.close()
        self.close()


def createKanjiCards():
    ke = KanjiExtractor()       
    ke.startCreation()
    

def setupBrowserMenu(browser):
    """ set up the button in the browser """
    a = QAction("Bulk-add Kanji-Cards", browser)
    browser.connect(a, SIGNAL("triggered()"), lambda e=browser: onRegenerate(e))
    browser.form.menuEdit.addSeparator()
    browser.form.menuEdit.addAction(a)


def onRegenerate(browser):
    ke = KanjiExtractor()
    ke.addCardsBulk(browser.selectedNotes())


def initDialog():
    mw.dialog = SettingsDialog()

def startReset():
    r = KanjiReset()
    r.Reset()

def createMenu():
    ml = QMenu()
    ml.setTitle("Kanji Extractor")
    mw.form.menuTools.addAction(ml.menuAction())
    mw.form.menuLookup = ml

    a = QAction(mw)
    a.setText("create kanji cards")
    ml.addAction(a)
    mw.connect(a, SIGNAL("triggered()"), createKanjiCards)

    a = QAction(mw)
    a.setText("Settings")
    ml.addAction(a)
    mw.connect(a, SIGNAL("triggered()"), initDialog)

    a = QAction(mw)
    a.setText("Reset")
    ml.addAction(a)
    mw.connect(a, SIGNAL("triggered()"), startReset)

createMenu()
addHook("browser.setupMenus", setupBrowserMenu)

