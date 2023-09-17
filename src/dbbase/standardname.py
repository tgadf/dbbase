""" Standard Artist Renaming Schemes """

__all__ = ["SummaryNameStandard", "MatchNameStandard"]

import re
from unidecode import unidecode
from pandas import Series


class NameStandardBase:
    def __init__(self, **kwargs):
        self.verbose = kwargs.get('verbose', False)

        ############################################################################################
        # Article Patterns
        ############################################################################################
        self.articlePatternBegin = re.compile(r"^(A|THE|LA|EL|LOS|DJ|MC)\s")
        self.articlePatternEnd = re.compile(r",\s(A|THE|LA|EL|LOS|DJ|MC)$")

        ############################################################################################
        # And/Ampersand Patterns
        ############################################################################################
        self.numParenPattern = re.compile(r"\s\((\d+)\)$")
        self.ampSpacePattern = re.compile(r"\s\&\s")
        self.ampJoinPattern = re.compile(r"\w\&\w")
        self.ampSemiPattern = re.compile(r"\s\&AMP;\s")
                
        ############################################################################################
        # HTML Patterns
        ############################################################################################
        self.htmlPatterns = {'&AGRAVE;': 'À', '&AACUTE;': 'Á', '&ACIRC;': 'Â', '&ATILDE;': 'Ã', '&AUML;': 'Ä', '&ARING;': 'Å', '&AELIG;': 'Æ', '&SZLIG;': 'SS', '&CCEDIL;': 'Ç', '&EGRAVE;': 'È', '&EACUTE;': 'É', '&ECIRC;': 'Ê', '&EUML;': 'Ë', '&#131;': 'Ƒ', '&IGRAVE;': 'Ì', '&IACUTE;': 'Í', '&ICIRC;': 'Î', '&IUML;': 'Ï', '&NTILDE;': 'Ñ', '&OGRAVE;': 'Ò', '&OACUTE;': 'Ó', '&OCIRC;': 'Ô', '&OTILDE;': 'Õ', '&OUML;': 'Ö', '&OSLASH;': 'Ø', '&#140;': 'Œ', '&#156;': 'Œ', '&#138;': 'Š', '&#154;': 'Š', '&UGRAVE;': 'Ù', '&UACUTE;': 'Ú', '&UCIRC;': 'Û', '&UUML;': 'Ü', '&#181;': 'Μ', '&YACUTE;': 'Ý', '&#159;': 'Ÿ', '&YUML;': 'Ÿ'}
        self.htmlDialectics1 = re.compile(r"\&\w(GRAVE|ACUTE|CIRC|TILDE|UML);")
        self.htmlDialectics2 = re.compile(r"\&(ARING|AELIG|SZLIG|CCEDIL|OSLASH);")

        ############################################################################################
        # Quote Patterns
        ############################################################################################
        self.posQuotePattern = re.compile(r"'S\s")
        self.chopQuotePattern = re.compile(r"\w'\w\w")
        self.endPosQuotePattern = re.compile(r"'S$")
        self.lilQuotePattern = re.compile(r"(LIL'\s|LI'L\s)")
        self.nQuotepattern = re.compile(r"(\sN'\s|\s'N'\s|\s'N\s)")
        self.nEndQuotepattern = re.compile(r"N'$")
        self.inQuotepattern = re.compile(r"IN'\s")
        self.contractQuotepattern1 = re.compile(r"N'T")
        self.contractQuotepattern2 = re.compile(r"I'M")
        
        
