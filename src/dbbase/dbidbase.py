""" Collection of classes to get db artist IDs """

__all__ = ["MusicDBIDBase", "MusicDBID"]

from hashlib import md5
from numpy import power
from urllib.parse import quote
import re
from .dbidmodval import MusicDBIDModVal
    

###############################################################################
# Artist ID I/O Class
###############################################################################
class MusicDBID:
    def __init__(self, db):
        self.aid = None
        self.amv = MusicDBIDModVal()
        self.getModVal = self.amv.get
        self.getGlobVal = self.amv.getGlobVal
        
    def getid(self, value):
        return self.aid.getArtistID(value)

    def getpsid(self, value):
        return self.aid.getArtistPseudoID(value)
    
    
###############################################################################
# Artist ID Base Class
###############################################################################
class MusicDBIDBase:
    def __init__(self, debug=False):
        self.debug = debug
        self.err = None

    def extractID(self, sval):
        groups = None if sval is None else sval.groups()
        artistID = None if groups is None else str(groups[0])
        return artistID

    def extractGroups(self, sval):
        groups = None if sval is None else sval.groups()
        return groups

    def testFormat(self, s):
        self.err = None
        if s is None:
            self.err = "None"
        elif not isinstance(s, str):
            self.err = type(s)
            
    def quoteIt(self, name):
        retval = name if "%" in name else quote(name)
        return retval

    def getErr(self):
        return self.err
    
    def getHashval(self, vals, addSize=False):
        if not isinstance(vals, list):
            raise ValueError("Must pass list of values. You passed [{0}]".format(vals))
        m = md5()
        for val in vals:
            try:
                enc = val.encode('utf-8')
            except Exception as error:
                continue
            m.update(enc)
            if addSize is True:
                m.update(str(len(val)).encode('utf-8'))
        hashval = m.hexdigest()
        return hashval
    
    def getIDFromHash(self, hashval, expo):
        iHash = int(hashval, 16)
        artistID = str(iHash) if expo < 1 else str(iHash % power(10, expo))
        return artistID
    
    def getArtistPseudoID(self, s):
        return s

    def getArtistIDFromPatterns(self, s, patterns):
        s = str(s)

        ######################################################
        # Test For Format
        ######################################################
        self.testFormat(s)
        if self.err is not None:
            return None

        ######################################################
        # Pattern Matching
        ######################################################
        for pattern in patterns:
            artistID = self.extractID(re.search(pattern, s))
            if artistID is not None:
                return artistID

        self.err = "NoMatch"
        return None

    
###############################################################################
# Self
###############################################################################
class MusicDBIDBaseDummy(MusicDBIDBase):
    def __init__(self, debug=False):
        super().__init__(debug)

    def getArtistID(self, s):
        return s