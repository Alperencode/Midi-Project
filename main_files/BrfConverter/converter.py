from music21 import * 
import os

c = converter.parse('example.xml')
bu = braille.translate.objectToBraille(c)
ba = braille.basic.brailleUnicodeToBrailleAscii(bu)
print(ba)