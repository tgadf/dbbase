""" I/O For Data Produced or Ingested By MusicDBIO """

__all__ = ["MusicDBModValDataIO", "MusicDBDataIO"]

from utils import DirInfo, FileInfo, FileIO
from pandas import Series, DataFrame, concat
from .dbidmodval import MusicDBIDModVal
from .dbrootdataio import MusicDBRootDataIO
from .fileselector import FileSelector


###############################################################################
# ModVal Data IO
###############################################################################
class MusicDBModValDataIO:
    def __repr__(self):
        return f"MusicDBModValDataIO(db={self.rdio.db}, fileType={self.dataKey})"
    
    def __init__(self, rdio: MusicDBRootDataIO, **kwargs):
        self.verbose = kwargs.get('verbose', False)
        self.rdio = rdio
        
    def getKey(self, *args) -> 'str':
        fileType = args[0] if len(args) == 1 else None
        dataKey = f"ModVal{fileType}" if isinstance(fileType, str) else "ModVal"
        return dataKey
        
    def exists(self, modVal: int, *args) -> 'bool':
        return self.getFile(modVal, *args).exists()
    
    def getFile(self, modVal: int, *args) -> 'FileInfo':
        dataKey = self.getKey(*args)
        modValFile = self.rdio.getFilename(dataKey, modVal)
        return modValFile
    
    def get(self, modVal: int, force=False, *args) -> 'dict':
        if not self.exists(modVal, *args) or force is True:
            modValData = {}
        else:
            dataKey = self.getKey(*args)
            modValData = self.rdio.getData(dataKey, modVal)
            assert isinstance(modValData, (Series, DataFrame)), f"{dataKey} Data [{type(modValData)}] is not a Series/DataFrame"
            modValData = modValData.to_dict() if isinstance(modValData, Series) else modValData
        return modValData
    
    def save(self, modVal: int, modValData: dict, *args) -> 'None':
        dataKey = self.getKey(*args)
        assert isinstance(modValData, dict), f"{dataKey} Data [{type(modValData)}] is not a dict"
        modValData = Series(modValData)
        self.rdio.saveData(dataKey, modVal, data=modValData)


