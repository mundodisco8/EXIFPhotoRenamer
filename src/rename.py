"""Script to rename files using exiftools"""
# Made so far
#   1. Get files in a folder
#   2. Get their metadata
#   3. If a value exists, print, or don't if it doesn't
import sys
from os import environ
from argparse import ArgumentParser
from pathlib import Path
from support.support import lvl, debugPrint
from support.massRenamer import generateSortedJSON, massRenamer


def in_virtualenv():
    """Silly check for virtual environments"""
    return "VIRTUAL_ENV" in environ


# Parse CLI arguments
parser = ArgumentParser()
parser.add_argument("--photosDir",
                    help="Path to the folder containing the images", type=str, required=True)
parser.add_argument(
    "--dry-run", help='If passed, performs a dry run, where no renaming is performed. Name changes are printed on the screen instead', action='store_true')
parser.add_argument(
    "--skip-JSON", help="If passed, skips the JSON file generation", action='store_true')
args = parser.parse_args()

if not in_virtualenv():
    print("Not in VENV!")
    sys.exit()

# Path to Files -> TODO:will have to become an argument
# photosDir = Path( r"/media/joel/Backup/Fotos Mac Organizar/2016 - duplicates")
# Path With Sidecars
photosDir = Path(args.photosDir)
# Skip this if skip-JSON was flagged
if args.skip_JSON == False:
    generateSortedJSON(photosDir)

massRenamer(Path("data_file_sorted.json"), args.dry_run)
