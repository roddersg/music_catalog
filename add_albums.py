#! /usr/bin/env python3
# add_album.py


import sys
from pathlib import Path

from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from tqdm import tqdm

from flacinfo import Flacinfo
from models import Album, Artist, Base, Genre, Track

PROGNAME = "add_albums"
VERSION = "0.3.0"


def get_or_create_artist(session, name: str) -> int:
    """
    gets or creates an artist, returns the artist id
    """
    result = session.query(Artist).filter_by(name=name).first()
    if result:
        return result.id
    else:
        new_artist = Artist(name=name)
        session.add(new_artist)
        session.commit()
        return new_artist.id


def get_or_create_genre(session, name: str) -> int:
    """
    gets or creates a genre, returns the genre id
    """
    result = session.query(Genre).filter_by(name=name).first()
    if result:
        return result.id
    else:
        new_genre = Genre(name=name)
        session.add(new_genre)
        session.commit()
        return new_genre.id


def add_album(session, ff: Flacinfo) -> bool:
    """
    Adds an album to the database, if it does not exist
    Returns True if the album was added
    """
    ff.artist_id = get_or_create_artist(session, ff.artist)
    result = (
        session.query(Album).filter_by(artist_id=ff.artist_id, date=ff.date, title=ff.album).first()
    )
    if result:
        # album already exists
        return False
    else:
        ff.genre_id = get_or_create_genre(session, ff.genre)
        new_album = Album(ff)
        session.add(new_album)
        session.commit()
        ff.album_id = new_album.id
        for trk in ff.tracks:
            if ff.compilation or ff.albumartist:
                # may have multiple artists
                perf_id = get_or_create_artist(session, trk[1])
            else:
                perf_id = ff.artist_id
            new_track = Track(ff.album_id, trk[0], perf_id, trk[2], trk[3])
            session.add(new_track)
        session.commit()
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


def add_albums_in_filepath(filepath):
    """
    adds albums (based on flac files) from filepath to database
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
    print("Album location: ", filepath)
    print("Gathering and sorting albums...")
    files = sorted(list(Path(filepath).glob("**/*.flac")))
    print("Adding albums to musicdb.db")
    for file in tqdm(files):
        try:
            ff = Flacinfo(file)
            if not add_album(session, ff):
                errors += 1
                logger.warning(f"{ff.artist}-{ff.date}-{ff.album} already exists")
        except SQLAlchemyError as e:
            logger.error(f"add_album: {str(e)}")
    session.close()
    if errors:
        print(f"{errors} album(s) not added.")


if __name__ == "__main__":
    # filepath = "/home/rodney/Music/done/test"
    # filepath = "/home/rodney/Music/done/cdimages-new"
    # filepath = "/media/rodney/astor/music/lossless/cdimages/"
    filepath = "/srv/sata2/akiba/Music/cdimages-new/"
    add_albums_in_filepath(filepath)
