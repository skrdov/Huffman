from bitarray import bitarray

from Model.EncodedData import EncodedData
from Model.EncodingRules import EncodingRules


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