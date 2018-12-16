import numpy as np
from itertools import groupby
import sys
import struct
import os.path
from bitarray import bitarray


class EncodingRules:
    def __init__(self, treeBits, symbols):
        # pvz jei yra 11110a0b11....., tai treeBits - bitukai; symbols - a,b
        self.treeBits = treeBits
        self.symbols = symbols

    def getTreeBits(self):
        return self.treeBits

    def getSymbols(self):
        return self.symbols


class EncodedData:
    def __init__(self, encodedWord, suffixBits):
        self.encodedWord = encodedWord
        self.suffixBits = suffixBits

    def getEncodedWord(self):
        return self.encodedWord

    def getSuffixBits(self):
        return self.suffixBits


class Node:
    def __init__(self, letter):
        self.letter = letter
        self.leftChild = None
        self.rightChild = None

    def addLeftChild(self, child):
        self.leftChild = child

    def addRightChild(self, child):
        self.rightChild = child

    def getLeftChild(self):
        return self.leftChild

    def getLetter(self):
        return self.letter

    def setLetter(self, letter):
        self.letter = letter


class Decoder:
    def __init__(self, encodedData, rulesFromEncoder):
        self.encodedWord = encodedData.getEncodedWord()
        self.suffixBits = encodedData.getSuffixBits()
        self.rulesFromEncoder = rulesFromEncoder
        self.codedSymbolBitsLength = self.__getSymbolBitLength(self.rulesFromEncoder.getTreeBits())

    def __getSymbolBitLength(self, rulesTree):
        i = 0
        while rulesTree[i] != 0:
            i += 1
        return i

    def decode(self):
        self.decodingRules = {}
        # root = Node('')
        bits = self.rulesFromEncoder.getTreeBits()
        letters = self.rulesFromEncoder.getSymbols()
        # print(letters)
        self.__createDecodingDictionary(bits, letters, bitarray())
        # print("dict dydis")
        # print(len(self.decodingRules))
        decodedWord = self.__decodeWord()
        decodedWord = self.__addSuffix(decodedWord)
        return decodedWord

    # Pridedam neuzkoduota galune, nes del k gali likti neuzkoduotu bituku zodyje
    def __addSuffix(self, decodedWord):
        if len(self.suffixBits) != 0:
            return decodedWord + self.suffixBits
        else:
            return decodedWord

    def __decodeWord(self):
        str = bitarray()
        i = 0
        temp = bitarray()
        while i < len(self.encodedWord):
            temp.append(self.encodedWord[i])
            if self.__isEncodedLetter(temp):
                str.extend(self.decodingRules[temp.to01()])
                temp = bitarray()
            i += 1
        return str

    def __isEncodedLetter(self, temp):
        if temp.to01() in self.decodingRules:
            return True
        return False

    def __createDecodingDictionary(self, bits, letters, buildingBits):
        if bits[0] == 0:
            self.decodingRules[buildingBits.to01()] = letters[0]
            # print("key: %s, value: %s" % (letters[0].to01(), buildingBits.to01()))
            # print(self.decodingRules[''])
            # print(buildingBits.to01())
            # print(letters[0])
            return bits[1:], letters[1:]
        elif bits[0] == 1:
            if (len(bits) > 1):
                buildingBits.append(False)
                bitss, letters = self.__createDecodingDictionary(bits[1:], letters, buildingBits)
                bits = [bits[0]]
                bits.extend(bitss)
                buildingBits.pop()
            if len(bits) > 1:
                buildingBits.append(True)
                bitss, letters = self.__createDecodingDictionary(bits[1:], letters, buildingBits)
                bits = [bits[0]]
                bits.extend(bitss)
                buildingBits.pop()
            return bits[1:], letters
        return None


