# -*- coding: utf-8 -*-



from PyQt4 import QtGui, QtCore
from aqt import mw
from aqt.qt import *
from aqt.addcards import AddCards
from anki.hooks import addHook, wrap, runHook
from aqt.utils import showInfo
import codecs
import os
import xml.etree.ElementTree


class KanjiExtractor(object):
    def __init__(self):
        # variables for the vocabulary notes
        self.vocabNote = {            
            "VModel": None,
            "Expression": None,
            "Reading": None,
            "VMeaning": None
            }

        # variables for the kanji notes
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

        # load settings
        with open(os.path.join(mw.pm.addonFolder(), 'extractor_base/config.txt'), 'r') as f:
    
            for line in f:
                try:
                    line = line.replace("\n", "")
                    line = line.split(" ", 1)
                    for key in self.kanjiNote:
                        if line[0] == _("Nothing"):
                            continue
                        if line[0] == key:
                            if line[1].isspace():
                                raise ValueError
                            self.kanjiNote[key] = line[1]

                    for key in self.vocabNote:
                        if line[0] == _("Nothing"):
                            continue
                        if line[0] == key:
                            if line[0].isspace():
                                raise ValueError
                            self.vocabNote[key] = line[1]

                    for key in self.Tags:
                        if line[0] == key:
                            self.Tags[key] = line[1]

                except IndexError:
                    showInfo("The key {0} of the config.txt file as no value".format(key))
                    return
                except ValueError:
                    showInfo("The key {0} of the config.txt file as no value".format(key))
                    return
            f.close()        
         
        
    def checkSettings(self):
        #check if at leat the most important fields (vocab and kanji model, kanji deck, Expression and kanji) are selected
        if not self.hasValue("Deck"):
            showInfo("You must select a deck for the kanji cards")
            return False

        if not self.hasValue("KModel"):
            showInfo("You must set a model for the kanji cards")
            return False

        if not self.hasValue("Kanji"):
            showInfo("You must select a field for the kanji")
            return False

        if not self.hasValue("VModel", "vocab"):
            showInfo("You must select a field for the model for your vocabulary cards")
            return False

        if not self.hasValue("Expression", "vocab"):
            showInfo("You must select a field for the Expression of your vocabulary notes")
            return False
        
        #ensure all other values are at least set to "nothing"
        for key, value in self.vocabNote.items():
            if key == 'VModel':
                continue

            if value == '':
                showInfo("You have to select a value for {0}".format(key))
                return False

            if value not in mw.col.models.fieldNames(mw.col.models.byName(self.vocabNote['VModel'])) and self.hasValue(key, 'vocab'):
                showInfo("The selected vocaburlary model does not have the field {0} for {1}".format(value, key))
                return False
           
        for key, value in self.kanjiNote.items():
            if key == 'KModel' or key == 'Deck':
                continue

            if value == '':
                showInfo("You must select a value for {0}".format(key))
                return False

            if value not in mw.col.models.fieldNames(mw.col.models.byName(self.kanjiNote['KModel'])) and self.hasValue(key): 
                showInfo("The selected kanji model does not have the field {0}".format(key))
                return False

            #ensure reading and meaning are set, if the user wants examples
            if key == 'ExampleWords' or key == 'ExampleWordsMeaning':
                if self.hasValue(key):
                    if not self.hasValue('Reading', 'vocab'):
                        showInfo("You need to select the reading field of the vocabulary note, if you want Japanese example Words")
                        return False

                    if not self.hasValue('VMeaning', 'vocab'):
                        showInfo("You need to select the meaning field of the vocabulary note, if you want Japanese and English example Words")
                        return False
        return True    


    def hasValue(self, key, s="kanji"):
        #checks if the value of kanji settings is something else than "nothing"
        if getattr(self, s +"Note")[key] != _("Nothing") and getattr(self, s + "Note")[key] != "":
            return True
        else:
            return False


    def addCardsBulk(self, nids):
        """ bulk add kanji notes from selected cards """
        if not self.checkSettings():
            return 

        mw.checkpoint("Bulk-add Kanji")
        mw.progress.start()    
    
        self.assign_model_and_deck()    

        tree = xml.etree.ElementTree.parse(os.path.join(mw.pm.addonFolder(), 'extractor_base/kanjidic2.xml'))
        setattr(self, "root", tree.getroot())

        for nid in nids:        
            self.createNotes(self.extractKanji(mw.col.getNote(nid)[self.vocabNote['Expression']]))
    
        mw.progress.finish()
        mw.reset()       
        showInfo("Kanji cards have been created and added to collection. Information has been provided by the kanjiDic2. For more inforamtion look into the __init__.py file, which is loacated in AnkiDataFolder/addons/extractor_base.")


    def createNotes(self, KanjiList):
        """ creates and adds new notes """
        for Kanji in KanjiList: 
	    # take next kanji if the current already exists
            if self.alreadyExists(Kanji):
                continue
   
            # get information
            note = self.addInfo(self.getInfo(Kanji))    
            # refresh note and add to database
            note.flush()        
            mw.col.addNote(note)


    def alreadyExists(self, char):
        """ retrun true if a note with the kanji already exits"""
        model = mw.col.models.byName(self.kanjiNote["KModel"])
        nids = mw.col.models.nids(model)

        for nid in nids:
            note = mw.col.getNote(nid)
            if note[self.kanjiNote["Kanji"]] == char:
                if self.hasValue('ExampleWords') or self.hasValue('ExampleWordsMeaning'):
                    s1, s2 = self.findExamples(char)
                    if self.hasValue('ExampleWordsMeaning'):
                        note[self.kanjiNote["ExampleWordsMeaning"]] = s1
                    if self.hasValue('ExampleWords'):
                        note[self.kanjiNote["ExampleWords"]] = s2
                    note.flush()    
                return True


    def getInfo(self, char):
        """ returns a dictionary with information about the kanji"""
        meanings = None
        onYomi = None
        kunYomi = None
        radical = None
        strokeNum = None
        jlpt = None
        grade = None

        Entry = [x for x in getattr(self, "root") if x.findtext('literal') == char][0]
        
        if self.hasValue("KMeaning"):
            meanings = []
            for m in Entry.findall('reading_meaning/rmgroup/meaning'):
                if m.get("m_lang", True) == True:
                    meanings.append(m.text)
    
        # get all OnYomi and KunYomi
        if self.hasValue("OnYomi"):
            onYomi = [reading.text for reading in Entry.findall('reading_meaning/rmgroup/reading[@r_type="ja_on"]')]


        if self.hasValue("KunYomi"):
            kunYomi = [reading.text for reading in Entry.findall('reading_meaning/rmgroup/reading[@r_type="ja_kun"]')]

        # get the radical from the text file
        if self.hasValue("Radical"):
            radical = ''
            radNum = Entry.findtext('radical/rad_value[@rad_type="classical"]')
            with codecs.open(os.path.join(mw.pm.addonFolder(), 'extractor_base/radicals.txt'), 'r', 'utf8') as file:
                for line in file:
                    if line.split()[0] == radNum:
                        radical = line[(len(radNum) + 1):]
                        file.close()
                        break	
            if not file.closed:
                file.close()
    
        # get stroke count
        if self.hasValue("StrokeNumber"):
            strokeNum = Entry.findtext('misc/stroke_count')

        # get grade
        grade = Entry.findtext('misc/grade')

        # get JLPT Level
        jlpt = Entry.findtext('misc/jlpt')

        return {'kanji': char, 'meanings': meanings, 'onYomi': onYomi, 'kunYomi': kunYomi, 'radical': radical, 'strokeNumber': strokeNum, 'grade': grade, 'JLPT': jlpt}


    def addInfo(self, info):
        """ add information to the note """    
        Note = mw.col.newNote()

        # the kanji itself
        Note[self.kanjiNote["Kanji"]] = info['kanji']
            
        # OnYomi
        if info['onYomi'] != None:
            Note[self.kanjiNote["OnYomi"]] = ', '.join(info['onYomi'])
    
        # KunYomi
        if info['kunYomi'] != None:
            Note[self.kanjiNote["KunYomi"]] = ', '.join(info['kunYomi'])
       
        # english meaning           
        if info['meanings'] != None:
            Note[self.kanjiNote["KMeaning"]] = ', '.join(info['meanings'])

        # find and add example Vocab
        if self.hasValue('ExampleWordsMeaning') or self.hasValue('ExampleWords'):
            s1, s2 = self.findExamples(info['kanji'])
            if self.hasValue('ExampleWords'):
                Note[self.kanjiNote['ExampleWords']] = s2
            if self.hasValue('ExampleWordsMeaning'):    
                Note[self.kanjiNote['ExampleWordsMeaning']] = s1

        # radicals
        if info['radical'] != None:
            Note[self.kanjiNote['Radical']] = info['radical']
               
        # stroke number
        if info['strokeNumber'] != None:
            Note[self.kanjiNote['StrokeNumber']] = info['strokeNumber']

        # add and create tags
        self.addTags(Note, info['grade'], info['JLPT'])
        return Note


    def findExamples(self, Kanji):
        """ find examples for kanji from Vocabulary deck """
         
        # parse through the notes 
        examplesFoundJap = []
        examplesFoundEng = []
        for nid in mw.col.models.nids(mw.col.models.byName(self.vocabNote['VModel'])):
            note = mw.col.getNote(nid)
            if Kanji in note[self.vocabNote['Expression']]:
                examplesFoundJap.append(note[self.vocabNote['Reading']])
                examplesFoundEng.append(note[self.vocabNote['VMeaning']])
                
        s1 = ''
        s2 = ''
        if examplesFoundJap:
            # create the string for the vocab
            for i, expression in enumerate(examplesFoundJap):
                s1 += expression + ': ' + examplesFoundEng[i] + '</br>'
                s2 += expression + '</br>'
        return s1, s2
        

    def isKanji(self, char):
        """ return true if char is a kanji or false if not """
        code = ord(char)
        return 0x4E00 <= code <= 0x9FFF


    def extractKanji(self, string):    
        """ take a string and return a list with only kanji """
        kanjiList = []
        for char in string:                   
            if self.isKanji(char):
                kanjiList.append(char)
        return kanjiList


    def addTags(self, note, grade, jlpt):
        """ add tags for kanji grade and JLPT-Level on note, if available """
        if grade != '' and grade is not None and self.Tags["gradeTag"] == "1":
            note.addTag('Kanji_Grade_' + grade)

        if jlpt != '' and jlpt is not None and self.Tags["jlptTag"] == "1":
            note.addTag('JLPT_Level_' + jlpt)   
        
        note.addTag(self.Tags["moreTags"])


    def assign_model_and_deck(self):
        """ Assign model to deck and deck to model """
        model = mw.col.models.byName(self.kanjiNote['KModel'])
        mw.col.models.setCurrent(model)
        mw.col.decks.select(mw.col.decks.id(self.kanjiNote['Deck']))

        cdeck = mw.col.decks.current()
        cdeck['mid'] = model['id']
        model['did'] = cdeck['id']
        mw.col.decks.save(cdeck)
        
        mw.col.reset()
                       

    def startCreation(self):
        """ searches for new cards and searches for kanji
        will be used for a button"""
        nids = []
        newNids = mw.col.findNotes("is:new")

        for nid in newNids:
	        if mw.col.getNote(nid).model()['name'] == self.vocabNote['VModel']:
	            nids.append(nid)
                
        if nids != []:
	        self.addCardsBulk(nids)