class MusicDBDataIO:
    def __repr__(self):
        return f"ModValDataDirIO(db={self.db})"
    
    def __init__(self, rdio: MusicDBRootDataIO, **kwargs):
        self.verbose = kwargs.get('verbose', False)
        self.rdio = rdio
        self.fs = FileSelector(rdio, **kwargs)
        self.io = FileIO()
        self.db = self.rdio.db
        self.mv = MusicDBIDModVal()
        
        self.mvdataio = MusicDBModValDataIO(rdio)
    
    ###########################################################################
    # ModVal Data IO
    ###########################################################################
    def existsModValData(self, modVal, force=False):
        fname = self.mdbdata.getModValFilename(modVal)
        if fname is None or force is True or (isinstance(fname, FileInfo) and not fname.exists()):
            return False
        return True
    
    def getModValData(self, modVal, force=False):
        fname = self.mdbdata.getModValFilename(modVal)
        modValData = {} if (force is True or not fname.exists()) else self.mdbdata.getModValData(modVal)
        modValData = modValData.to_dict() if isinstance(modValData, Series) else {}
        return modValData
    
    def saveModValData(self, modVal, modValData):
        modValData = Series(modValData) if isinstance(modValData, dict) else modValData
        self.mdbdata.saveModValData(data=modValData, modval=modVal)
    
    ###########################################################################
    # Raw Aggregated Data IO
    ###########################################################################
    def getRawAggFileTypeFilename(self, fType, dbid, **kwargs):
        modVal = self.mv.getModVal(dbid)
        fModVal = self.mv.getModGlobVal(modVal)
        globVal = self.mv.getGlobVal(dbid)
        fGlobVal = self.mv.getModGlobVal(globVal)
        fName = f"{self.db}-{fType}-mv-{fModVal}-gv-{fGlobVal}"
        dirVal = eval(f"self.mdbdir.getRaw{fType}ModValDataDir(modVal)")
        if not isinstance(dirVal, DirInfo):
            if kwargs.get('verbose') is True:
                print(f"self.mdbdir.getRaw{fType}ModValDataDir({modVal}) did not return a DirInfo")
            return None
        filename = dirVal.join(f"{fName}.p")
        return filename
        
    def getRawAggFileTypeData(self, fType, dbid, **kwargs):
        fname = self.getRawAggFileTypeFilename(fType, dbid)
        if fname is None or (isinstance(fname, FileInfo) and not fname.exists()):
            if kwargs.get('verbose') is True:
                print(f"File [{fname}] does not exist")
            return None
        aggData = self.io.get(fname)
        retval = aggData.get(dbid) if isinstance(aggData, (dict, Series)) else None
        if kwargs.get('verbose') is True and retval is None:
            print(f"Did not find [{dbid}] in [{fname}]")
        return retval
    
    ###########################################################################
    # SearchArtist Data IO
    ###########################################################################
    def getSearchArtistFilename(self, arg=None):
        fileType = "SearchArtist"
        try:
            retval = eval(f"self.mdbdata.get{fileType}Filename()")
        except:
            retval = None
        return retval
        
    def getSearchArtistData(self, arg=None):
        fileType = "SearchArtist"
        retval = eval(f"self.mdbdata.get{fileType}Data(arg)") if isinstance(arg,(int,str)) else eval(f"self.mdbdata.get{fileType}Data()")
        assert isinstance(retval,DataFrame),f"Trying to get SearchArtistData, but it is not a DataFrame [{type(retval)}]"
        return retval
    
    def saveSearchArtistData(self, searchArtistData):
        assert isinstance(searchArtistData, DataFrame), f"Trying to save SearchArtistData, but it is not a DataFrame [{type(searchArtistData)}]"
        cmd = f"self.mdbdata.save{fileType}Data(data=shuffleData)"
        try:
            eval(cmd)
        except:
            raise ValueError("Couldn't call {0}".format(cmd))
    
    ###########################################################################
    # Shuffle Data IO
    ###########################################################################
    def getShuffleFilename(self, modVal, globVal, fileType):
        try:
            retval = eval(f"self.mdbdata.get{fileType}Filename({modVal}, {globVal})")
        except:
            retval = None
        return retval
        
    def getShuffleData(self, modVal, globVal, fileType, force=False):
        fname = self.getShuffleFilename(modVal, globVal, fileType)
        if fname is None or force is True or (isinstance(fname, FileInfo) and not fname.exists()):
            return {}
        retval = eval(f"self.mdbdata.get{fileType}Data({modVal}, {globVal})")
        return retval
    
    def saveShuffleData(self, modVal, globVal, fileType, shuffleData):
        shuffleData = Series(shuffleData) if isinstance(shuffleData, dict) else shuffleData
        func = f"save{fileType}Data"
        if hasattr(self.mdbdata, func) and callable(getattr(self.mdbdata, func)):
            eval(f"self.mdbdata.{func}")(modVal=modVal, globval=globVal, data=shuffleData)
        else:
            raise ValueError(f"Could not call function {func} from mdbdata: [{self.mdbdata.dir()}]")
    
    ###########################################################################
    # ModVal FileType Data IO
    ###########################################################################
    def getFileTypeModValFilename(self, modVal, fileType):
        try:
            retval = eval(f"self.mdbdata.getModVal{fileType}Filename({modVal})")
        except:
            retval = None
        return retval
        
    def getFileTypeModValData(self, modVal, fileType, force=False):
        fname = self.getFileTypeModValFilename(modVal, fileType)
        if fname is None or force is True or (isinstance(fname, FileInfo) and not fname.exists()):
            return {}
        retval = eval(f"self.mdbdata.getModVal{fileType}Data({modVal})")
        return retval
    
    def saveFileTypeModValData(self, modVal, fileType, modValFileTypeData):
        modValFileTypeData = Series(modValFileTypeData) if isinstance(modValFileTypeData, dict) else modValFileTypeData
        cmd = f"self.mdbdata.saveModVal{fileType}Data(modval='{modVal}', data=modValFileTypeData)"
        try:
            eval(cmd)
        except:
            raise ValueError("Couldn't call {0}".format(cmd))
            
        

    ###########################################################################
    # ModVal Search FileType Data IO
    ###########################################################################
    def getSearchFileTypeModValSyntax(self, modVal, fileType, globVal):
        syntax = f"{self.db}-{fileType}-mv-{modVal}-gv-{globVal}"
        return syntax
    
    def getSearchFileTypeModValFilename(self, modVal, fileType, globVal):
        syntax = self.getSearchFileTypeModValSyntax(modVal, fileType, globVal)
        try:
            retval = eval(f"self.mdbdata.getModVal{fileType}Filename({modVal}, '{syntax}')")
        except:
            retval = None
        return retval

    def getSearchFileTypeModValData(self, modVal, fileType, globVal, force=False):
        fname = self.getSearchFileTypeModValFilename(modVal, fileType, globVal)
        if fname is None or force is True or (isinstance(fname, FileInfo) and not fname.exists()):
            return {}
        retval = self.io.get(fname)
        return retval
    
    def saveSearchFileTypeModValData(self, modVal, fileType, globVal, modValFileTypeData, force=False, merge=True):
        modValFileTypeData = Series(modValFileTypeData) if isinstance(modValFileTypeData, dict) else modValFileTypeData
        fname = self.getSearchFileTypeModValFilename(modVal, fileType, globVal)
        if merge is True and force is False:
            previousData = self.getSearchFileTypeModValData(modVal, fileType, globVal, force=force)
            if previousData is None:
                self.io.save(idata=modValFileTypeData, ifile=fname)
            else:
                if len(previousData) == 0:
                    saveData = modValFileTypeData
                else:
                    previousData = Series(previousData) if isinstance(previousData, dict) else previousData
                    saveData = concat([previousData,modValFileTypeData])
                    saveData = saveData[~saveData.index.duplicated()]
                self.io.save(idata=saveData, ifile=fname)
        else:
            self.io.save(idata=modValFileTypeData, ifile=fname)
            
        
            
                
    ###########################################################################
    # Get Recently Updated ModVal Files
    ###########################################################################
    def getNewFiles(self, modVal, fileType, expr='< 0 Days', force=False, tsFileType=None, **kwargs):
        verbose = kwargs.get('verbose', self.verbose)
        fileTypeFunc = "" if fileType in [None] else fileType
        tsFileType   = fileType if tsFileType is None else tsFileType
        
        if verbose: print(f"   ===> Getting New {self.db} ModVal={modVal} Files")
            
        cmd = f"self.mdbdir.getModVal{fileTypeFunc}DataDir({modVal}).glob('*.*', debug=False, lazy=False)"
        allFiles = eval(cmd)
        
        newFiles = self.fs.select(allFiles, modVal, tsFileType, expr, force, verbose=verbose)
        if verbose: print(f"   ===> Found [New={len(newFiles)} / All={len(allFiles)}]  (Call=[{cmd}])")
            
        return newFiles
    
    
    def getNewShuffleFiles(self, modVal, fileType, expr='< 0 Days', force=False, tsFileType=None, **kwargs):
        verbose = kwargs.get('verbose', self.verbose)
        fileTypeFunc = "" if fileType in [None] else fileType
        tsFileType   = fileType if tsFileType is None else tsFileType
        
        if verbose: print(f"   ===> Getting New {self.db} ModVal={modVal} Files")
            
        cmd = f"self.mdbdir.get{fileType}BaseDataDir().glob('*/{modVal}-{fileType}-DB.p', lazy=False, debug=False)"
        allFiles = eval(cmd)
        
        newFiles = self.fs.select(allFiles, modVal, tsFileType, expr, force, verbose=verbose)
        if verbose: print(f"   ===> Found [New={len(newFiles)} / All={len(allFiles)}]  (Call=[{cmd}])")
            
        return newFiles
    
    
    def getNewShuffleArtistFiles(self, modVal, fileType, expr='< 0 Days', force=False, tsFileType=None, **kwargs):
        verbose = kwargs.get('verbose', self.verbose)
        fileTypeFunc = "" if fileType in [None] else fileType
        tsFileType   = fileType if tsFileType is None else tsFileType
        
        if verbose: print(f"   ===> Getting New {self.db} ModVal={modVal} Files")
            
        cmd = f"self.mdbdir.get{fileType}BaseDataDir().glob('{modVal}/*-{fileType}-DB.p', lazy=False, debug=False)"
        allFiles = eval(cmd)
        
        newFiles = self.fs.select(allFiles, modVal, tsFileType, expr, force, verbose=verbose)
        if verbose: print(f"   ===> Found [New={len(newFiles)} / All={len(allFiles)}]  (Call=[{cmd}])")
            
        return newFiles
    
    
    def getNewMergedFiles(self, modVal, mergeType, expr='< 0 Days', force=False, **kwargs):
        verbose = kwargs.get('verbose', self.verbose)
        if verbose: print(f"   ===> Getting New {self.db} ModVal={modVal} Files")
        
        files = []
        if isinstance(mergeType.inputName,str):
            files.append(self.getFileTypeModValFilename(modVal, mergeType.inputName))
        files = [ifile for ifile in files if isinstance(ifile, FileInfo)]
        newFiles = self.fs.select(files, modVal, fileType=mergeType.outputName, expr=expr, force=force, verbose=verbose)
        if verbose: print(f"   ===> Found [New={len(newFiles)} / All={len(files)}]")
        return newFiles
    
    
    ###########################################################################
    # ModVal Summary Data IO
    ###########################################################################
    def getSummaryFilename(self, fileType):
        try:
            retval = eval(f"self.mdbdata.getSummary{fileType}Filename()")
        except:
            retval = None
        return retval
        
    def getSummaryData(self, fileType, force=False):
        retval = eval(f"self.mdbdata.getSummary{fileType}Data()")
        return retval
    
    def saveSummaryData(self, fileType, summaryData):
        cmd = f"self.mdbdata.saveSummary{fileType}Data(data=summaryData)"
        try:
            eval(cmd)
        except:
            raise ValueError("Couldn't call {0}".format(cmd))