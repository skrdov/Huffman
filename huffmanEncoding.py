import sys

from Encoder.CodeWriter import CodeWriter
from Encoder.Coder import Coder

'''
try:
    codedSymbolInBitsLength = int(text1)
except ValueError:
    print("Ivestas ne skaicius")
    sys.exit(2)
    
if codedSymbolInBitsLength < 2 or codedSymbolInBitsLength > 24:
    print("Skaicius turi buti tarp 2 ir 24")
    sys.exit(3)
'''
sys.setrecursionlimit(10000)
# Nustatom kiek bitu traktuosim kad yra raides ilgis
codedSymbolInBitsLength = 8
# Nuskaitom norima uzkoduoti faila
f = open("test.txt", 'rb')
allBytes = f.read()
# Nuskaitom faila i kuri uzkoduosim
text3 = "encoded"

coder = Coder(allBytes, codedSymbolInBitsLength)
encodedData = coder.getEncodedData()
encodingRules = coder.getEncodingRules()
codeWriter = CodeWriter(encodingRules, encodedData)
codeWriter.writeToFile(text3)
