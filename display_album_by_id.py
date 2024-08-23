#! /usr/bin/env python3
# list_album_by_artist.py
# provides a simplified album listing

import click
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Album, Artist, Base, Genre, Track
from tabulate import tabulate
import textwrap

PROGNAME = "dispaly_album_by_id"
VERSION = "0.2.0"

# 0.2.0
# uses tabulate to display data, textwrap to shorten strings
# install cjk_textwrap for CJK chars
#

def truncate_with_elipses(s: str, max_length:int) -> str:
    if len(s) > max_length:
        return s[:max_length - 3] + "..."
    else:
        return s


def length_in_mmss(length: float) -> (int, int):
    ilength = int(length + 0.5)
    mm = ilength // 60
    ss = ilength % 60
    return mm, ss

def display_album_by_id(session, album_id: int, verbose: bool = False):
    """
    display album by id
    """
    result = (session.query(Album, Artist, Genre)
              .join(Artist)
              .join(Genre)
              .where(Album.id == album_id)
              .first()
    )
    if result:
        s = f"{'Album ID': <20} {album_id}\n"
        s += f"{'Album Artist': <20} {result.Artist.name}\n"
        s += f"{'Album Date': <20} {result.Album.date}\n"
        s += f"{'Album Title': <20} {result.Album.title}\n"
        s += f"{'Genre': <20} {result.Genre.name}\n"
        s += f"{'Discnumber': <20} {result.Album.discnumber}\n"
        s += f"{'Totaldiscs': <20} {result.Album.totaldiscs}\n"
        s += f"{'Compilation': <20} {result.Album.compilation}\n"
        s += f"{'AlbumArtist': <20} {result.Album.albumartist}\n"
        s += f"{'Comment': <20} {result.Album.comment}\n"
        mm, ss = length_in_mmss(result.Album.length)
        s += f"{'Length': <20} {mm:2}:{ss:02} min\n"
        if verbose:
            # s += "Tracks:\n"
            # s += f"{'Trk':3} {'Artist':<20} {'Title' : <40} {'Length':<6}\n"
            # s += f"{'-'*72}\n"
            # trks = session.query(Track, Artist).join(Artist).where(Track.album_id == album_id).all()
            # for trk in trks:
            #     perf = truncate_with_elipses(trk.Artist.name, 20)
            #     title = truncate_with_elipses(trk.Track.title,40)
            #     mm, ss = length_in_mmss(trk.Track.length)
            #     s += f"{trk.Track.trk_num:02d}  {perf:<20} {title:<40} {mm:2}:{ss:02}\n"

            trks = session.query(Track, Artist).join(Artist).where(Track.album_id == album_id).all()
            s += "Tracks:\n"
            headers = ['Trk', 'Performer', 'Title', 'Length']
            catalog = []
            for trk in trks:
                mm, ss = length_in_mmss(trk.Track.length)
                catalog.append([
                            trk.Track.trk_num,
                            textwrap.shorten(trk.Artist.name, 20, placeholder="..."),
                            textwrap.shorten(trk.Track.title, 50, placeholder="..."),
                            f"{mm:2}:{ss:02}"
                            ]
                )
            s += tabulate(catalog, headers)
        # finally print the string
        print(s)
    else:
        print("Album not found.")

@click.command()
@click.version_option(prog_name=PROGNAME, version=VERSION)
@click.argument("album_id", type=int)
@click.option("-v", "--verbose", is_flag=True, default=False, help="Display Track Information")
def display(album_id, verbose):
    """
    Display album information using album id
    """
    # connect to database
    engine = create_engine("sqlite:///musicdb.db")
    Session = sessionmaker(bind=engine)
    session = Session()
    Base.metadata.create_all(engine)

    display_album_by_id(session, album_id, verbose)
    session.close()


if __name__ == "__main__":
    display()
