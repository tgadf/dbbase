""" Classes to get db artist mod value """

__all__ = ["MusicDBIDModVal", "getModVals"]
         
from dbmaster import MasterBasic
from hashlib import md5


###############################################################################
# Artist ID ModVal Class
###############################################################################
class MusicDBIDModVal:
    def __init__(self):
        self.maxModVal = MasterBasic().getMaxModVal()
        self.get = self.getModVal
    
    def getDBIDHashVal(self, dbid):
        if isinstance(dbid, str):
            if dbid.isdigit() and dbid.isascii():
                retval = dbid
            else:
                m = md5()
                m.update(dbid.encode('utf-8'))
                hashval = m.hexdigest()
                retval = int(hashval, 16)
        elif isinstance(dbid, tuple):
            m = md5()
            for element in dbid:
                m.update(element.encode('utf-8'))
            hashval = m.hexdigest()
            retval = int(hashval, 16)
        elif isinstance(dbid, int):
            retval = dbid
        elif dbid is None:
            retval = None
        else:
            raise ValueError(f"Can not get mod value for [{dbid}]")
            
        return retval

    def getModGlobVal(self, modVal) -> 'str':
        assert isinstance(modVal, int), f"Passing non-int [{modVal}] to getModGlobVal()"
        retval = f"0{modVal}" if modVal < 10 else f"{modVal}"
        return retval
    
    def getDBID(self, dbid) -> 'str':
        if dbid is None:
            return None
        dbid = str(dbid) if isinstance(dbid, int) else dbid
        assert isinstance(dbid, str), f"dbid [{dbid}] is not a string"
        return f"0000{dbid}"
        
    def getModVal(self, dbid: str) -> 'int':
        hashval = self.getDBIDHashVal(dbid)
        dbidstr = self.getDBID(hashval)
        modVal = int(dbidstr) % self.maxModVal if isinstance(dbidstr, str) else None
        return modVal
        
    def getGlobVal(self, dbid: str) -> 'int':
        hashval = self.getDBIDHashVal(dbid)
        dbidstr = self.getDBID(hashval)
        modVal = int(dbidstr[:-2]) % self.maxModVal if isinstance(dbidstr, str) else None
        return modVal
    
    
###############################################################################
# Helper Function For Parsing/Merging
###############################################################################
def getModVals(modVal=None) -> 'list':
    if isinstance(modVal, range):
        retval = list(modVal)
    elif isinstance(modVal, list):
        retval = modVal
    elif isinstance(modVal, (str, int)):
        retval = [modVal]
    elif modVal is None:
        retval = MasterBasic().getModVals(listIt=True)
    else:
        raise TypeError("Unsure how to parse modVal [{modVal}] in getModVals()")
    return retval