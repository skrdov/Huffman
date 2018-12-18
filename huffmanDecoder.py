import sys

from Decoder.Decoder import Decoder
from Decoder.CodeReader import CodeReader

'''
text1 = input('Uzkoduoto failo pavadinimas: ')
if os.path.isfile(text1) == False:
    print("Toks failas neegzistuoja")
    sys.exit(1)
    
text2 = input('Dekoduoto failo pavadinimas(orginalus tekstas): ')
'''
# Nuskaitom komandines eilutes parametrus
fileIn = 'encoded'
fileOut = 'decoded.txt'
if len(sys.argv) > 1:
    fileIn = sys.argv[1]
if len(sys.argv) > 2:
    fileOut = sys.argv[2]

sys.setrecursionlimit(10000)
fileName = sys.argv[0]
# Dekoduojam teksta is failo
# Dekoduojam i faila
codeReader = CodeReader(fileIn)
encodedData = codeReader.getEncodedData()
rulesFromEncoder = codeReader.getRulesFromEncoder()
decoder = Decoder(encodedData, rulesFromEncoder)
# print(decoder.decode().tobytes())
# print(decoder.decode())
# print(decoder.decode()[:30])
f = open(fileOut, 'wb')
f.write(decoder.decode().tobytes())
