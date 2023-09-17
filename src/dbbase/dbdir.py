""" Base class for a musicdb dir (path) w/ or w/o argument """

__all__ = ["MusicDBDir"]

from utils import DirInfo
from inspect import signature


###############################################################################
# Base MusicDB Dir Class
###############################################################################
class MusicDBDir:
    def __repr__(self):
        return f"MusicDBDir(path={self.path}, arg={self.arg}, child={self.child})"
    
    def __init__(self, path, arg=False, child=None):
        assert isinstance(path, (DirInfo, MusicDBDir)), f"Invalid path: [{path}]"
        assert isinstance(arg, bool), f"arg [{arg}] must be a bool"
        assert isinstance(child, str) or child is None, f"child [{child}] must be a str or None"
        
        if isinstance(path, DirInfo):
            self.meth = path.get
            self.methParams = len(signature(self.meth).parameters)
        elif isinstance(path, MusicDBDir):
            self.meth = path.get
            self.methParams = path.getNumArgs()
            
        self.path = path
        self.arg = arg
        self.child = child
        
    def getNumArgs(self):
        numargs = self.methParams + 1 if self.arg is True else self.methParams
        return numargs
        
    def getPathArgs(self, *args):
        pathArgs = None
        assert isinstance(args, tuple), f"args [{args}] is not a tuple"
        assert len(args) == self.getNumArgs(), f"Expected [{self.getNumArgs()}] Args, but found [{len(args)}] (args={args})"
        assert len(args) <= 2, "MusicDBDir not ready for 2+ args"
            
        if self.arg is True:
            pathArgs = {"Path": None, "Arg": args[0]} if len(args) == 1 else {"Path": args[0], "Child": args[1]}
        elif self.arg is False:
            pathArgs = {"Path": args, "Arg": None} if len(args) > 0 else {"Path": None, "Arg": None}
            
        assert isinstance(pathArgs, dict), f"Error with pathArgs [{pathArgs}]"
        return pathArgs
    
    def getDirInfo(self, *args):
        pathArgs = self.getPathArgs(*args)
        
        dinfo = self.meth() if pathArgs["Path"] is None else self.meth(pathArgs["Path"])
        dinfo = dinfo.join(pathArgs["Arg"]) if self.arg is True else dinfo
        dinfo = dinfo.join(self.child) if self.child is not None else dinfo
        return dinfo
    
    def mkDir(self, *args):
        self.getDirInfo(*args).mkDir()
        
    def get(self, *args):
        return self.getDirInfo(*args)
    
    def getFiles(self, *args):
        return self.getDirInfo(*args).getFiles()