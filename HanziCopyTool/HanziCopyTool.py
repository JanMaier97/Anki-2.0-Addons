# -*- coding: utf-8 -*-

from aqt import mw
from aqt.qt import *
from aqt.utils import showInfo, tooltip
from anki.hooks import addHook, wrap


TARGET_MODEL = 'Basic'  # the note type, to which the content should be copied to.
TARGET_LOOKUP = 'Front' # the field, which is used to search the needed content.
TARGET_FIELD = 'Back'   # the field, to which the content is copied.

SOURCE_MODEL = 'Hanzi Writing'  # the note type, which is the source for the content.
SOURCE_LOOKUP = 'Hanzi'         # the field, which is used as the lookup.
SOURCE_FIELD = 'Diagram'        # the field, which contains the content, which will be copied.

ENABLE_AUTOMATIC_COPY = True    # set this to a value of True or False. Enables the automatic copying in the note editor.
ENABLE_EDITOR_BUTTON = True     # set this to a value of True or False. Enables a button in the note editor

BUTTON_SHORTCUT = 'Ctrl+H'  # shortcut for the button


def validateFields(modelName, fieldList):
    """Return True if the given model exists and has the specified fields."""
    
    model = None

    # check if the model exists
    model = mw.col.models.byName(modelName)
    if model is None:
        showInfo("The model {0} does not exist. Please check for spelling errors.".format(modelName))
        return False

    # check if the model has the fields
    fields = mw.col.models.fieldNames(model)    
    for field in fieldList:
        if field not in fields:
            showInfo("The model {0} doesn't have the field {1}".format(modelName, field))
            return False

    return True
    

def validateSettings():
    """Retrun true if the set options are valid."""

    # validate the models and their fields and return the result 
    return validateFields(TARGET_MODEL, [TARGET_LOOKUP, TARGET_FIELD]) and validateFields(SOURCE_MODEL, [SOURCE_LOOKUP, SOURCE_FIELD])


def handleTargetNote(nid):
    """Search and copy content to the given note."""
    
    note = mw.col.getNote(nid)

    # only write to an empty target field
    if note[TARGET_FIELD] != "":
        return

    lookup = note[TARGET_LOOKUP]
    sourceData = getSourceData(lookup)

    # enumeate the data, log error or add the content to the target field    
    for data in sourceData:
        if data is None:
            note.addTag("Hanzi_Tool_Error")
        else:
            note[TARGET_FIELD] += data
            
    note.flush() # save changes
        

def getSourceData(string):
    data = []
    dataFound = False

    srcMid = mw.col.models.byName(SOURCE_MODEL)['id']
    query = "mid:" + str(srcMid) + " (" + " or ".join(string) + ")" # query for the notes: modelId and (char1 or char2...)
    
    srcNids = mw.col.findNotes(query)

    # enumerate the characters and the notes
    for c in string:
        for srcNid in srcNids:
            srcNote = mw.col.getNote(srcNid)           
            if c == srcNote[SOURCE_LOOKUP]:
                data.append(srcNote[SOURCE_FIELD])
                dataFound = True
        if not dataFound:
            data.append(None) # there was an error
        else:
            dataFound = False
    return data    


def startProcess():
    """Start processing all new Notes."""

    # ensure that models and their fields exist
    if not validateSettings():
        return

    mid = mw.col.models.byName(TARGET_MODEL)['id']
    nids = mw.col.findNotes("is:new " + "mid:" + str(mid)) # get the now notes 
    
    for nid in nids:
        handleTargetNote(nid)

    mw.reset() # reset gui
    showInfo("Process finished.")


def onFocusLost(flag, note, fieldIndex):
    """Copy content in the note editor, when the focus of the field has been lost."""
   
    # check the model, of the note
    if note.model()['name'] != TARGET_MODEL:        
        return flag

    # validate the settings and ensure that the specified fields exist
    if not validateSettings():        
        return flag

    # return if the target field has been  set already
    if note[TARGET_FIELD]:        
        return flag
    
    # get the field index of the look up field
    # get the field map, which is a dic mapping field name to (ord, field)    
    index = mw.col.models.fieldMap(mw.col.models.byName(TARGET_MODEL))[TARGET_LOOKUP][0]

    # return if the field index, which triggered this event is the same as the index of the look up field
    if fieldIndex != index:        
        return flag

    # get the data and add them to the field
    data = getSourceData(note[TARGET_LOOKUP])
    
    if None in data:
        tooltip("Some characters could not be found.")
        # remove the null values from the array
        data = [elem for elem in data if not elem is None]

    # set the target field
    note[TARGET_FIELD] = ''.join(data)    
    return True   


def editorBtnClicked(self):
    """Copy content to the note editor, when the editor button has been clicked."""

    note = self.note
       
    # check the model, of the note
    if note.model()['name'] != TARGET_MODEL:
        showInfo("The note type is wrong.")
        return        

    # validate the settings and ensure that the specified fields exist
    if not validateSettings():
        return
    
    # get the field index of the look up field
    # get the field map, which is a dic mapping field name to (ord, field)    
    index = mw.col.models.fieldMap(mw.col.models.byName(TARGET_MODEL))[TARGET_LOOKUP][0]

    # get the data and add them to the field
    data = getSourceData(note[TARGET_LOOKUP])

    # check for None values and remove them from the array
    if None in data:
        tooltip("Some characters could not be found.")        
        data = [elem for elem in data if not elem is None]

    # set the target field
    note[TARGET_FIELD] = ''.join(data)    

    # save changes and redraw gui
    note.flush()
    mw.reset()
    

def onRegenerate(browser):
    """Copy content to the selected notes in the browser."""

    if not validateSettings():
        return

    # ensure that all selected notes are the target model
    if any(mw.col.getNote(nid).model()['name'] != TARGET_MODEL for nid in browser.selectedNotes()):
        showInfo("You have selected a card with the wrong note type.")
        return

    # copy the content for the cards
    for nid in browser.selectedNotes():
        handleTargetNote(nid)

    mw.reset()
    showInfo("Process finished.")


def setupBrowserMenu(browser):
    a = QAction("Bulk Copy Hanzi Stroke Order", browser)
    browser.connect(a, SIGNAL("triggered()"), lambda e=browser: onRegenerate(e))
    browser.form.menuEdit.addSeparator()
    browser.form.menuEdit.addAction(a)


def setupMainWindowButton():
    action = QAction("Copy Hanzi Stroke Order", mw)
    mw.connect(action, SIGNAL("triggered()"), startProcess)
    mw.form.menuTools.addAction(action)


def setupEditorButton(self):
    if not self is None and ENABLE_EDITOR_BUTTON:
        btn = self._addButton(
            "copyHanzi",
            lambda self = self: editorBtnClicked(self),
            tip = "Copy Hanzi Stroke Order ({0})".format(BUTTON_SHORTCUT))        
        btn.setShortcut(BUTTON_SHORTCUT)
        btn.setIcon(QIcon.fromTheme("edit-undo"))      
    
    
# add hooks
addHook("browser.setupMenus", setupBrowserMenu)
addHook("setupEditorButtons", setupEditorButton)

if ENABLE_AUTOMATIC_COPY:
    addHook("editFocusLost", onFocusLost)