###############################################################################
# Rules For Renaming Summary Artist Names
###############################################################################
class SummaryNameStandard(NameStandardBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Order
        self.funcs = [self.numberParentheses]
    
    ###########################################################################
    # Primary Routine
    ###########################################################################
    def updateMedia(self, media):
        if not isinstance(media, list):
            return media
        
        retval = media
        for func in self.funcs:
            retval = [func(value) for value in retval]
        retval = sorted(list(set(retval)))
        return retval
    
    def updateNames(self, names):
        retval = names
        for func in self.funcs:
            retval = retval.apply(func)
        return retval
                
    def update(self, names, dtype, **kwargs):
        assert isinstance(names, Series), f"Names data [{type(names)}] is not a Series"
        assert dtype in ["Name", "Media"], f"Dtype [{dtype}] is not in [Name, Media]"

        if dtype == "Name":
            retval = self.updateNames(names)
        elif dtype == "Media":
            retval = names.apply(self.updateMedia)
            
        return retval
    
    def numberParentheses(self, value, posit=False):
        assert isinstance(value, str), f"Value [{value}] is not a string"
        retval = re.sub(self.numParenPattern, "", value).strip() if isinstance(re.search(self.numParenPattern, value), re.Match) else value.strip()
        return retval
        

###############################################################################
# Rules For Renaming Match Artist Names
###############################################################################
class MatchNameStandard(NameStandardBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Order
        self.funcs = [self.titlePunctuation, self.numberParentheses, self.conjunction,
                      self.singleQuote, self.nonAlphaNum, self.article, self.diacritics]
    
    ###########################################################################
    # Primary Routine
    ###########################################################################
    def updateMedia(self, media):
        if not isinstance(media, list):
            return media
        
        retval = [value.upper() for value in media]
        for func in self.funcs:
            retval = [func(value) for value in retval]
        retval = [value.upper() for value in media]
        retval = sorted(list(set(retval)))
        return retval
    
    def updateNames(self, names):
        retval = names.str.upper()
        for func in self.funcs:
            retval = retval.apply(func)
        retval = retval.str.upper()
        return retval
                
    def update(self, names, dtype, **kwargs):
        assert isinstance(names, Series), f"Names data [{type(names)}] is not a Series"
        assert dtype in ["Name", "Media"], f"Dtype [{dtype}] is not in [Name, Media]"

        if dtype == "Name":
            retval = self.updateNames(names)
        elif dtype == "Media":
            retval = names.apply(self.updateMedia)
            
        return retval

    def titlePunctuation(self, value, posit=False):
        assert isinstance(value, str), f"Value [{value}] is not a string"
        retval = value.replace(".", "")  # if value.endswith(".") else value
        return retval

    def diacritics(self, value, posit=False):
        assert isinstance(value, str), "Value [{value}] is not a string"
        asciiCnt = len(value.encode("ascii", "ignore"))
        retval = unidecode(value) if asciiCnt > 1 else value
        asciiCnt = len(retval.encode("ascii", "ignore"))
        retval = retval if asciiCnt > 1 else value
        return retval

    def article(self, value, posit=False):
        assert isinstance(value, str), f"Value [{value}] is not a string"
        retval = value
        
        mval = re.search(self.articlePatternBegin, retval)
        if isinstance(mval, re.Match):
            if self.verbose:
                print(f"{retval} ==> ", end="")
            retval = retval.replace(mval.group(), "").strip()
            if self.verbose:
                print(f"{retval}")
        mval = re.search(self.articlePatternEnd, retval)
        if isinstance(mval, re.Match):
            if self.verbose:
                print(f"{retval} ==> ", end="")
            retval = retval.replace(mval.group(), "").strip()
            if self.verbose:
                print(f"{retval}")
        
        return retval

    def numberParentheses(self, value, posit=False):
        assert isinstance(value, str), f"Value [{value}] is not a string"
        retval = re.sub(self.numParenPattern, "", value).strip() if isinstance(re.search(self.numParenPattern, value), re.Match) else value.strip()
        return retval

    def conjunction(self, value, posit=False):
        assert isinstance(value, str), f"Value [{value}] is not a string"
        retval = value
        
        # html dialectics with &
        mval = re.search(self.htmlDialectics1, retval)
        if isinstance(mval, re.Match):
            if self.verbose:
                print(f"{retval} ==> ", end="")
            retval = retval.replace(mval.group(), self.htmlPatterns[mval.group()])
            if self.verbose:
                print(f"{retval}")
        mval = re.search(self.htmlDialectics2, retval)
        if isinstance(mval, re.Match):
            if self.verbose:
                print(f"{retval} ==> ", end="")
            retval = retval.replace(mval.group(), self.htmlPatterns[mval.group()])
            if self.verbose:
                print(f"{retval}")
        
        # self.ampSpacePattern = re.compile(r"\s\&\s")
        for match in re.findall(self.ampSpacePattern, retval):
            if self.verbose:
                print(f"{retval} ==> ", end="")
            retval = retval.replace(match, " AND ")
            if self.verbose:
                print(f"{retval}")
            
        # self.ampJoinPattern  = re.compile(r"\w\&\w")
        for match in re.findall(self.ampJoinPattern, retval):
            if self.verbose:
                print(f"{retval} ==> ", end="")
            retval = retval.replace("&", " AND ")
            if self.verbose:
                print(f"{retval}")
            
        # self.ampSemiPattern  = re.compile(r"\s\&AMP;\s")
        for matchval in re.findall(self.ampSemiPattern, retval):
            if self.verbose:
                print(f"{retval} ==> ", end="")
            retval = retval.replace(matchval, "AND")
            if self.verbose:
                print(f"{retval}")
        
        return retval

    def singleQuote(self, value, posit=False):
        assert isinstance(value, str), f"Value [{value}] is not a string"
        retval = value
        retval = re.sub(self.posQuotePattern, "S ", retval).strip() if isinstance(re.search(self.posQuotePattern, retval), re.Match) else retval.strip()
        retval = re.sub(self.endPosQuotePattern, "S", retval).strip() if isinstance(re.search(self.endPosQuotePattern, retval), re.Match) else retval.strip()
        retval = re.sub(self.lilQuotePattern, "LIL ", retval).strip() if isinstance(re.search(self.lilQuotePattern, retval), re.Match) else retval.strip()
        retval = re.sub(self.nQuotepattern, " N ", retval).strip() if isinstance(re.search(self.nQuotepattern, retval), re.Match) else retval.strip()
        retval = re.sub(self.nEndQuotepattern, " N", retval).strip() if isinstance(re.search(self.nEndQuotepattern, retval), re.Match) else retval.strip()
        retval = re.sub(self.inQuotepattern, "IN ", retval).strip() if isinstance(re.search(self.inQuotepattern, retval), re.Match) else retval.strip()
        retval = re.sub(self.contractQuotepattern1, "NT", retval).strip() if isinstance(re.search(self.contractQuotepattern1, retval), re.Match) else retval.strip()
        retval = re.sub(self.contractQuotepattern2, "IM", retval).strip() if isinstance(re.search(self.contractQuotepattern2, retval), re.Match) else retval.strip()
        return retval

    def nonAlphaNum(self, value, posit=False):
        assert isinstance(value, str), f"Value [{value}] is not a string"
        retval = value.replace("$", "S")
        return retval

    def applyEntireFix(self, value, func):
        retval = func(value)
        return retval

    def applyWordFix(self, value, pos, func):
        words = value.split()
        words[pos] = func(words[pos])
        retval = " ".join(words)
        return retval