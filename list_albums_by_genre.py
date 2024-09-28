#! /usr/bin/env python3
# list_album_by_genre.py
# provides a simplified album search by album genre

import textwrap

import click
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tabulate import tabulate

from models import Album, Artist, Base, Genre

PROGNAME = "list_albums_by_genre"
VERSION = "0.1.0"


@click.command()
@click.version_option(version=VERSION, prog_name=PROGNAME)
@click.argument("genre")
def list_albums_by_genre(genre: str):
    """
    List albums by genre (using LIKE operator)
    Use '%' as wildcard
    """
    # connect to database
    engine = create_engine("sqlite:///musicdb.db")
    Session = sessionmaker(bind=engine)
    session = Session()
    Base.metadata.create_all(engine)

    # ask user for artist
    click.echo(f"Search for albums by genre (using LIKE '{genre}')\n")
    results = (
        session.query(Album, Artist, Genre)
        .join(Artist)
        .join(Genre)
        .filter(Genre.name.like(genre))
        .order_by(Artist.name)
        .order_by(Album.date)
        .order_by(Album.title)
        .all()
    )
    if results:
        catalog = [
            [
                r.Album.id,
                textwrap.shorten(r.Artist.name, 20, placeholder="..."),
                r.Album.date,
                textwrap.shorten(r.Album.title, 50, placeholder="..."),
            ]
            for r in results
        ]
        headers: list = ["Id", "Artist", "Date", "Title"]
        print(tabulate(catalog, headers))
    else:
        print("No albums found")
    session.close()


if __name__ == "__main__":
    list_albums_by_genre()
