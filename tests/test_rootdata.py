from dbmaster import MasterDBs
from dbbase import MusicDBRootDataIO
from dbbase import MusicDBDir
from utils import DirInfo, FileInfo


def test_rootdata():
    dbs = MasterDBs().getDBs()
    rdio = MusicDBRootDataIO(dbs[0])

    finfo = rdio.getFilename("ModVal", 57)
    assert isinstance(finfo, FileInfo), f"{finfo} File is not a FileInfo"
    

def test_rootdirs():
    dbs = MasterDBs().getDBs()
    rdio = MusicDBRootDataIO(dbs[0])

    rootDirs = ["Raw", "ModVal", "Meta", "Summary", "Match"]
    for rootDir in rootDirs:
        dbdir = rdio.getDBDir(rootDir)
        assert isinstance(dbdir, MusicDBDir), f"{rootDir} DBDir is not a MusicDBDir"
        dinfo = rdio.getDir(rootDir)
        assert isinstance(dinfo, DirInfo), f"{rootDir} Dir is not a DirInfo"
    
    rootDirs = ["RawModVal"]
    for rootDir in rootDirs:
        dbdir = rdio.getDBDir(rootDir)
        assert isinstance(dbdir, MusicDBDir), f"{rootDir} DBDir is not a MusicDBDir"
        dinfo = dbdir.get(57)
        assert isinstance(dbdir, MusicDBDir), f"{rootDir} DBDir is not a MusicDBDir"
        dinfo = rdio.getDir(rootDir, 57)
        assert isinstance(dinfo, DirInfo), f"{rootDir} Dir is not a DirInfo"


if __name__ == "__main__":
    test_rootdata()
    test_rootdirs()