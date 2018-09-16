#!/usr/bin/env python3

################################################################################
#
# har2raster.py
#
# Application to convert HAR file of cached tiles from mapy.bratislava.sk to 
# PNG files. HAR file is JSON file with requests and responses, it is provided
# by Google Chrome in developer mode.
#
# Interactive input:
# harFileName - input name of HAR JSON file, follow the instruction in CLI
#
# Output: Folder with the similar name to input HAR file (dash separated) with
# "png" subfolder with tiles and its world files ("*.pgw"). If selected option
# to convert to TIFF files also "tif" folder with tiles and merged mosaic is
# included in output folder.
#
# Requirements: 
# - python3 interpreter installed with json,bas64,sys,os,shutil packages
# - module har2raster.py has to be available in the same directory
# - GDAL library installed (for conversion from PNG to TIFF)
# 
# Run as: $./har2png.py (be sure to add execution permission to file)
#
# Created: Peter Spanik, 16.9.2018
################################################################################

import json
import base64
import sys,os,shutil
import har2rasterlib as lib

harFileName = input("Set HAR file to process: ")

with open(harFileName, "r") as f:
    data = json.load(f)

# Create/overwrite folder with output images
datadir = os.path.join(os.getcwd(), "-".join(harFileName.split(".")[0:-1]))
if os.path.exists(datadir):
    shutil.rmtree(datadir)
os.makedirs(datadir)
os.makedirs(os.path.join(datadir, "png"))
os.chdir(datadir)

# Selection of valid entries (based on content of URL)
entries = data["log"]["entries"]
validEntries = []

for e in entries:
    if e["request"]["url"].rfind("image%2Fvnd.jpeg-png") != -1:
        validEntries.append(e)

# Looping throught valid entries
totalCount = len(validEntries)
print("\nConverting base64 representation from HAR file to PNG ...")
for count, entry in enumerate(validEntries):
    reqURL = entry["request"]["url"]
    resTEXT = entry["response"]["content"]["text"]
    ext = entry["response"]["content"]["mimeType"].replace("/", ".").replace("-", ".").split(".")[-1]
    
    # Update progressbar
    print(lib.progressBar(80, float((count+1)/totalCount)), end="\r")
    sys.stdout.flush()

    # Write tile basestring as image file
    with open("png/{0:>04d}.{1:s}".format(count,ext), "wb") as fimage:
        imgdata = base64.b64decode(resTEXT)
        fimage.write(imgdata)

    # Write corresponding world file 
    bbox = lib.reqString2bbox(reqURL)
    worldParams = lib.getWorldFileParameters(bbox)
    with open("png/{0:>04d}.{1:s}".format(count,lib.getWorldFileExtension(ext)), "w") as fworld:
        fworld.write("\n".join(str(element) for element in worldParams))

# Option to convert PNG to TIFF
processConversion = input("\n\nDo you wish to convert PNG to TIFF ([y]/[n]): ")
if processConversion == "y":
    lib.png2tif("png")
