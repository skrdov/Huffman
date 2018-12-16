class EncodingRules:
    def __init__(self, treeBits, symbols):
        # pvz jei yra 11110a0b11....., tai treeBits - bitukai; symbols - a,b
        self.treeBits = treeBits
        self.symbols = symbols

    def getTreeBits(self):
        return self.treeBits

    def getSymbols(self):
        return self.symbols
