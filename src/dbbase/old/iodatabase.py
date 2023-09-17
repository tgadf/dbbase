""" Base class for music db data names """

__all__ = ["MusicDBBaseData"]

from dbmaster import MasterParams
from .dbdata import MusicDBData
from .iodirbase import MusicDBBaseDirs


###############################################################################
# Container For Music DB BaseData
###############################################################################
class MusicDBBaseData:
    def __repr__(self):
        return f"MusicDBBaseData(db={self.db})"
        
    def __init__(self, mdbdir, **kwargs):
        self.verbose = kwargs.get('verbose', False)
        assert isinstance(mdbdir, MusicDBBaseDirs), "mdbdir [{mdbdir}] must be type MusicDBBaseDirs"
        
        self.mdbdir = mdbdir
        self.db = mdbdir.db
        self.data = {}

        mp = MasterParams()
        
        modValDataDir = mdbdir.getMusicDBDir("ModVal")
        metaDataDir = mdbdir.getMusicDBDir("Meta")
        summaryDataDir = mdbdir.getMusicDBDir("Summary")
        matchDataDir = mdbdir.getMusicDBDir("Match")
        
        #######################################################################
        # Data Classes
        #######################################################################
        
        # ModVal Data
        self.addData("ModVal", MusicDBData(path=modValDataDir, arg=True, suffix="DB"), addname=True)
        
        # Meta Data
        self.metaTypes = mp.getMetaTypes()
        self.summaryTypes = mp.getSummaryTypes()
        self.matchTypes = mp.getMatchTypes()
        for metaType in self.metaTypes.keys():
            self.addData(f"Meta{metaType}", MusicDBData(path=metaDataDir, arg=True, suffix=metaType), addname=True)
        
        # Summary (From Metadatas)
        # for metaType, summaryKeys in self.metaTypes.items():
        #    for key in summaryKeys:
        #        fname = "Summary{0}".format(key)
        #        self.addData(fname, MusicDBData(path=summaryDataDir, fname=fname))
        
        # Summary (From Summaries)
        for summaryType, summaryKeys in self.summaryTypes.items():
            for key in summaryKeys:
                fname = "Summary{0}".format(key)
                self.addData(fname, MusicDBData(path=summaryDataDir, fname=fname))
                
        # Match
        for key in self.matchTypes:
            fname = "Match{0}".format(key)
            self.addData(fname, MusicDBData(path=matchDataDir, fname=fname))
            
        if self.verbose:
            print(self.__repr__())
            self.clsdir()
            
    ###########################################################################
    # Info
    ###########################################################################
    def clsdir(self):
        print("  Callable:")
        for func in dir(self):
            if callable(eval(f"self.{func}")) and not func.startswith("__"):
                print(f"    {func}")
        
    ###########################################################################
    # Add/Get MusicDB Data To/From Data List
    ###########################################################################
    def addData(self, key, mdbDataIO, addname=False):
        assert isinstance(mdbDataIO, MusicDBData), f"mdbDataIO [{mdbDataIO}] is not a MusicDBData"
        assert key not in self.data.keys(), f"key [{key}] data is already set!"
        exec("self.get{0}Data  = mdbDataIO.get".format(key))
        exec("self.save{0}Data = mdbDataIO.save".format(key))
        if addname is True:
            exec("self.get{0}Filename  = mdbDataIO.getFilename".format(key))
        self.data[key] = mdbDataIO
            
    def setData(self, key, dataio):
        exec("self.get{0}Data  = dataio".format(key))
        self.data[key] = dataio
        
    def getData(self, key, arg=None):
        assert key in self.data.keys(), f"key [{key}] is not available"
        data = self.data[key]
        if data.arg is True:
            assert arg is not None, f"Arg must be set for dir [{data}]"
            retval = data.get(arg)
        else:
            assert arg is None, f"Arg is not needed for dir [{data}]"
            retval = data.get()
        return retval
        