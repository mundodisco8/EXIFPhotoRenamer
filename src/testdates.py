from exiftool import ExifToolHelper, ExifTool, ExifToolAlpha
from datetime import datetime
from whenever import OffsetDateTime

TAGS_TO_EXTRACT: list[str] = ["-time:all", "-UserComment", "-Make", "-Model", "-Software", "-GPS:all"]

date = "2024-08-09T22:11:00-02:00"
offset = date[-6:]
with ExifToolHelper() as et:
    out = et.execute(
        "-v3",
        "-P",
        "-d",
        "%Y-%m-%dT%H:%M:%S%z",
        f"-alldates={date}",
        f"-OffsetTime={offset}",
        f"-OffsetTimeOriginal={offset}",
        f"-OffsetTimeDigitized={offset}",
        "..\\FotosTest\\A\\P1266346_NoTags.JPG",
    )
    print(out)


EXTRACT_ALL_TAGS_ARGS: list[str] = TAGS_TO_EXTRACT + [
    "-G1",
    "-a",
    "-s",
    "-j",
    "-r",
    "-d",
    "%Y-%m-%dT%H:%M:%S%:z",
    # The only thing missing here is the destination path
]
with ExifToolHelper() as et:
    datesList = et.execute_json(*EXTRACT_ALL_TAGS_ARGS, "..\\FotosTest\\A\\P1266346_NoTags.JPG")
print(datesList)

with ExifToolHelper() as et:
    datesList = et.execute(*EXTRACT_ALL_TAGS_ARGS, "..\\FotosTest\\A\\P1266346_NoTags.JPG")
print(datesList)

with ExifTool() as et:
    datesList = et.execute(*EXTRACT_ALL_TAGS_ARGS, "..\\FotosTest\\A\\P1266346_NoTags.JPG")
print(datesList)

with ExifToolAlpha() as et:
    datesList = et.execute(*EXTRACT_ALL_TAGS_ARGS, "..\\FotosTest\\A\\P1266346_NoTags.JPG")
print(datesList)
