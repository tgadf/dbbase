from dbbase import MusicDBDir, MusicDBData
from utils import DirInfo, FileIO
from os import getcwd


def test_dbdata_basic():
    dinfo = DirInfo(getcwd())
    finfo = dinfo.join("test_musicdbdata.p")
    FileIO().save(idata={'a': 1}, ifile=finfo)
    
    dbdir = MusicDBDir(path=dinfo)
    dbdata = MusicDBData(path=dbdir, fname="test_musicdbdata")
    dbfile = dbdata.getFilename()
    assert dbfile == finfo, f"dbdata files are not equal: [{dbfile}] vs [{finfo}]"
    
    data = dbdata.get()
    assert isinstance(data, dict) and len(data) == 1, f"Could not get correct data [{data}]"
    
    finfo.rmFile(debug=False)
    
    
def test_dbdata_args():
    dinfo = DirInfo(getcwd())
    dbdir = MusicDBDir(path=dinfo)
    dbdata = MusicDBData(path=dbdir, arg=True)
    dbdata.save(0, data={'a': 1})
    
    data = dbdata.get(0)
    assert isinstance(data, dict) and len(data) == 1, f"Could not get correct data [{data}]"
    
    dbfile = dbdata.getFilename(0)
    dbfile.rmFile(debug=False)
    
    
if __name__ == "__main__":
    test_dbdata_basic()
    test_dbdata_args()