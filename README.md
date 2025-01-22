# EXIFPhotoRenamer

Playing a bit with Python in order to make a script that can rename my photos, based on their EXIF tags.

I want to store my photos using their date of creation to sort them, and things got totally out of control.

## Steps

As scanning the files can get really slow (specially for EXIFTool), we divided the work in multiple steps. That way we can run any of them, and start intermediate steps when some of the output files are generated.

### 1) Gather data with EXIFTool.

Run EXIFTool with a bunch of tags enabled, and create a "database" of sorts, a JSON file that contains all the info associated to a file. Only some tags are of interest.

### 2) Process data and Extract

Process the JSON data and keep all the info of interest. For example:

* Some files contain multiple date and time fields. I'll set some priorities and we will look for their presence in order to stablish what was the date and time of capture for the media file
* Some files don't have date and time, or even EXIF data at all. Some apps, like Whatsapp, scrap all the EXIF from files when it's shared (I guess for privacy reasons). We infer their date of creation based on filename and the date of creation of "nearby" files.
* File origin: we check fileds like "Make", "Model", "Software", ... to stablish the origin of the media file (an app, a camera, ...). We can use that info to name the file, or put it in a subfolder.

This step will generate a second "database", a list of media files and the data that we are interested on, ready to start the renaming process.

### 3) Rename

Once we have a list of files and their metadata, we can proceed to rename the files. Or we can do a dry-run, and see what the output would be!

## Getting the EXIF Tags

We use EXIFTool for that

TODO: Find the command to get the correct tags to JSON

Once we have a JSON file with the all the tags, we can access it with loadExifToolTagsFromFile.

## The MediaFile Class

I use MediaFile objects to store the relevant metadata for each media file (photo or video).

The MediaFile class has the follwing attributes

* _fileName: the path pointing to the media file
* _dateTime: a string with the date and time of creation in "YYYY:MM:DD hh:mm:ss" format, in UTC.
* _sidecar: if the file has a sidecar associated to it, path to it (so we can rename them together).
* _source: a string with the source of the photo (Camera, Phone, App, ...) so we can use that as the base of the new filename.

The MediaFile provides the following methods:

* fromExifTags (Class Method): takes the EXIF tags for a particular file (as a Dict, as EXIFTool exports them) and tries to gather all the metadat for the file (filename, date of creation, source, presence of an associated sidecar, ...) and creates a clas instance with the data found
* some getters: getTime, getFilename, ...

### Getting The Date of Creation - findCreationTime

Takes the output of an EXIFTool run (a list of files and their EXIF tags) and tries to get the creation date and time for each file.

1) It scans for the presence of certain date-related tags in a certain order. When one is found, uses it as time of capture. If the date we obtained is "naive" (doesn't contain timezone info), we try to get the offset from some EXIF tags that might be present. In any case, we end with either one or many offset-aware times of capture, or none at all.
1) If more than one times are found, we sort them and pick the oldest present in the file.

### Getting The Source - getFileSource

Determines the device or SW that generated the file.

1) Starts checking for the presence of `Make` and `Model`. If we have Model, we use it as our name string. If not, we check for Make.
1) If it doesn't, it probably is a media file of SW origin (Whatsapp, screenshots, etc.). Run a number of functions to try to determine its origin, again based on the presence of certain tags.


### Getting the sidecar - getSidecar:

For now, checks for iOS sidecars, which have the same name as the file, with `.aae` suffix, or append an `O` to the filename, and add the `.aae` suffix.

We can add more cases as we process files from other sources (Android, other cameras, ...).


## File Manipulation

We use this methods to write and read from disk

1) StoreMediaFile: as the last thing to do on step 2), once we have a list of instances of MediaFile, stores them to disk, so we can restart on step 3 without having to do all the pre-processing.
1) LoadMediaFileListFromFile: the first thing to do on step 3), once we have a representation of all the media files as MediaFile instances, we load that list of instances from disk.


## Plan

1) Grab a bunch of tags from a JSON and create a bunch of MediaClass instances
2) Store them in a file
3) See which ones have missing dates
4) Fix missing dates
5) Dry-run renaming
6) Point out to any file that might not be renamed? Missed sidecars,...