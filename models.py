# models.py
# classes that hold the database model for the music catalog

from sqlalchemy import Float, ForeignKey, Integer, LargeBinary, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from flacinfo import Flacinfo


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)


class Artist(Base):
    __tablename__ = "artists"

    name: Mapped[str] = mapped_column(String, nullable=False)


class Genre(Base):
    __tablename__ = "genres"

    name: Mapped[str] = mapped_column(String, nullable=False)


class Album(Base):
    __tablename__ = "albums"
    # important tags
    artist_id: Mapped[int] = mapped_column(Integer, ForeignKey("artists.id"))
    date: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    genre_id: Mapped[int] = mapped_column(Integer, ForeignKey("genres.id"))
    # optional tags
    discnumber: Mapped[int] = mapped_column(Integer, nullable=True)
    totaldiscs: Mapped[int] = mapped_column(Integer, nullable=True)
    discid: Mapped[str] = mapped_column(String, nullable=True)
    comment: Mapped[str] = mapped_column(String, nullable=True)
    compilation: Mapped[int] = mapped_column(Integer, nullable=True)
    albumartist: Mapped[str] = mapped_column(String, nullable=True)
    cuesheet: Mapped[str] = mapped_column(String, nullable=True)
    length: Mapped[float] = mapped_column(Float, nullable=False)
    cover_data: Mapped[bytes] = mapped_column(LargeBinary, nullable=True)
    cover_mime: Mapped[str] = mapped_column(String, nullable=True)
    cover_type: Mapped[int] = mapped_column(Integer, nullable=True)
    # relationships
    artists = relationship("Artist")
    genres = relationship("Genre")
    # constraints
    __table_args__ = (UniqueConstraint("artist_id", "date", "title", name="uix_artist_date_title"),)

    def __init__(self, ff: Flacinfo):
        """
        created from a Flacinfo object
        """
        self.date = ff.date
        self.title = ff.album
        self.cuesheet = ff.cuesheet
        self.discnumber = ff.discnumber
        self.totaldiscs = ff.totaldiscs
        self.discid = ff.discid
        self.comment = ff.comment
        self.compilation = ff.compilation
        self.albumartist = ff.albumartist
        self.length = ff.length
        self.cover_data = ff.cover_data
        self.cover_mime = ff.cover_mime
        self.cover_type = ff.cover_type
        # Foreign keys
        self.artist_id = ff.artist_id
        self.genre_id = ff.genre_id


class Track(Base):
    __tablename__ = "tracks"

    album_id: Mapped[int] = mapped_column(Integer, ForeignKey("albums.id"))
    trk_num: Mapped[int] = mapped_column(Integer, nullable=False)
    artist_id: Mapped[int] = mapped_column(Integer, ForeignKey("artists.id"))
    title: Mapped[str] = mapped_column(String, nullable=False)
    length: Mapped[float] = mapped_column(Float, nullable=False)
    # relationships
    albums = relationship("Album")
    artists = relationship("Artist")

    def __init__(self, album_id: int, tn: int, perf_id: int, title: str, length: float):
        self.album_id = album_id
        self.trk_num = tn
        self.artist_id = perf_id
        self.title = title
        self.length = length
