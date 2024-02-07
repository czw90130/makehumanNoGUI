class LicenseInfo(object):
    """
    License information for MakeHuman assets.
    Assets bundled with the official MakeHuman binary have been released as CC0.
    Assets created by third parties can be bound to different licensing conditions,
    which is why properties can be set as a dict of format:
        {"author": ..., "license": ..., "copyright": ..., "homepage": ...}
    """

    def __init__(self):
        """Create the default MakeHuman asset license. Can be modified for
        user-created assets.
        """
        self.author = "MakeHuman Team"
        self.license = "CC0"
        self.homepage = "http://www.makehumancommunity.org"
        self.copyright = "(c) www.makehumancommunity.org 2001-2020"
        self._keys = ["author", "license", "copyright", "homepage"]
        self._customized = False

    @property
    def properties(self):
        return list(self._keys)

    def setProperty(self, name, value):
        if name in self._keys:
            if getattr(self, name) != value:
                self._customized = True
                object.__setattr__(self, name, value)

    def __setattr__(self, name, value):
        # Assume that the LicenseInfo is not yet inited until self._customized is set
        if not hasattr(self, '_customized'):
            object.__setattr__(self, name, value)
            return
        if not hasattr(self, name):
            raise KeyError("Not allowed to add new properties to LicenseInfo")
        if name in self._keys:
            self.setProperty(name, value)
        else:
            object.__setattr__(self, name, value)

    def isCustomized(self):
        return self._customized

    def __str__(self):
        return """MakeHuman asset license:
Author: %s
License: %s
Copyright: %s
Homepage: %s""" % (self.author, self.license, self.copyright, self.homepage)

    def asDict(self):
        return dict( [(pname, getattr(self, pname)) for pname in self._keys] )

    def fromDict(self, propDict):
        for prop,val in list(propDict.items()):
            self.setProperty(prop, val)
        return self

    def fromJson(self, json_data):
        for prop in self.properties:
            if prop in json_data:
                self.setProperty(prop, json_data[prop])
        return self

    def copy(self):
        result = LicenseInfo()
        result.fromDict(self.asDict())
        result._customized = self.isCustomized()
        return result

    def updateFromComment(self, commentLine):
        commentLine = commentLine.strip()
        if commentLine.startswith('#'):
            commentLine = commentLine[1:]
        elif commentLine.startswith('//'):
            commentLine = commentLine[2:]
        commentLine = commentLine.strip()

        words = commentLine.split()
        if len(words) < 1:
            return

        key = words[0].rstrip(":")
        value = " ".join(words[1:])

        self.setProperty(key,value)

    def toNumpyString(self):
        def _packStringDict(stringDict):
            import numpy as np
            text = ''
            index = []
            for key,value in list(stringDict.items()):
                index.append(len(key))
                index.append(len(value))
                text += key + value
            text = np.fromstring(text, dtype='S1')
            index = np.array(index, dtype=np.uint32)
            return np.array([text, index], dtype=object)

        return _packStringDict(self.asDict())

    def fromNumpyString(self, text, index=None):
        def _unpackStringDict(text, index):
            stringDict = dict()
            last = 0
            for i in range(0,len(index), 2):
                l_key = index[i]
                l_val = index[i+1]

                key = str(text[last:last+l_key].tostring(), 'utf8')
                val = str(text[last+l_key:last+l_key+l_val].tostring(), 'utf8')
                stringDict[key] = val

                last += (l_key + l_val)
            return stringDict

        if index is None:
            text, index = text
        return self.fromDict( _unpackStringDict(text, index) )

def getAssetLicense(properties=None):
    """
    Retrieve the license information for MakeHuman assets.
    Assets bundled with the official MakeHuman binary have been released as CC0.
    Assets created by third parties can be bound to different licensing conditions,
    which is why properties can be set as a dict of format:
        {"author": ..., "license": ..., "copyright": ..., "homepage": ...}
    """
    result = LicenseInfo()
    if properties is not None:
        result.fromDict(properties)
        result._customized = False
    return result