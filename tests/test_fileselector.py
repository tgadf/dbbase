from dbmaster import MasterDBs
from dbbase import MusicDBRootDataIO
from dbbase import FileSelector


def test_fileselector():
    dbs = MasterDBs().getDBs()
    rdio = MusicDBRootDataIO(dbs[0])
    fs = FileSelector(rdio=rdio)


if __name__ == "__main__":
    test_fileselector()