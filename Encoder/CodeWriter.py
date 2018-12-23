from bitarray import bitarray


class CodeWriter:
    def __init__(self, encodingRules, encodedData):
        self.encodingRules = encodingRules
        self.encodedData = encodedData

    def writeToFile(self, fileName):
        # Rasom: 3 bitai pasako kiek uzkoduotam zodyje yra nereikalingu bituku, tam kad uzkoduotas zodis tilptu i pilna baita. + 5 bitai pasako kiek bitu liko neuzkoduotu
        # Gaunam kiek bitu nuskaityti neuzkoduotai galunei
        # Rasom neuzkoduota galune
        # Rasom medi
        # Rasom viska iki galo - uzkoduota zodi
        encodedWord = self.encodedData.getEncodedWord()
        suffixBits = self.encodedData.getSuffixBits()
        letterLength = self.encodingRules.getLetterLength()
        letterLengthByte = self.__int_to_bytes(letterLength)
        suffixBitsBytes = self.__getBytesFromNonFullBits(suffixBits)
        treeRulesPlusEncodedWord = bitarray()
        treeBits = self.encodingRules.getTreeBits()
        #treeBits = self.__deleteLatestOnes(treeBits)
        treeRulesPlusEncodedWord.extend(treeBits)
        treeRulesPlusEncodedWord.extend(encodedWord)
        #print(encodedWord[:25])
        treeRulesPlusEncodedWordBytes = self.__addBitsToCompleteLastByte(treeRulesPlusEncodedWord)
        trashAndSuffixBitsLengthByte = self.__getTrashAndSuffixBitsLengthByte(len(treeRulesPlusEncodedWord), len(suffixBits))
        
        f = open(fileName, 'wb')
        f.write(trashAndSuffixBitsLengthByte)
        f.write(letterLengthByte)
        f.write(suffixBitsBytes)
        f.write(treeRulesPlusEncodedWordBytes)
        f.close()

    def __getTrashAndSuffixBitsLengthByte(self, encodedWordLength, suffixBitsLength):
        if encodedWordLength % 8 == 0:
            value1 = 0
        else:
            value1 = (8 - (encodedWordLength % 8)) << 5
        return self.__int_to_bytes(value1 + suffixBitsLength)

    # Gaunam baitus, is bitu sekos kurios liekana != 0 (uzpildom vienetukais gala)
    def __getBytesFromNonFullBits(self, bits):
        # Gaunam kiek bitu reikia kad uzpildytume baita
        bitsToAdd = self.__bitsToGetFullByte(len(bits))
        # Prijungiam bitukas, kad gautume pilna baita
        bits.extend(self.__addBitsToCompleteByte(bitsToAdd))
        # Verciam i baitus
        return bits.tobytes()

    def __addBitsToCompleteByte(self, bitsToAdd):
        bits = []
        for i in range(0, bitsToAdd):
            bits.append(True)
        return bits

    def __addBitsToCompleteLastByte(self, bitArray):
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


