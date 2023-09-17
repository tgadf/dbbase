""" Base class for music db directories """

__all__ = ["MusicDBRootPath", "MusicDBRootDataIO"]

from dbmaster import MasterPaths, MasterDBs, MasterMetas
from utils import DirInfo
from .dbdir import MusicDBDir
from .dbdata import MusicDBData
from .dbidmodval import getModVals

        
class MusicDBRootPath:
    def __repr__(self):
        return f"MusicDBRootPath(local={self.local}, mod={self.mod})"
    
    def __init__(self, **kwargs):
        local = kwargs.get('local', False)
        mod = kwargs.get('mod', False)
        
        mp = MasterPaths()
        if local is True:
            self.rawPath = mp.getMatchPath()
        elif mod is True:
            self.rawPath = mp.getModPath()
        else:
            self.rawPath = mp.getRawPath()
        self.modPath = mp.getModValPath()
        self.sumPath = mp.getSummaryPath()
        self.matchPath = mp.getMatchPath()
        
        
class MusicDBRootDataIO:
    def __repr__(self):
        return f"MusicDBRootDataIO(db={self.db})"
    
    def __init__(self, db, **kwargs):
        self.verbose = kwargs.get('verbose', False)
        assert MasterDBs().isValid(db), f"db [{db}] is not valid!"
        local = kwargs.get('local', False)
        self.isLocal = local
        self.mkDirs = kwargs.get('mkDirs', False)
        mod = kwargs.get('mod', False)
        root = MusicDBRootPath(local=local, mod=mod)
        mm = MasterMetas()
        dbname = db.lower()
        self.db = db
        self.dirs = {}
        self.data = {}
        
        #######################################################################
        # Root Directories
        #######################################################################
        rawDBName = f"artists-{dbname}"
        self.addDir("Raw", MusicDBDir(path=root.rawPath.join(rawDBName)))
        self.addDir("RawModVal", MusicDBDir(path=self.getDBDir("Raw"), arg=True))
        
        modDBName = f"artists-{dbname}-db"
        self.addDir("ModVal", MusicDBDir(path=root.modPath.join(modDBName)))
        
        self.addDir("Meta", MusicDBDir(path=root.modPath.join([modDBName, "metadata"])))
        
        sumDBName = f"db-{dbname}"
        self.addDir("Summary", MusicDBDir(path=root.sumPath.join(sumDBName)))
        
        matchDBName = f"db-{dbname}"
        self.addDir("Match", MusicDBDir(path=root.matchPath.join(matchDBName)))
        
        #######################################################################
        # Root Data
        #######################################################################
        self.addData("ModVal", MusicDBData(path=self.getDBDir("ModVal"), arg=True, suffix="DB"), addname=True)
        
        metaTypes = mm.getMetaTypes().keys()
        for metaType in metaTypes:
            self.addData(f"Meta{metaType}", MusicDBData(path=self.getDBDir("Meta"), arg=True, suffix=metaType), addname=True)
            
        summaryTypes = [summaryKey for summaryKeys in mm.getSummaryTypes().values() for summaryKey in summaryKeys]
        for summaryType in summaryTypes:
            fname = f"Summary{summaryType}"
            self.addData(fname, MusicDBData(path=self.getDBDir("Summary"), fname=fname))
            
        matchTypes = mm.getMatchTypes()
        for matchType in matchTypes:
            fname = f"Match{matchType}"
            self.addData(fname, MusicDBData(path=self.getDBDir("Match"), fname=fname))
            
        #######################################################################
        # Make Static and Dynamic Paths (if needed)
        #######################################################################
        self.createDirs()
            
        if self.verbose is True:
            print(self.__repr__())
            self.clsdir()
            
    ###########################################################################
    # Add/Get MusicDB Data To/From Data List
    ###########################################################################
    def addData(self, key, mdbDataIO, addname=False):
        assert isinstance(mdbDataIO, MusicDBData), f"mdbDataIO [{mdbDataIO}] is not a MusicDBData"
        assert key not in self.data.keys(), f"key [{key}] data is already set!"
        if any([key.startswith(value) for value in ["ModVal", "Summary"]]):
            exec("self.get{0}Data  = mdbDataIO.get".format(key))
            exec("self.save{0}Data = mdbDataIO.save".format(key))
            if addname is True:
                exec("self.get{0}Filename  = mdbDataIO.getFilename".format(key))
        self.data[key] = mdbDataIO

    def getDBData(self, key: str) -> 'MusicDBData':
        assert key in self.data.keys(), f"Invalid data key [{key}]. Available: {self.data.keys()}"
        dbdata = self.data[key]
        return dbdata

    def getFilename(self, key: str, *args, **kwargs):
        debug = kwargs.get('debug', False)
        verbose = True if debug is True else False
        
        if verbose:
            print(f"rdio.getFilename(key={key}, args={args}, **kwargs)")

        dbdata = self.getDBData(key)
        if verbose:
            print(f"  ==> dbData [{dbdata}]")
            print(f"  ==> Args: dbdata.arg = {dbdata.arg}, dbdata.numArgs = {dbdata.getNumArgs()}, args = {args})")
            
        numArgs = dbdata.getNumArgs()
        assert numArgs == len(args), f"data [{dbdata}] expects [{numArgs}] and you passed [{len(args)}] args"
        retval = dbdata.getFilename(*args) if numArgs > 0 else dbdata.getFilename()
            
        if verbose:
            print(f"  ==> DataType [{type(retval)}]")
        return retval
        
    def getData(self, key: str, *args, **kwargs):
        debug = kwargs.get('debug', False)
        verbose = True if debug is True else False
        
        if verbose:
            print(f"rdio.getData(key={key}, args={args}, **kwargs)")

        dbdata = self.getDBData(key)
        if verbose:
            print(f"  ==> dbData [{dbdata}]")
            print(f"  ==> Args: dbdata.arg = {dbdata.arg}, dbdata.numArgs = {dbdata.getNumArgs()}, args = {args})")
            
        numArgs = dbdata.getNumArgs()
        assert numArgs == len(args), f"data [{dbdata}] expects [{numArgs}] and you passed [{len(args)}] args"
        retval = dbdata.get(*args) if numArgs > 0 else dbdata.get()
            
        if verbose:
            print(f"  ==> DataType [{type(retval)}]")
        return retval
        
    def saveData(self, key: str, *args, **kwargs):
        verbose = kwargs.get('verbose', self.verbose)
        data = kwargs.get('data')
        assert data is not None, "data is None!"
        if verbose:
            print(f"rdio.saveData(key={key}, data={type(data)}, args={args}, **kwargs)")

        dbdata = self.getDBData(key)
        if verbose:
            print(f"  ==> dbData [{dbdata}]")
            print(f"  ==> Args: dbdata.arg = {dbdata.arg}, dbdata.numArgs = {dbdata.getNumArgs()}, args = {args})")
            
        numArgs = dbdata.getNumArgs()
        assert numArgs == len(args), f"data [{dbdata}] expects [{numArgs}] and you passed [{len(args)}] args"
        if numArgs > 0:
            dbdata.save(*args, data=data)
        else:
            dbdata.save(data=data)
        
    ###########################################################################
    # Add/Get MusicDB Dir To/From Dirs List
    ###########################################################################
    def addDir(self, key, path) -> 'None':
        assert isinstance(path, MusicDBDir), f"path [{path}] is not a MusicDBDir"
        assert key not in self.dirs.keys(), f"key [{key}] dirs is already set!"
        if any([key.startswith(value) for value in ["ModVal", "Summary"]]):
            exec(f"self.get{key}DataDir = path.get")
        self.dirs[key] = path
            
    def getDBDir(self, key) -> 'MusicDBDir':
        assert key in self.dirs.keys(), f"Invalid dir key [{key}]. Available: {self.dirs.keys()}"
        retval = self.dirs[key]
        return retval
        
    def getDir(self, key: str, *args, **kwargs) -> 'DirInfo':
        verbose = kwargs.get('verbose', self.verbose)
        if verbose:
            print(f"rdio.getDir(key={key}, args={args}, **kwargs)")
            
        dbdir = self.getDBDir(key)
        if verbose:
            print(f"  ==> dbDir [{dbdir}]")
            print(f"  ==> Args: dbdir.arg = {dbdir.arg}, dbdir.numArgs = {dbdir.getNumArgs()}, args = {args})")

        numArgs = dbdir.getNumArgs()
        assert numArgs == len(args), f"path [{dbdir}] expects [{numArgs}] and you passed [{len(args)}] args"
        retval = dbdir.get(*args) if numArgs > 0 else dbdir.get()
            
        if verbose:
            print(f"  ==> DirInfo [{retval}]")
        return retval
    
    def createDirs(self) -> 'None':
        if self.mkDirs is False:
            return
        for mdbdir in self.dirs.values():
            mdbdir.mkDir()
        for modVal in getModVals():
            mdbdir = self.getDir("RawModVal", modVal)
            mdbdir.mkDir()
                    
    ###########################################################################
    # Info
    ###########################################################################
    def clsdir(self) -> 'None':
        print("  Callable:")
        for func in dir(self):
            if callable(eval(f"self.{func}")) and not func.startswith("__"):
                print(f"    {func}")
                
    def isLocal(self) -> 'bool':
        return self.local