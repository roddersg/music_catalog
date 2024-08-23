#! /usr/bin/env python3
# check_new_albums.py
# ;checks whether an album is already in the database
# prints out the albums that already in the database


import sys
from pathlib import Path

import click
from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from tqdm import tqdm

from flacinfo import Flacinfo
from models import Album, Artist, Base, Genre, Track

PROGNAME = "check_new_albums"
VERSION = "0.1.0"


def get_artist(session, name: str) -> int:
    """
    gets an artist, returns the artist id
    """
    result = session.query(Artist).filter_by(name=name).first()
    if result:
        return result.id
    else:
        # no artist found
        return -1


def check_new_album(session, ff: Flacinfo) -> bool:
    """
    Adds an album to the database, if it does not exist
    Returns True if the album was added
    """

    if get_artist(session, ff.artist) == -1:
        # must be new artist, so no album
        logger.info(f"{ff.artist}-{ff.date}={ff.album} is already in the database.")
        return False

    # let's check for the album
    result = (
        session.query(Album).filter_by(artist_id=ff.artist_id, date=ff.date, title=ff.album).first()
    )
    if result:
        # album already exists
        logger.info(f"{ff.artist}-{ff.date}={ff.album} is already in the database.")
        return False
    else:
        return True


def setup_logger(log_to_file: bool = False):
    """
    setup the logger
    """
    # remove previous loggers
    logger.remove()

    # log to file as well
    if log_to_file:
        logfile = "musicdb.log"
        f_fmt = "<green>{time:YYYY-MM-DD HH:mm:ss}</green>| "
        f_fmt += "<level>{level: <8}</level> | "
        f_fmt += "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan>"
        f_fmt += " - <level>{message}</level>"
        logger.add(logfile, level="WARNING", format=f_fmt)
    # stderr
    c_fmt = "<level>{level: <8}</level> | "
    c_fmt += "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan>"
    c_fmt += " - <level>{message}</level>"
    logger.add(sys.stdout, level="WARNING", format=c_fmt)


@click.command()
@click.version_option(version=VERSION, prog_name=PROGNAME)
@click.argument("filepath", type=click.Path(exists=True))
def check_new_albums_in_filepath(filepath):
    """
    check new albums (based on flac files) from filepath to database
    """
    # setup the logger
    setup_logger(log_to_file=True)

    # connect to database
    engine = create_engine("sqlite:///musicdb.db")
    Session = sessionmaker(bind=engine)
    session = Session()
    Base.metadata.create_all(engine)

    # add albums
    errors = 0
    print("Gathering and sorting albums...")
    files = sorted(list(Path(filepath).glob("**/*.flac")))
    print("Checking new albums")
    for file in tqdm(files):
        try:
            ff = Flacinfo(file)
            if not check_new_album(session, ff):
                errors += 1
                logger.warning(f"{ff.artist}-{ff.date}-{ff.album} already exists")
        except SQLAlchemyError as e:
            logger.error(f"check_new_album: {str(e)}")
    session.close()
    if errors:
        print(f"{errors} album(s) exit in database.")


if __name__ == "__main__":
    # filepath = "/home/rodney/Music/done/test"
    # filepath = "/home/rodney/Music/done/cdimages-new"
    # filepath = "/media/rodney/astor/music/lossless/cdimages/"
    check_new_albums_in_filepath()
