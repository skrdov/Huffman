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
# Nuskaitom komandines eilutes parametrus
codedSymbolInBitsLength = 8
fileIn = 'test.txt'
fileOut = 'encoded'
if len(sys.argv) > 1:
    codedSymbolInBitsLength = int(sys.argv[1])
if len(sys.argv) > 2:
    fileIn = sys.argv[2]
if len(sys.argv) > 3:
    fileOut = sys.argv[3]

sys.setrecursionlimit(10000)
# Nuskaitom norima uzkoduoti faila
f = open(fileIn, 'rb')
allBytes = f.read()

coder = Coder(allBytes, codedSymbolInBitsLength)
encodedData = coder.getEncodedData()
encodingRules = coder.getEncodingRules()
codeWriter = CodeWriter(encodingRules, encodedData)
codeWriter.writeToFile(fileOut)
