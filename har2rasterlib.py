################################################################################
#
# har2rasterlib.py
#
# Module file with supporting functions for har2raster application,
# 
# Created: Peter Spanik, 16.9.2018
################################################################################

# Importing modulas
import sys,os,shutil

# Function definition
def getWorldFileParameters(bbox):
    xPixelSize = (bbox[2] - bbox[0])/256
    yPixelSize = -(bbox[3] - bbox[1])/256
    xRotation = 0.0
    yRotation = 0.0
    xCenter = bbox[0] + 0.5*xPixelSize
    yCenter = bbox[3] + 0.5*yPixelSize

    return (xPixelSize, yRotation, xRotation, yPixelSize, xCenter, yCenter)

def reqString2bbox(reqString):
    bbox = reqString.split('&')[-1][5:].split('%2C')
    return tuple(map(float, bbox))

def processReqFile(reqFileName):
    with open(reqFileName,'r') as finp:
        for lineTuple in enumerate(finp):
            bbox = reqString2bbox(lineTuple[1])
            worldFileParams = getWorldFileParameters(bbox)

    return worldFileParams

def getWorldFileExtension(ext):
    if len(ext) < 3 or len(ext) > 3:
        return ext + "w"
    else:
        return ext[0] + ext[-1] + "w"

def writeParamsToFile(reqFileName, worldParams):
    out = reqFileName.split('/')[-1].split('.')
    outFileName = out[0]
    with open(outFileName,'w') as fout:
        fout.write('\n'.join(str(element) for element in worldParams))

def progressBar(length, percent):
    barcode = length - 25
    done = round(float(barcode)*percent)
    return "[{0:s}{1:s}] {2:>5.1f}%".format(done*"#", (barcode-done)*" ", 100*percent)

def png2tif(folderName):
    mergedTiffFile = input("Set the output GTiff file name: ")

    # Create tif folder
    if os.path.exists("tif"):
        shutil.rmtree("tif")
    os.makedirs("tif")

    # Enter *.png folder
    os.chdir(folderName)

    # Looping through all *.png files
    listPNG = []
    for f in os.listdir():
        if f.split(".")[-1] == "png":
            listPNG.append(f)

    totalFiles = len(listPNG)
    print("\nApplication will convert PNG to TIF:")
    for count,file in enumerate(listPNG):
        if file.split(".")[-1] == "png":
            os.system("gdal_translate -of GTiff -a_srs EPSG:3857 {0:s} -q ../tif/{1:s}".format(
                file, file.split(".")[0] + ".tif"))
            
            # Update progressbar
            print(progressBar(80, float((count+1)/totalFiles)), end="\r")
            sys.stdout.flush()

    # Merging tif files
    os.chdir("../tif")
    os.mkdir("merged")
    print("\n\nMerging TIF files into one file {0:s} ...".format(mergedTiffFile))
    os.system(
        "gdal_merge.py -o merged/{0:s} -of GTiff -co COMPRESS=JPEG *.tif".format(mergedTiffFile))
