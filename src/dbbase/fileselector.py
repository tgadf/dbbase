""" Class For Selecting Files Based on Type and Data """

__all__ = ["FileSelector"]

from utils import RecentFiles, FileInfo
from .dbrootdataio import MusicDBRootDataIO


class FileSelector:
    def __repr__(self):
        return f"FileSelector(db={self.rdio.db})"
    
    def __init__(self, rdio: MusicDBRootDataIO, **kwargs):
        self.verbose = kwargs.get('verbose', False)
        assert isinstance(rdio, MusicDBRootDataIO), f"rdio {rdio} is not MusicDBBaseData"
        self.rdio = rdio
                
    def select(self, files: list, tsFile: FileInfo, expr='< 0 Days', force=False, **kwargs) -> 'list':
        verbose = kwargs.get('verbose', False)
        assert isinstance(files, list), f"files arg [{type(files)}] must be a list"
        
        if verbose is True:
            print(f"FileSelector.select(numFiles={len(files)}, tsFile={tsFile}, expr={expr}, force={force})")

        if force is True:
            retval = files
            if verbose is True:
                print(f"  Found {len(retval)} selected files because force is True")
            return retval

        rf = RecentFiles(files=files)
        if isinstance(tsFile, FileInfo):
            assert tsFile.exists(), f"File [{tsFile}] does not exist!"
            retval = rf.getFilesByModTime(expr, tsFile)
        else:
            retval = rf.getFilesByRecency(expr)
            
        assert isinstance(retval, list), f"RecentFiles retval [{type(retval)}] is not a list"
        
        if verbose is True:
            print(f"  Found {len(retval)} selected files.")
            
        return retval
