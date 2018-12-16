import numpy as np
from itertools import groupby
import sys
import os.path
import struct
from bitarray import bitarray
from heapq import heappush, heappop

class EncodingRules:
    def __init__(self, treeBits, symbols):
        #pvz jei yra 11110a0b11....., tai treeBits - bitukai; symbols - a,b
        self.treeBits = treeBits
        self.symbols = symbols
    def getTreeBits(self):
        return self.treeBits
    def getLetters(self):
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
        
    def addLeftChild(self, child):
        self.rightChild = child
        
    def getLetter(self):
        return self.letter
        
    def setLetter(self, letter):
        self.letter = letter
        
class Coder:
    def __init__(self, word, codeWordLength):
        self.word = bitarray()
        self.word.frombytes(word)
        #print(self.word)
        self.codeWordLength = codeWordLength
        #Bitai kurie nebeiejo i raide. Pvz:. jei k = 4 ir turim žodį: 010110, tai 0101 bus viena raidė, o galune 10 nebesudarys raides
        self.suffixBits = bitarray()
        self.suffixBits, self.word = self.__getSuffixBits()
        #print(self.suffixBits)
        self.lettersDictionary = self.__getLettersDictionary()
    def __getSuffixBits(self):
        suffixBitsLength = len(self.word) % self.codeWordLength
        if suffixBitsLength == 0:
            return bitarray(), self.word
        #print(suffixBitsLength)
        suffixBits = self.word[len(self.word) - suffixBitsLength:len(self.word)]
        return suffixBits, self.word[:len(self.word)-suffixBitsLength]
    def getEncodingRules(self):
        rootNode = self.__createTree()
        treeStr = self.__getEncodingDecodingRules(rootNode)
        #print(treeStr)
        treeBits, letters = self.__separateTreeBitsAndLetters(treeStr)
        encodingRules = EncodingRules(treeBits, letters)
        return encodingRules
    #pvz jei yra 11110a0b11....., tai treeBits - bitukai; symbols - a,b
    def __separateTreeBitsAndLetters(self, treeStr):
        bits = []
        letters = []
        for element in treeStr:
            if isinstance(element, bool):
                bits.append(element)
            else:
                letters.append(element)
        return bitarray(bits), letters
    #Gaunam taisykles. Pvz:. 1110a110b... -> a dekoduojama i 0001, b i 
    def __getEncodingDecodingRules(self, node):
        str = []
        if node.getLetter() == '':
            str.append(True)
        else:
            str.append(False)
            str.append(node.getLetter())
        if node.leftChild is not None:
            str.extend(self.__getEncodingDecodingRules(node.leftChild))
        if node.rightChild is not None:
            str.extend(self.__getEncodingDecodingRules(node.rightChild))
        return str
    
    def __createTree(self):
        rootNode = Node('')
        uniqueCharsRepresentedInBits = self.__getUniqueLettersInWord()
        for letter in uniqueCharsRepresentedInBits:
            rootNode = self.__updateTree(rootNode, letter)
        return rootNode
        
    def __updateTree(self, node, letter):
        #letter[0], kadangi letter butu [raide, daznis]
        encodedLetter = self.lettersDictionary[letter[0]]
        currentNode = node
        for i in range(0, len(encodedLetter)):
            bit = encodedLetter[i]
            if bit == 0:
                if currentNode.leftChild == None:
                    currentNode.leftChild = Node('')
                currentNode = currentNode.leftChild
            elif bit == 1:
                if currentNode.rightChild == None:
                    currentNode.rightChild = Node('')
                currentNode = currentNode.rightChild
        currentNode.setLetter(letter[0])
        return node
        
    def getEncodedData(self):
        encodedWord = bitarray()
        i = 0
        while i < len(self.word):
            currentLetter = self.word[i:i+self.codeWordLength]
            encodedLetter = self.__getEncodedLetter(currentLetter.to01())
            encodedWord.extend(encodedLetter)
            #print(self.__getEncodedLetter(currentLetter.to01()))
            i += len(currentLetter)
        #print(self.suffixBits)
        return EncodedData(encodedWord, self.suffixBits)
    
    def __getEncodedLetter(self, letter):
        return self.lettersDictionary[letter]
    
    #Gaunam žodyna koki simboli i koki uzkoduoti. Tai diction[a] - gaunam kaip uzkoduotas a
    def __getLettersDictionary(self):
        uniqueSymbols = self.__getUniqueLettersInWord()
        #print(uniqueSymbols)
        symbolsList = self.__splitListOfSymbolsToListOfSymbolsList(uniqueSymbols)
        if(len(symbolsList) == 1):
            diction = self.__createDictionaryForSymbols(symbolsList, "0", {})
        else:
            diction = self.__createDictionaryForSymbols(symbolsList, "", {})
        #print("dict dydis")
        #print(len(diction))
        return diction
    #Jei turim lista [a,b,c,d], tai verciam i [[a],[b],[c],[d]]
    def __splitListOfSymbolsToListOfSymbolsList(self, uniqueSymbols):
        list = []
        for element in uniqueSymbols:
            newList = []
            newList.append(element)
            list.append(newList)
        return list
    
    #gaunam dictionary raidems
    def __createDictionaryForSymbols(self, symbolsList, currentSeq, diction):
        if(len(symbolsList) == 1):
            diction[((symbolsList[0])[0])[0]] = bitarray(currentSeq)
            #print(len(currentSeq))
            #print("key: %s, value: %s" % (((symbolsList[0])[0])[0], currentSeq))
            return diction
        minHeap = self.__createHeap(symbolsList)
        #print("recLimit %d" % (sys.getrecursionlimit()))
        while len(minHeap) != 2:
            #2 mažiausius bucketus apjungiam i viena bucketa. Jei turim [[a],[b],[c],[d]] verciam i [[a], [b], [c,d]]
            minHeap = self.__merge2LeastBucketsIntoOne(minHeap)
            #symbolsList = self.__merge2LeastBucketsIntoOne(symbolsList)
        #Po loopo gaunam lista kuriame yra du itemai, pvz [[a, c, h, ...], [b, d, e, ...]]
        #symbolsList = self.__sortDescending(symbolsList)
        leftList = self.__splitListOfSymbolsToListOfSymbolsList(heappop(minHeap)[1])
        currentSeq = currentSeq + "0"
        diction = self.__createDictionaryForSymbols(leftList, currentSeq, diction)
        currentSeq = currentSeq[:len(currentSeq)-1]
        rightList = self.__splitListOfSymbolsToListOfSymbolsList(heappop(minHeap)[1])
        currentSeq = currentSeq + "1"
        diction = self.__createDictionaryForSymbols(rightList, currentSeq, diction)
        
        return diction
    def __createHeap(self, symbolsList):
        heap = []
        for item in symbolsList:
            value = self.__calculateTotalValueOfBucket(item)
            heappush(heap, (value, item))
        return heap
    def __merge2LeastBucketsIntoOne(self, minHeap):
        least = heappop(minHeap)
        secLeast = heappop(minHeap)
        newItem = []
        newItem.extend(secLeast[1])
        newItem.extend(least[1])
        newItemValue = secLeast[0] + least[0]
        heappush(minHeap, (newItemValue, newItem))
        return minHeap

    def __sortDescending(self, symbolsList):
        valuesList = []
        #print(len(symbolsList))
        for i in range(0, len(symbolsList)):
            valuesList.append(self.__calculateTotalValueOfBucket(symbolsList[i]))
        for i in range(0, len(symbolsList)-1):
            for j in range(i+1, len(symbolsList)):
                if(valuesList[i] > valuesList[j]):
                    tempVal = valuesList[i]
                    valuesList[i] = valuesList[j]
                    valuesList[j] = tempVal
                    temp = symbolsList[i]
                    symbolsList[i] = symbolsList[j]
                    symbolsList[j] = temp
                    i -= 1
        return symbolsList
    def __calculateTotalValueOfBucket(self, bucket):
        totalValue = 0
        for item in bucket:
            totalValue = totalValue + item[1]
        return totalValue

    #Gaunam lista unikaliu raidziu ir ju daznius [['00001', 1534], [...], ...]
    def __getUniqueLettersInWord(self):
        i = 0
        length = len(self.word)
        dict = {}
        while i < length:
            letter = self.word[i:i+self.codeWordLength]
            if letter.to01() in dict:
                dict[letter.to01()] += 1
            else:
                dict[letter.to01()] = 0
            i += len(letter)
        dictList = []
        for key, value in dict.items():
            dictList.append([key, value])
        return dictList

