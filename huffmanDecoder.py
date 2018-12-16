import sys

from Decoder.Decoder import Decoder
from Encoder.CodeReader import CodeReader

'''
text1 = input('Uzkoduoto failo pavadinimas: ')
if os.path.isfile(text1) == False:
    print("Toks failas neegzistuoja")
    sys.exit(1)
    
text2 = input('Dekoduoto failo pavadinimas(orginalus tekstas): ')
'''
sys.setrecursionlimit(10000)
# Dekoduojam teksta is failo
text1 = "encoded"
# Dekoduojam i faila
text2 = "decoded.txt"
codeReader = CodeReader(text1)
encodedData = codeReader.getEncodedData()
rulesFromEncoder = codeReader.getRulesFromEncoder()
decoder = Decoder(encodedData, rulesFromEncoder)
# print(decoder.decode().tobytes())
# print(decoder.decode())
# print(decoder.decode()[:30])
f = open(text2, 'wb')
f.write(decoder.decode().tobytes())
