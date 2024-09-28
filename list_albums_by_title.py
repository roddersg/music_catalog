#! /usr/bin/env python3
# list_album_by_title.py
# provides a simplified album search by album title

import textwrap

import click
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tabulate import tabulate

from models import Album, Artist, Base, Genre

PROGNAME = "list_albums_by_title"
VERSION = "0.1.0"

# 0.2.0
# uses tabulate to display data, cjk-textwrap for CJK chars


@click.command()
@click.version_option(version=VERSION, prog_name=PROGNAME)
@click.argument("title")
def list_albums_by_title(title: str):
    """
    List albums by artist (using LIKE operator)
    Use '%' as wildcard
    """
    # connect to database
    engine = create_engine("sqlite:///musicdb.db")
    Session = sessionmaker(bind=engine)
    session = Session()
    Base.metadata.create_all(engine)

    # ask user for artist
    click.echo(f"Search for albums by title (using LIKE '{title}')\n")
    results = (
        session.query(Album, Artist, Genre)
        .join(Artist)
        .join(Genre)
        .filter(Album.title.like(title))
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
    list_albums_by_title()
