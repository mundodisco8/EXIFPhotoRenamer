"""Script to rename files using exiftools"""
# Made so far
#   1. Get files in a folder
#   2. Get their metadata
#   3. If a value exists, print, or don't if it doesn't
#
# Add Date and Time to Files that don't have it, or just have minimal EXIF data
# Some files (Whatsapp, screenshots, images generated via an app) don't normally have as
# many EXIF tags as a photo/video created with a Phone Camera.
# They normally have their file metadata, but the creation date on them is normally the
# date of the creaion of the file itself, and that is normally more recent than the
# original photo. Because photos are stored (in their folders) sorted by their date (file
# creation date, but on the phone itself), we might be able to infer their date of
# creation based on the previous/next file (if they are "camera" photos, and have a valid
# date)
# 1. On the JSON generation, mark all those photos without a date with a flag.
# 2. After all the photos have been analysed, and before we rename them, we can do a pass
#    and try to infer a date for them from previous/following files, based on their
#    current filename
# 3. Write the inferred date as a tag
# 4. Sort the JSON again
# 5. Now we can rename them.

import sys
from os import environ
from argparse import ArgumentParser
from json import load
from pathlib import Path
from support.support import lvl, debugPrint
from massRenamer.massRenamer import generateSortedJSON, massRenamer, showAllTags, fixDateless, metadataDict, doExifToolBatchProcessing
from typing import OrderedDict

def in_virtualenv():
    """Silly check for virtual environments"""
    return "VIRTUAL_ENV" in environ

# Parse CLI arguments
parser = ArgumentParser()
parser.add_argument("--photosDir",
                    help="Path to the folder containing the images", type=Path, required=False)
parser.add_argument("--printFileTags",
                    help="Path to file to be used and print all its tags", type=str, required=False)
parser.add_argument(
    "--dryRun", help='If passed, performs a dry run, where no renaming is performed. Name changes are printed on the screen instead', action='store_true')
parser.add_argument(
    "--skipJSON", help="If passed, skips the JSON file generation", action='store_true')
parser.add_argument(
    "--skipBatch", help="If passed, skips the ExifTool batch process", action='store_true')
parser.add_argument(
    "--fixDatelessInterActive", help="After having generated a sorted JSON, finds files without creation dates interactively", action='store_true')
parser.add_argument("--test", action='store_true')

args = parser.parse_args()
if not in_virtualenv():
    print("Not in VENV!")
    sys.exit()

from massRenamer.massRenamer import test

if args.test:
    test()
    # files = getListOfFiles(args.photosDir)
    # files = natsorted(files)
    # for file in files[0:100]:
    #     if isScreenShot(file):
    #         debugPrint(lvl.DEBUG, f"{file.name} is screenshot")
    exit(0)

if args.fixDatelessInterActive:
    # Load the JSON metadata: dict with filename as str key and metadataDict as value
    # Check if JSON exists, in case skipJSON has been passed, but no JSON exists
    if Path("data_file_sorted.json").is_file == False:
        debugPrint(lvl.ERROR, "Couldn't find the JSON file with the file data")
    else:
        # JSON file exists, process it.
        with open("data_file_sorted.json", "r") as readFile:
            jsonData = load(readFile)

    # Get the entries that are marked as dateless from the JSON
    datelessItems = [key for key in jsonData.keys() if jsonData[key]["dateless"] == True]
    fixDateless(jsonData, datelessItems, Path(args.photosDir), inferMethod="interactive")
    exit(0)

# Check that either photosDir or printFileTags has been passed
if args.photosDir is None and args.printFileTags is None:
    debugPrint(lvl.ERROR, "Either --photosDir or --printFileTags must be passed!")
    exit(0)

# Print all tags from file
if args.printFileTags:
    showAllTags(args.printFileTags)
    exit(0)