class CodeWriter:
    def __init__(self, encodingRules, encodedData):
        self.encodingRules = encodingRules
        self.encodedData = encodedData
    def writeToFile(self, fileName):
        #Rasom: 3 bitai pasako kiek uzkoduotam zodyje yra nereikalingu bituku, tam kad uzkoduotas zodis tilptu i pilna baita. + 5 bitai pasako kiek bitu liko neuzkoduotu
        #Gaunam kiek bitu nuskaityti neuzkoduotai galunei
        #Rasom neuzkoduota galune
        #Rasom kiek baitu skirta kodavimo/dekodavimo taisykliu medziui
        #Rasom medi
        #Rasom viska iki galo - uzkoduota zodi
        encodedWord = self.encodedData.getEncodedWord()
        suffixBits = self.encodedData.getSuffixBits()
        #print("suffix bit length")
        #print(len(suffixBits))
        letterLength = len(self.encodingRules.getLetters()[0])
        trashAndSuffixBitsLengthByte = self.__getTrashAndSuffixBitsLengthByte(len(encodedWord), len(suffixBits))
        letterLengthByte = self.__int_to_bytes(letterLength)
        suffixBitsBytes = self.__getBytesFromNonFullBits(suffixBits)
        encodedWordInBytes = self.__getEncodedWordInBytes(encodedWord)
        treeRulesBytes = self.__getBytesFromNonFullBits(self.encodingRules.getTreeBits())
        
        letters = self.encodingRules.getLetters()
        letters = self.__convertLettersToBitsArray(letters)
        lettersBytes = self.__getBytesFromNonFullBits(letters)
        #print(len(lettersBytes))
        treeRequiredBytes = len(treeRulesBytes)
        treeRequiredBytesBytes = self.__changeTo2Bytes(self.__int_to_bytes(treeRequiredBytes))
        #print(len(encodedWord))
        #print("tree rules")
        #print(len(treeRulesBytes))
        '''
        bbb = bitarray()
        bbb.frombytes(treeRequiredBytesBytes)
        print(bbb)
        '''
        
        f = open(fileName, 'wb')
        f.write(trashAndSuffixBitsLengthByte)
        f.write(letterLengthByte)
        #print("suffix")
        #print(len(suffixBitsBytes))
        f.write(suffixBitsBytes)
        #print("tree")
        #print(len(treeRequiredBytesBytes))
        f.write(treeRequiredBytesBytes)
        f.write(treeRulesBytes)
        f.write(lettersBytes)
        f.write(encodedWordInBytes)
        f.close()
    def __changeTo2Bytes(self, bytes):
        if len(bytes) == 2:
            return bytes
        else:
            bits = bitarray()
            bits.frombytes(bytes)
            newBits = bitarray(8)
            newBits.setall(False)
            newBits.extend(bits)
            return newBits.tobytes()
    def __convertLettersToBitsArray(self, letters):
        bits = bitarray()
        for letter in letters:
            #print(letter)
            bits.extend(letter)
        return bits
    def __getTrashAndSuffixBitsLengthByte(self, encodedWordLength, suffixBitsLength):
        if encodedWordLength % 8 == 0:
            value1 = 0
        else:
            value1 = (8 - (encodedWordLength % 8)) << 5
        return self.__int_to_bytes(value1 + suffixBitsLength)
    #Gaunam baitus, is bitu sekos kurios liekana != 0 (uzpildom vienetukais gala)
    def __getBytesFromNonFullBits(self, bits):
        #Gaunam kiek bitu reikia kad uzpildytume baita
        bitsToAdd = self.__bitsToGetFullByte(len(bits))
        #Prijungiam bitukas, kad gautume pilna baita
        bits.extend(self.__addBitsToCompleteByte(bitsToAdd))
        #Verciam i baitus
        return bits.tobytes()
    
    def __addBitsToCompleteByte(self, bitsToAdd):
        bits = []
        for i in range(0, bitsToAdd):
            bits.append(True)
        return bits
        
    def __getEncodedWordInBytes(self, bitArray):
        bitsToAdd = self.__bitsToGetFullByte(len(bitArray))
        bitArray.extend(self.__appendBits(bitsToAdd))
        bytes = bitArray.tobytes()
        return bytes
    
    def __appendBits(self, bitsToAdd):
        extraBits = bitarray()
        for i in range(0, bitsToAdd):
            extraBits.append(True)
        return extraBits
    
    def __bitsToGetFullByte(self, bits):
        if bits % 8 == 0:
            return 0
        else:
            return (int(bits / 8) + 1) * 8 - bits
    def __int_to_bytes(self, x):
        if x == 0:
            b = bitarray(8)
            b.setall(False)
            return b.tobytes()
        return x.to_bytes((x.bit_length() + 7) // 8, 'big')    

#text1 = input('Uzkoduoto simbolio ilgis bitais: ')
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
#Nustatom kiek bitu traktuosim kad yra raides ilgis
codedSymbolInBitsLength = 8
#Nuskaitom norima uzkoduoti faila
f = open(r"C:\Users\Dovydas\infoTeorija\tests\text2.txt", 'rb')
allBytes = f.read()
#Nuskaitom faila i kuri uzkoduosim 
text3 =  r"C:\Users\Dovydas\infoTeorija\tests\encodedFile.txt"

coder = Coder(allBytes, codedSymbolInBitsLength)
encodedData = coder.getEncodedData()
encodingRules = coder.getEncodingRules()
codeWriter = CodeWriter(encodingRules, encodedData)
codeWriter.writeToFile(text3)
