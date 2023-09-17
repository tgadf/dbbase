""" Music DB I/O Bases Class """

__all__ = ["MusicDBIOBase"]

from .dbrootdataio import MusicDBRootDataIO
from .dbidmodval import MusicDBIDModVal

    
##################################################################################################################
# Base I/O Class
##################################################################################################################
class MusicDBIOBase:
    def __init__(self, db, **kwargs):
        self.rdio = MusicDBRootDataIO(db, **kwargs)
        self.mv = MusicDBIDModVal()
        self.db = db