# Process a folder
if args.photosDir:
    photosDir = Path(args.photosDir)

    # Skips or not the batch processing, as it's the bit that takes most time
    if args.skipBatch == False:
        doExifToolBatchProcessing(photosDir)

    # Skip this if skipJSON was flagged
    if args.skipJSON == False:
        # Create JSON with metadata for postprocessing
        generateSortedJSON(photosDir)

    # Check if JSON exists, in case skipJSON has been passed, but no JSON exists
    if Path("data_file_sorted.json").is_file == False:
        debugPrint(lvl.ERROR, "Couldn't find the JSON file with the file data")
    else:
        # JSON file exists, process it. Pass the dryRun flag
        with open("data_file_sorted.json", "r") as readFile:
            jsonData: OrderedDict[str, metadataDict] = load(readFile)
        # Start filtering the JSON, and pass a subset of all the entries
        # in the sorted JSON. Make sure the sets are exclusive!
        # NOTE: fails checks because the dict comprehension returns a dict, not an ordered Dict, but it's close enough
        # I have to do a generator for typing to work
        screenshotsJson: OrderedDict[str, metadataDict] = {key: value for (key, value) in jsonData.items() if jsonData[key]['screenshot'] == True} # type: ignore we can't do orderedDict comprehension, so this wil always be flagged

        if screenshotsJson:

            massRenamer(screenshotsJson, args.photosDir, args.dryRun, "iPhone Screenshots", "ScreenShots")

        # Docs that are not screenshots and have no manufacturer data
        noCameraJson: OrderedDict[str, metadataDict] = {key: value for (key, value) in jsonData.items() if jsonData[key]['hasManufacturer'] == False and jsonData[key]['screenshot'] == False} # type: ignore we can't do orderedDict comprehension, so this wil always be flagged
        if noCameraJson:

            massRenamer(noCameraJson, args.photosDir, args.dryRun, "WhatsApp", "WhatsApp")
        # The rest, documents that have manufacturer data (and are not screenshots)
        cameraJson: OrderedDict[str, metadataDict] = {key: value for (key, value) in jsonData.items() if jsonData[key]['hasManufacturer'] == True and jsonData[key]['screenshot'] == False} # type: ignore we can't do orderedDict comprehension, so this wil always be flagged

        massRenamer(cameraJson, args.photosDir, args.dryRun, "iPhone")

        debugPrint(lvl.OK, f"Found {len(screenshotsJson.keys())} Screenshots")
        debugPrint(lvl.OK, f"Found {len(noCameraJson.keys())} Whatsapp")
        debugPrint(lvl.OK, f"Found {len(cameraJson.keys())} Camera")


###### TO DO:
# * It seems that iPhones (at least since the start of the use of HEIC) only use JPEG on bursts. Bursts can be identified as they have the `Burst UUID` datapoint
#   * Other jpegs seem to come from "tools" (apps, whatsapp) and they normally don't have a `DateTimeOriginal` tag, and their FileModifyDate is the export date from MacOS' Photos
# * At least on iOS, screenshots have the word `Screenshot` in the tag `User Comment`. They are also PNGs
# * iOS doesn't seem to use .mp4 either for video, so that could be another lead for whatsapp videos?


############## SCRIPTS ################
# # Load etJSON.json
# from json import load
# etData: List = []
# with open("etJSON.json", "r") as readFile:
#     etData = load(readFile)

# # Get all the tags captured - Only once
# all_keys = set().union(*(dict.keys() for dict in etData))

# # Get all the tags captured - All, with repeats
# all_keys = [item for dict in etData for item in list(dict.keys())]

# # Print n files that have the tagToPrint tag
# tagToPrint = "PNG:CreateDate"
# filesToList = 10
# listFilesTag = [dict['SourceFile'] for dict in etData if tagToPrint in dict.keys()]
# print('\n'.join(listFilesTag[0:filesToList]))

# # Print all the individual values for a certain tag
tagToPrint = "EXIF:Make"
set([dict[tagToPrint] for dict in etData if tagToPrint in dict.keys()])

# # Print all the filenames with a certain value in the tag
# tagToPrint = "EXIF:Make"
# tagValue = "Apple"
# [dict["SourceFile"] for dict in etData if tagToPrint in dict.keys() and tagValue in dict[tagToPrint]]

# # Histogram of tags
# from collections import Counter
# dateHistogram = Counter([item for dict in etData for item in list(dict.keys())])