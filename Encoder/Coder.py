from heapq import heappush, heappop

from bitarray import bitarray

from Model.EncodedData import EncodedData
from Model.EncodingRules import EncodingRules
from Model.Node import Node


class Coder:
    def __init__(self, word, codeWordLength):
        self.word = bitarray()
        self.word.frombytes(word)
        # print(self.word)
        self.codeWordLength = codeWordLength
        # Bitai kurie nebeiejo i raide. Pvz:. jei k = 4 ir turim žodį: 010110, tai 0101 bus viena raidė, o galune 10 nebesudarys raides
        self.suffixBits = bitarray()
        self.suffixBits, self.word = self.__getSuffixBits()
        # print(self.suffixBits)
        self.lettersDictionary = self.__getLettersDictionary()

    def __getSuffixBits(self):
        suffixBitsLength = len(self.word) % self.codeWordLength
        if suffixBitsLength == 0:
            return bitarray(), self.word
        # print(suffixBitsLength)
        suffixBits = self.word[len(self.word) - suffixBitsLength:len(self.word)]
        return suffixBits, self.word[:len(self.word) - suffixBitsLength]

    def getEncodingRules(self):
        rootNode = self.__createTree()
        treeStr = self.__getEncodingDecodingRules(rootNode)
        # print(treeStr)
        treeBits, letters = self.__separateTreeBitsAndLetters(treeStr)
        encodingRules = EncodingRules(treeBits, letters)
        return encodingRules

    # pvz jei yra 11110a0b11....., tai treeBits - bitukai; symbols - a,b
    def __separateTreeBitsAndLetters(self, treeStr):
        bits = []
        letters = []
        for element in treeStr:
            if isinstance(element, bool):
                bits.append(element)
            else:
                letters.append(element)
        return bitarray(bits), letters

    # Gaunam taisykles. Pvz:. 1110a110b... -> a dekoduojama i 0001, b i
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
        # letter[0], kadangi letter butu [raide, daznis]
        encodedLetter = self.lettersDictionary[letter[0]]
        currentNode = node
        for i in range(0, len(encodedLetter)):
            bit = encodedLetter[i]
            if bit == 0:
                if currentNode.leftChild is None:
                    currentNode.leftChild = Node('')
                currentNode = currentNode.leftChild
            elif bit == 1:
                if currentNode.rightChild is None:
                    currentNode.rightChild = Node('')
                currentNode = currentNode.rightChild
        currentNode.setLetter(letter[0])
        return node

    def getEncodedData(self):
        encodedWord = bitarray()
        i = 0
        while i < len(self.word):
            currentLetter = self.word[i:i + self.codeWordLength]
            encodedLetter = self.__getEncodedLetter(currentLetter.to01())
            encodedWord.extend(encodedLetter)
            # print(self.__getEncodedLetter(currentLetter.to01()))
            i += len(currentLetter)
        # print(self.suffixBits)
        return EncodedData(encodedWord, self.suffixBits)

    def __getEncodedLetter(self, letter):
        return self.lettersDictionary[letter]

    # Gaunam žodyna koki simboli i koki uzkoduoti. Tai diction[a] - gaunam kaip uzkoduotas a
    def __getLettersDictionary(self):
        uniqueSymbols = self.__getUniqueLettersInWord()
        # print(uniqueSymbols)
        symbolsList = self.__splitListOfSymbolsToListOfSymbolsList(uniqueSymbols)
        if len(symbolsList) == 1:
            diction = self.__createDictionaryForSymbols(symbolsList, "0", {})
        else:
            diction = self.__createDictionaryForSymbols(symbolsList, "", {})
        # print("dict dydis")
        # print(len(diction))
        return diction

    # Jei turim lista [a,b,c,d], tai verciam i [[a],[b],[c],[d]]
    def __splitListOfSymbolsToListOfSymbolsList(self, uniqueSymbols):
        list = []
        for element in uniqueSymbols:
            newList = [element]
            list.append(newList)
        return list

    # gaunam dictionary raidems
    def __createDictionaryForSymbols(self, symbolsList, currentSeq, diction):
        if len(symbolsList) == 1:
            diction[((symbolsList[0])[0])[0]] = bitarray(currentSeq)
            # print(len(currentSeq))
            # print("key: %s, value: %s" % (((symbolsList[0])[0])[0], currentSeq))
            return diction
        minHeap = self.__createHeap(symbolsList)
        # print("recLimit %d" % (sys.getrecursionlimit()))
        while len(minHeap) != 2:
            # 2 mažiausius bucketus apjungiam i viena bucketa. Jei turim [[a],[b],[c],[d]] verciam i [[a], [b], [c,d]]
            minHeap = self.__merge2LeastBucketsIntoOne(minHeap)
            # symbolsList = self.__merge2LeastBucketsIntoOne(symbolsList)
        # Po loopo gaunam lista kuriame yra du itemai, pvz [[a, c, h, ...], [b, d, e, ...]]
        # symbolsList = self.__sortDescending(symbolsList)
        leftList = self.__splitListOfSymbolsToListOfSymbolsList(heappop(minHeap)[1])
        currentSeq = currentSeq + "0"
        diction = self.__createDictionaryForSymbols(leftList, currentSeq, diction)
        currentSeq = currentSeq[:len(currentSeq) - 1]
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
        # print(len(symbolsList))
        for i in range(0, len(symbolsList)):
            valuesList.append(self.__calculateTotalValueOfBucket(symbolsList[i]))
        for i in range(0, len(symbolsList) - 1):
            for j in range(i + 1, len(symbolsList)):
                if (valuesList[i] > valuesList[j]):
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

    # Gaunam lista unikaliu raidziu ir ju daznius [['00001', 1534], [...], ...]
    def __getUniqueLettersInWord(self):
        i = 0
        length = len(self.word)
        dict = {}
        while i < length:
            letter = self.word[i:i + self.codeWordLength]
            if letter.to01() in dict:
                dict[letter.to01()] += 1
            else:
                dict[letter.to01()] = 1
            i += len(letter)
        dictList = []
        for key, value in dict.items():
            dictList.append([key, value])
        return dictList
