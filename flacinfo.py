#!/usr/bin/env python3

# class Flacinfo
# extracts and validates the information from a flac file,
# is_valid() is True if the flac file is valid

# fixes:
# - console logging messages, removes the date and time
# - add support for ALBUMARTIST
# - changed test for empty lists
# 0.3.0
# - changed the checking for the discnumber, totaldiscs (working better)
# - bug, "COMMENTS" => COMMENT
# 0.3.2
# - check the filenames as well, actual, cue, generated
# 0.3.3
# - option to log to file, default only long to terminal
#   uses the normal fmt line
# - changed FILE match pattern to include " and .flac
# fixed COMPILATION to either 1 or ""
# 0.3.4
# - verbose option for file, showing all details
# - check for .flac before processing
# 0.3.5
# - changed aritstId, albumId and genreId to artist_id, album_id and genre_id following pep8
# todo:
# - tqdm progress bar, to show errors when running

import re
import sys
from pathlib import Path

import click
from loguru import logger
from mutagen import MutagenError
from mutagen.flac import FLAC
from tqdm import tqdm

VERSION = "0.3.4"
PROGNAME = "flacinfo"

logger.remove()
# logfile = "musicdb.log"
# fmt = "<green>{time:YYYY-MM-DD HH:mm:ss}</green>| <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
# logger.add(logfile, level="WARNING")
fmt = "<level>{level: <8}</level> | "
fmt += "<cyan>{name}</cyan>:<cyan>{function}</cyan>:"
fmt += "<cyan>{line}</cyan> - <level>{message}</level>"
logger.add(sys.stderr, level="WARNING", format=fmt)


# internal function
def getTagValue(au: FLAC, tag: str, default=None) -> str | None:
    """
    returns the tag value if present
    None if not present
    """
    tagValue = au.tags.get(tag, default)
    if tagValue is not None:
        return tagValue[0]
    else:
        return None


# parse discnumber or totaldiscs
def parse_value(value):
    if value is None:
        return 1
    elif isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            return None  # Invalid string that cannot be converted to int
    return value


