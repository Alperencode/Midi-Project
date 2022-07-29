from music21 import * 
import os

os.chdir('xmlsamples') 

converter = converter.parse('simple.mxl')
bu = onverterbraille.translate.objectToBraille(c)
ba = braille.basic.brailleUnicodeToBrailleAscii(bu)
print(ba)
