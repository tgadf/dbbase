""" Base class for a musicdb data file w/ or w/o argument """

__all__ = ["MusicDBData"]

from utils import FileIO, FileInfo
from numpy import ndarray
from .dbdir import MusicDBDir


class MusicDBData:
    def __init__(self, path: MusicDBDir, arg=False, fname=None, prefix=None, suffix=None, ext=".p"):
        assert isinstance(path, MusicDBDir), f"path [{path}] is not a MusicDBDir"
        self.path = path
        
        assert isinstance(arg, bool), f"arg [{arg}] must be a bool"
        self.arg = arg
        
        assert isinstance(fname, str) or fname is None, f"fname [{fname}] must be a str or None"
        self.fname = fname
        
        assert isinstance(prefix, str) or prefix is None, f"prefix [{prefix}] must be a str or None"
        self.prefix = prefix
        
        assert isinstance(suffix, str) or suffix is None, f"suffix [{suffix}] must be a str or None"
        self.suffix = suffix
        
        assert isinstance(ext, str), f"ext [{ext}] must be a str"
        assert ext.startswith("."), f"ext [{ext}] is not formatted properly"
        self.ext = ext
        
        assert isinstance(self.fname, str) != arg, f"Must set either fname {fname} or arg [{arg}]"
        
    def getNumArgs(self):
        numargs = self.path.getNumArgs() + 1 if self.arg is True else self.path.getNumArgs()
        return numargs
        
    def getArgs(self, *args):
        numPathArgs = self.path.getNumArgs()
        dtypes = (tuple, list, ndarray)
        if numPathArgs <= 1:
            assert isinstance(args, dtypes), f"args [{args}] is not correct format"
            
        if numPathArgs == 1 and self.arg is True:
            assert len(args) == 2, "args [{args}] requires path and file args (2)"
            return {"Path": args[0], "Arg": args[1]}
        elif numPathArgs == 0 and self.arg is True:
            assert len(args) == 1, "args [{args}] requires file arg (1)"
            return {"Path": None, "Arg": args[0]}
        elif numPathArgs == 1 and self.arg is False:
            assert len(args) == 1, "args [{args}] requires path arg (1)"
            return {"Path": args[0], "Arg": None}
        elif numPathArgs == 0 and self.arg is False:
            assert len(args) == 0, "args [{args}] requires no arg (0)"
            return {"Path": None, "Arg": None}
        
    def getFilename(self, *args):
        fileArgs = self.getArgs(*args)
        path = self.path.get() if fileArgs["Path"] is None else self.path.get(fileArgs["Path"])
        path.mkDir()
        
        fname = None
        if self.arg is False:
            assert self.fname is not None, "Must set fname if there is no arg for DataBaseIO"
            fname = f"{self.fname}{self.ext}"
        else:
            arg = fileArgs["Arg"]
            if self.prefix is not None:
                fname = f"{self.prefix}-{arg}{self.ext}"
            elif self.suffix is not None:
                fname = f"{arg}-{self.suffix}{self.ext}"
            else:
                fname = f"{arg}{self.ext}"

        assert isinstance(fname, str), f"fname [{fname}] is not set!"
        return path.join(fname)
            
    def get(self, *args):
        return FileIO().get(self.getFilename(*args))

    def save(self, *args, **kwargs):
        data = kwargs.get('data')
        assert data is not None, "data is None!"
        finfo = self.getFilename(*args)
        assert isinstance(finfo, FileInfo), f"No savename [{finfo}]"
        FileIO().save(ifile=finfo, idata=data)
        
