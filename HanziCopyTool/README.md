# HanziCopyTool 
HanziCopyTool is an anki addon, which was requested on the r/anki subreddit. It is ment to be used to copy the gif files from this deck https://ankiweb.net/shared/info/39888802 to notes, which contains a chinese word or phrase, so that the stroke order of every character is displayed as a gif.

# Setup
Put the HanziCopyTool.py file in the anki add-ons folder (quick access: open anki -> Tools -> Add-ons -> Open Add-ons folder). Now open the file with your favourite text editor and write the values for the following variables:

TARGET_MODEL: The name of the note type to which the gif files will be copied to.
TARGET_LOOKUP: The name of the field, which is contains the word or phrase.
TARGET_FIELD: The name of the field, to which the gif files be copied.

Important: What ever you write, write it between the single quotes.

If you are using the anki deck mentioned above, you don't have to change the values for the SOURCE... variables. If you howerver want to change them, then it is the same logic as above, but you set the source of what will be copied.

The variable 'ENABLE_AUTOMATIC_COPY' enables or disables the addon in the note editor. Either set the value to False (disable) or True (enable).
The variable 'ENABLE_EDITOR_BUTTON' enables or disables the button in the note editor. Either set the value to False (disable) or True (enable).

# Usage
You can use the add-on in four ways.

In the main window you can click Tools -> Copy Hanzi Stroke Order. Note that this option only updates the target notes, which are new. So it is best to use it right after you added a bunch of new notes.

In the browser you can click Edit -> Bulk Copy Hanzi Stroke Order. This will update all notes, you have currently selected in the browser. If you use the addon for the first time, you can filter the cards for the note type, select all cards and click the button to update all notes.

In the note editor, if you loose focus on the target lookup (press tab, or click some where else after you clicked on the field) the content of the source notes will be copied to the editor. 

In the note editor you can use the small button, which has no icon. You can hover above it to read its function. The default shortcut is Ctrl-H.
 
# Misc
Notes, whose target field is not empty will not be updated by the add-on, except if you use the editor button. Pressing it will overwrite anything in the target field.
 
If a character from the target lookup field could not be found in the other note type, the target will be tagged with "Hanzi_Tool_Error".
