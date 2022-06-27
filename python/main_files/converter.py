from music21 import * # Simple but not recommended
import os
os.chdir('xmlsamples') # 'music' is my file location

c = converter.parse('simple.mxl')
bu = braille.translate.objectToBraille(c)
ba = braille.basic.brailleUnicodeToBrailleAscii(bu)
print(ba)