class CodeReader:
    def __init__(self, fileName):
        self.fileName = fileName
        self.__readFromFile()

    def getEncodedData(self):
        return self.encodedData

    def getRulesFromEncoder(self):
        return self.rulesFromEncoder

    def __readFromFile(self):
        f = open(self.fileName, 'rb')

        # Skaitom kiek bituku paskutiniame teksto baite bereiksmiai + tame paciame baite kiek liko neuzkoduotu bituku (originalaus zodzio galune)
        trashAndSuffixBitsLengthByte = f.read(1)
        trashBitsLength, suffixBitsLength = self.__getTrashAndSuffixBitsLength(trashAndSuffixBitsLengthByte)
        # print("suffix bit length")
        # print(suffixBitsLength)
        # print(trashBitsLength)
        # self.__int_from_bytes(trashBitsLengthByte)

        # Skaitom koks raides ilgis bitukais originaliame žodyje
        seekCount = 1
        f.seek(seekCount)
        letterLengthByte = f.read(1)
        letterLength = self.__int_from_bytes(letterLengthByte)

        # Skaitom suffix bitukus (bitukai kurie nebuvo uzkoduoti, nes netilpo i ivesta raides ilgi)
        seekCount = 2
        f.seek(seekCount)
        bytesToRead = self.__getBytesAmountToRead(suffixBitsLength)
        suffixBytes = f.read(bytesToRead)
        suffixBits = self.__getSuffixBits(suffixBytes, suffixBitsLength)
        # print(suffixBits)

        # Skaitom kiek baitu uzema kodavimo/dekodavimo taisykliu medis
        # print("suffix bytes")
        # print(bytesToRead)
        seekCount = 2 + bytesToRead
        f.seek(seekCount)
        treeLengthInBytes = f.read(2)
        treeLength = self.__int_from_bytes(treeLengthInBytes)
        # print("tree rules")
        # print(treeLength)

        # Skaitom  kodavimo/dekodavimo taisykles
        seekCount += 2
        f.seek(seekCount)
        treeBytes = f.read(treeLength)
        treeBits = bitarray()
        treeBits.frombytes(treeBytes)
        treeBits = self.__filterTrashBits(treeBits)
        countEncodedLetters = self.__getEncodedLettersAmount(treeBits)

        letterBits = letterLength * countEncodedLetters
        toReadBytes = self.__getBytesAmountToRead(letterBits)
        seekCount += treeLength
        f.seek(seekCount)
        lettersInBytes = f.read(toReadBytes)
        allLettersInBitsSeq = bitarray()
        allLettersInBitsSeq.frombytes(lettersInBytes)
        lettersList = self.__chopToLetterInBitsList(allLettersInBitsSeq, letterLength, countEncodedLetters)
        # print(lettersList)
        # print(len(lettersList))
        # print(allLettersInBitsSeq)
        # Skaitom  užkoduotus žodžius

        seekCount += toReadBytes
        f.seek(seekCount)
        codeBytes = f.read()
        encodedTextBits = bitarray()
        encodedTextBits.frombytes(codeBytes)

        encodedTextBits = self.__filterCodedWordAdditionalBits(encodedTextBits, trashBitsLength)
        # print(toReadBytes)
        # print("encodedWord")

        self.rulesFromEncoder = EncodingRules(treeBits, lettersList)
        self.encodedData = EncodedData(encodedTextBits, suffixBits)

    def __getSuffixBits(self, suffixBytes, suffixBitsLength):
        if suffixBitsLength == 0:
            return bitarray()
        suffixBits = bitarray()
        suffixBits.frombytes(suffixBytes)
        suffixBits = suffixBits[:suffixBitsLength]
        return suffixBits

    def __getBytesAmountToRead(self, bits):
        if bits % 8 == 0:
            return int(bits / 8)
        else:
            # print(int(bits / 8) + 1)
            return int(bits / 8) + 1

    def __getTrashAndSuffixBitsLength(self, trashAndSuffixBitsLengthByte):
        b = bitarray()
        b.frombytes(trashAndSuffixBitsLengthByte)
        trashBitsSizeBits = bitarray(8)
        trashBitsSizeBits.setall(False)
        trashBitsSizeBits[5:] = b[:3]
        suffixBitsSizeBits = bitarray(8)
        suffixBitsSizeBits.setall(False)
        suffixBitsSizeBits[3:] = b[3:]
        return self.__int_from_bytes(trashBitsSizeBits.tobytes()), self.__int_from_bytes(suffixBitsSizeBits.tobytes())

    def __chopToLetterInBitsList(self, allLettersInBitsSeq, letterLength, letterCount):
        totalBitsForLetters = letterLength * letterCount
        allLettersInBitsSeq = allLettersInBitsSeq[:totalBitsForLetters]
        i = 0
        letterInBitsList = []
        while i < len(allLettersInBitsSeq):
            currentLetterInBits = allLettersInBitsSeq[i:i + letterLength]
            letterInBitsList.append(currentLetterInBits)
            i += letterLength
        return letterInBitsList

    def __getEncodedLettersAmount(self, treeBits):
        count = 0
        for i in treeBits:
            if i == 0:
                count += 1
        return count

    def __filterCodedWordAdditionalBits(self, bits, trashBitsLength):
        return bits[:len(bits) - trashBitsLength]

    def __filterTrashBits(self, bits):
        length = len(bits)
        i = length - 1
        while bits[i] != 0:
            bits = bits[:len(bits) - 1]
            i -= 1
        return bits

    def __int_from_bytes(self, xbytes):
        return int.from_bytes(xbytes, 'big')


'''
text1 = input('Uzkoduoto failo pavadinimas: ')
if os.path.isfile(text1) == False:
    print("Toks failas neegzistuoja")
    sys.exit(1)
    
text2 = input('Dekoduoto failo pavadinimas(orginalus tekstas): ')
'''
sys.setrecursionlimit(10000)
# Dekoduojam teksta is failo
text1 = r"C:\Users\Dovydas\infoTeorija\tests\encodedFile.txt"
# Dekoduojam i faila
text2 = r"C:\Users\Dovydas\infoTeorija\tests\decodedfile.txt"
codeReader = CodeReader(text1)
encodedData = codeReader.getEncodedData()
rulesFromEncoder = codeReader.getRulesFromEncoder()
decoder = Decoder(encodedData, rulesFromEncoder)
# print(decoder.decode().tobytes())
# print(decoder.decode())
# print(decoder.decode()[:30])
f = open(text2, 'wb')
f.write(decoder.decode().tobytes())
