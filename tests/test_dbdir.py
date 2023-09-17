from dbbase import MusicDBDir
from utils import DirInfo
from os import getcwd


def test_dbdir():
    dinfo = DirInfo(getcwd())
    mdbdir = MusicDBDir(path=dinfo)
    dirpath = mdbdir.get()
    assert dirpath.str == dinfo.str, f"mdbdir path [{dirpath}] does not equal input path [{dinfo}]"

    mdbdir = MusicDBDir(path=dinfo, arg=True)
    dirpatharg = mdbdir.get(0)
    dinfoarg = dinfo.join(0)
    assert dirpatharg == dinfoarg, f"mdbdir path [{dirpatharg}] does not equal input path [{dinfoarg}]"

    mdbdir = MusicDBDir(path=dinfo, child="test_musicdbdir")
    dirpathchild = mdbdir.get()
    dinfochild = dinfo.join("test_musicdbdir")
    assert dirpathchild == dinfochild, f"mdbdir path [{dirpathchild}] does not equal input path [{dinfochild}]"
    mdbdir.mkDir()
    assert dirpathchild.get().exists(), "mdbdir path [{dirpathchild.get()}] does not exist!"
    dirpathchild.get().rmDir()


if __name__ == "__main__":
    test_dbdir()
    