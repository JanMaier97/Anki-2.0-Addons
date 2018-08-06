# KanaAdder
An Anki addon, which will fill one field of a note with only kana from a japanese word. This will happen after a new note has been created. There is also a bulk add kana option for existing cards in the browser menu.

# Requirements
Install the addon 'japanese support'.

# Setup
Open the KanaAdder.py file and change the values of the variables READING_FIELD, KANA_FIELD and VOCAB_MODEL. Note that the values are case sensitive and the fields and the model must exist.

# Common Error
Sometimes there will be one or more hiragana characters than needed. The error happens when the reading from the japanese support addon  also contains a hiragana character between two kanji characters. For example the word 間に合う.
The reading field would look like this: 間に合[まにあ]う  
Then the kana field look like this: にまにあう