class Flacinfo:
    """
    Extracts and validates the information from a flac file,
    is_valid() is True if the flac file is valid
    """

    def is_valid(self) -> bool:
        """
        Only use if is_valid() is True
        """
        return self.valid

    def __init__(self, filepath: str):
        # set validity to false, don't use if false
        self.valid = False
        # check file prescence and validate flac
        logger.info(f"Processing file: {filepath}")
        self.filepath = filepath
        try:
            p = Path(filepath).stat()
            au = FLAC(filepath)
        except MutagenError as e:
            logger.error(f"Mutagen {e} [{filepath}]")
            return None
        except FileNotFoundError as e:
            logger.error(f"File not found {e}. [{filepath}]")
            return None
        if au.tags is None:
            logger.error(f"No tags found, [{filepath}]")
            return None
        # extract the tags from the flac file
        self.artist = getTagValue(au, "ARTIST")
        self.album = getTagValue(au, "ALBUM")
        self.date = getTagValue(au, "DATE")
        self.genre = getTagValue(au, "GENRE")
        self.cuesheet = getTagValue(au, "CUESHEET")
        self.discnumber = getTagValue(au, "DISCNUMBER")
        self.totaldiscs = getTagValue(au, "TOTALDISCS")
        self.compilation = getTagValue(au, "COMPILATION")
        self.discid = getTagValue(au, "DISCID")
        self.comment = getTagValue(au, "COMMENT")
        # v0.2.0 albumartist is not always present, present only if multiple performers
        self.albumartist = getTagValue(au, "ALBUMARTIST")
        # get the flac total length--------------------------------------------------------
        if au.info.length is not None:
            self.length = float(au.info.length)
        # get the cover
        if au.pictures is not None:
            self.cover_data = au.pictures[0].data
            self.cover_mime = au.pictures[0].mime
            self.cover_type = au.pictures[0].type
        self.tracks: list = None
        # initialise ids, to None, will get gathered in the sql
        self.artist_id = None
        self.album_id = None
        self.genre_id = None

        # Validation
        # validate the required tags
        # tags which must not be None, or out of range
        # any errors here return None
        try:
            assert self.artist is not None, "ARTIST is missing"
            assert self.album is not None, "ALBUM is missing"
            assert self.genre is not None, "GENRE is missing"
            assert self.cuesheet is not None, "CUESHEET is missing"
            assert self.date is not None and (
                1920 <= int(self.date) <= 2050
            ), "DATE is missing or out-of-range (1920-2050)"
        except AssertionError as e:
            logger.error(f"Required Tag '{e}'. [{filepath}]")
            return
        except ValueError as e:
            logger.error(f"DATE Tag '{e}'. [{filepath}]")
            return
        # validate Non-essential tags, cursory check
        # check DISCNUMBER, TOTALDISCS, COMPILATION
        try:
            if self.compilation:
                self.compilation = 1
            else:
                self.compilation = ""
            # elif int(self.compilation) > 1:
            #     self.compilation = 1
        except ValueError as e:
            # not serious, can continue
            logger.warning(f"COMPILATION Tag '{e}'. [{filepath}]")

        # Parse dn and td
        dn = parse_value(self.discnumber)
        td = parse_value(self.totaldiscs)

        # If dn is provided, td must also be provided
        if dn is not None and td is None:
            logger.error(f"'TOTALDISCS' is missing while 'DISCNUMBER' is present. [{filepath}]")
            return

        # If td is provided and dn is not, return False
        if td is not None and dn is None:
            logger.error(f"'DISCNUMBER' is missing while 'TOTALDISCS' is present. [{filepath}]")
            return

        # If both dn and td are None, set their default values to 1
        if dn is None and td is None:
            dn = 1
            td = 1
        else:
            # Parse dn and td
            dn = parse_value(dn)
            td = parse_value(td)

        # If dn or td is an invalid string, return False
        if dn is None or td is None:
            logger.error(f"Invalid 'DISCNUMBER' or 'TOTALDISCS'. [{filepath}]")
            return

        # If both dn and td are integers, check that td >= dn
        if isinstance(dn, int) and isinstance(td, int):
            if td < dn:
                logger.error(
                    f"'TOTALDISCS' must be greater than or equal to 'DISCNUMBER'. [{filepath}]"
                )
                return
        # OK

        # ------------------------------------------------------
        # check if COVER exists
        if self.cover_data is None:
            logger.error(f"No cover found. [{filepath}]")
        # cannot have a flac file of zero length
        if self.length == 0.0:
            logger.error(f"Flac Length Error. [{filepath}]")
            return
        # extract the tracks
        self.tracks = self.extract_tracks()
        if not self.tracks:
            # empty list
            return
        # ------------------------------------------------------
        # check the filenames
        actual_filename = Path(self.filepath).stem + ".flac"
        # pattern = re.compile(r"\s+FILE\s+(.*)\s+WAVE")
        pattern = re.compile(r"FILE\s+[\'\"](.*flac)[\'\"]\s+WAVE", re.IGNORECASE)
        m = pattern.search(self.cuesheet)
        if not m:
            logger.error(f"cuesheet FILE error. [{filepath}]")
            return
        cue_filename = m.group(1)
        gen_filename = f"{self.artist} - {self.album}.flac"
        if cue_filename != gen_filename:
            logger.error(f"Cue and Gen filename mismatch. [{filepath}]")
            return
        if cue_filename != actual_filename:
            logger.error(f"Cue and Actual filename mismatch. [{filepath}]")
            return

        # if you got here without any errors, then the file is valid
        self.valid = True

    def extract_track_offset(self, idxlist: list) -> float:
        """
        Extracts the track length from the index in seconds
        """
        tlen: float = 0.0
        for i in idxlist:
            # process only index 01
            if i[0] == "01":
                tlen = int(i[1]) * 60.0 + int(i[2]) + int(i[3]) / 75.0
        return tlen

    def extract_tracks(self) -> list:
        """
        Extracts the tracks from the cuesheet
        returns a list of track info [track_number, performer, title, track_offset]
        """
        # split the content based on 'tracks'
        tracks = re.split(
            r"^\s*TRACK\s+", self.cuesheet, flags=re.MULTILINE | re.DOTALL | re.IGNORECASE
        )

        # remove the top REM and FILE sections
        tracks.pop(0)
        # iterate through each track
        track_info = []
        for track in tracks:
            try:
                track_number = re.search(
                    r"^(\d+)", track, flags=re.MULTILINE | re.IGNORECASE
                ).group(1)
                title = re.search(r'TITLE "(.*?)"', track, flags=re.IGNORECASE).group(1)
                performer = re.search(r'PERFORMER "(.*?)"', track, flags=re.IGNORECASE)
                if performer is None:
                    performer = self.artist
                else:
                    performer = performer.group(1)
                indexlist: list = re.findall(r"INDEX (\d+) (\d+):(\d+):(\d+)", track, re.IGNORECASE)
                track_offset = self.extract_track_offset(indexlist)
                track_info.append([track_number, performer, title, track_offset])
            except Exception as e:
                logger.error(f"Error extracting track info {e}- {track} [{self.filepath}]")
                return
        # v 0.2.0
        # lets check for albumartist
        perf = track_info[0][1]
        for t in track_info[1:]:
            if t[1] != perf:
                self.albumartist = self.artist
                break

        # calculate the track lengths
        # # total length is passed as int in seconds
        for t in range(len(track_info)):
            # print(track_info[t])
            if (t + 1) == len(track_info):
                l: float = self.length - track_info[t][3]
            else:
                l: float = track_info[t + 1][3] - track_info[t][3]
                # mm = int(l) // 60
                # ss = int(l % 60 + 0.5)
                # tl = f"{mm}:{ss:02d}"
            # save the track length in seconds
            track_info[t][3] = int(l + 0.5)
        # return the track information as a list
        return track_info

    def pprint(self) -> str:
        """
        Prints out album details
        """
        s = f"{self.filepath}\n"
        s += f"  Artist      : {self.artist}\n"
        s += f"  Album       : {self.album}\n"
        s += f"  Date        : {self.date}\n"
        s += f"  Genre       : {self.genre}\n"
        s += f"  Comment     : {self.comment}\n"
        s += f"  Length      : {self.length}\n"
        s += f"  Compilation : {self.compilation}\n"
        s += f"  DiscNumber  : {self.discnumber}\n"
        s += f"  TotalDiscs  : {self.totaldiscs}\n"
        s += f"  DiscId      : {self.discid}\n"
        s += f"  AlbumArtist : {self.albumartist}\n"
        s += f"  Cover       : {self.cover_mime}, Type: {self.cover_type}\n"
        s += "Tracks:\n"
        for t in self.tracks:
            # s += f"{t[0]:>3} {t[1]:<30} {t[2]:<40} {t[3]:>5}\n"
            s += f"{t[0]:>3} {t[1]:<30} {t[2]:<40} {t[3] // 60}:{t[3] % 60:02d}\n"
        s += f"Artist ID : {self.artistId}\n"
        s += f"Album ID  : {self.albumId}\n"
        s += f"Genre ID  : {self.genreId}\n"
        return s


