################################################################################ Hash Class###############################################################################class Hash():    def __init__(self, values, addSize=False):        self.addSize = addSize        self.hashval = None        if isinstance(values, list):            assert all([isinstance(value, str) for value in values]), f"All values in {values} must be a string"            self.values = values        else:            assert isinstance(values, str), f"Hash input [{values}] must be a string (or list of strings)"            self.values = [values]                def findHash(self):        m = md5()        for value in self.values:            m.update(value.encode('utf-8'))        if self.addSize is True:            m.update(str(len(self.values)).encode('utf-8'))        self.hashval = m.hexdigest()            def getUID(self):        hvals = []        for value in self.values:            m = md5()            m.update(value.encode('utf-8'))            hvals.append(m.hexdigest()[:6])        return "-".join(hvals)                    def get(self, maxlen=None):        self.findHash()        retval = self.hashval[:maxlen] if isinstance(maxlen,int) else self.hashval        return retval        def getInt(self, maxlen=None):        self.findHash()        iHash = int(hashval, 16)        artistID = str(iHash) if maxlen < 1 else str(iHash % power(10,maxlen))        return artistID