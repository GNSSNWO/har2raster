import glob
import os
import json
import base64
import re


class Har(object):
    param = {
        "mimeTypes": ["jpeg", "jpg", "png"],
        "statusOK": 200,
        "tilenumRegexPattern": r"/\d+/\d+/\d+",
        "tileEncoding": "base64",
        "rootTileFolder": "cykloserver"
    }

    def __init__(self, filename):
        fullFilename = os.path.realpath(filename)
        if os.path.isfile(fullFilename):
            (directory, file) = os.path.split(fullFilename)
            if file.lower().endswith("har"):
                self.filepath = fullFilename
            else:
                raise IOError("Wrong file format of '{0:s}'!".format(file))
        else:
            raise IOError("File not exist!")

        content = self.getContent()
        
        for x in content["log"]["entries"]:
            mimeType = x["response"]["content"]["mimeType"]
            status = x["response"]["status"]
            imageExt = mimeType.split("/")[-1]
            if imageExt in self.param["mimeTypes"] and status == self.param["statusOK"]:
                requestUrl = x["request"]["url"]
                tileNums = Har.parseTileNumsFromRequest(requestUrl, self.param["tilenumRegexPattern"])
                if tileNums:
                    if x["response"]["content"]["encoding"] == self.param["tileEncoding"]:
                        imageText = x["response"]["content"]["text"]
                        Har.convertBase64ToFile(imageText, tileNums, "."+imageExt, self.param["rootTileFolder"])

    def getContent(self):
        with open(self.filepath) as f:
            return json.load(f)

    @staticmethod
    def parseTileNumsFromRequest(requestUrl,tilePattern):
        tileNums = None
        allTileNums = re.findall(tilePattern, requestUrl)
        if allTileNums:
            if len(allTileNums) == 1:
                tileNums = allTileNums[0].split('/')[1:]
            else:
                print("Not unique tile numbers for: '{0:s}'!".format(requestUrl))
        else:
            print("Unable to extract tile numbers for: '{0:s}' -> skipped".format(requestUrl))

        return tileNums

    @staticmethod
    def convertBase64ToFile(basestring, tileNums=["untitled"], ext="", rootImageFolder=""):
        folderPath = os.path.join(rootImageFolder, "/".join(tileNums[0:-1]))
        filePath = os.path.join(rootImageFolder, "/".join(tileNums))
        if folderPath != "":
            os.makedirs(folderPath, exist_ok=True)
            
        with open(filePath+ext, "wb") as fimage:
            imgdata = base64.b64decode(basestring)
            fimage.write(imgdata)
        

    def extractImages():
        pass


if __name__ == "__main__":
    dirPath = os.path.dirname(os.path.abspath(__file__))
    #harfile = os.path.join(dirPath, "../test/testData/www.kompass.de.har")
    harfile = os.path.join(dirPath, "../test/testData/www.cykloserver.cz.har")
    
    har = Har(harfile)
    pass