# -----------------------------------------------------------------------------------
@click.command()
@click.version_option(version=VERSION, prog_name=PROGNAME)
@click.argument("filepath", type=click.Path(exists=True, file_okay=True, dir_okay=True))
@click.option("-l", "--log", is_flag=True, help="log to file: musicdb.log", default=False)
@click.option("-v", "--verbose", is_flag=True, help="verbose output for file", default=False)
def validate(filepath: str, log: bool, verbose: bool):
    """
    validates flac files or recursively in a folder

    FILEPATH - a path to a file or directory (required).
    If a file is specified, full details will be printed.
    """

    if log:
        # log to file as well
        logfile = "musicdb.log"
        f_fmt = "<green>{time:YYYY-MM-DD HH:mm:ss}</green>| "
        f_fmt += "<level>{level: <8}</level> | "
        f_fmt += "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan>"
        f_fmt += " - <level>{message}</level>"
        logger.add(logfile, level="WARNING", format=f_fmt)

    p = Path(filepath)
    errors: int = 0
    if p.is_file():
        click.echo("Processing file...")
        if p.suffix == ".flac":
            ft = Flacinfo(filepath)
            if ft.is_valid():
                # full output if flag is set
                if verbose:
                    click.echo(ft.pprint())
                else:
                    # no errors
                    pass
            else:
                errors += 1
        else:
            click.echo("Not a flac file.")
            errors += 1
    else:
        click.echo("Processing folders...")
        files = sorted(list(Path(filepath).glob("**/*.flac")))
        for f in tqdm(files):
            ft = Flacinfo(f)
            if ft.is_valid() is False:
                errors += 1
    if errors > 0:
        click.echo(f"{errors} errors found. Check log for errors.")
    else:
        click.echo("No errors found.")


if __name__ == "__main__":
    validate()
