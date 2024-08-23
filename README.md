# music_catalog

1. Written in python using
    - sqlalchemy 2.0 for database
    - click for cmdline interface
    - tabulate for neatly printing tables of music data
    - tqdm to show progress in scanning using bars
    - mutagen to access flac and audio tags
    - loguru for generating logs
2. `musicdb.db` is the current database in use.  The database or logs are not cloned. Either choose from
   - `cdimages-new-musicdb.db` for limited albums, or
   - `astor-musicdb.db` for full catalog (~ 4.3 GB)
3. use test.ipynb for juypter notebook testing

## programs

### add_albums.py
Adds albums to the database, ignores duplicates

### display_album_by_id.py
Displays album using the album_id key.  Use -v for track listing

### flacinfo.py
Extracts the tags from flac files/folders (recursively), checks for errors.
The internal class Flacinfo()
- reads a flac file
- extracts the tags
- checks for errors in the tags
- creates an instance of Flacinfo() with the necessary tags
- use self.is_valid() to check whether the object was created sucessfully

### list_album_by_artist.py
Uses a string to search for the artist in the database using 'LIKE'.  Use '%' for wildcard.  Once the album is found, use the id to check/list contents using `display_album_by_id.py`

### models.py
The ORM for the database model used in the catalog, made up of the classes
- Artist holds id and name
- Album holds the album contents
- Genre holds the different genres
- Tracks holds the track information

### check_new_albums.py
Under construction/checking.
Scans folder/file for flacinfo
Using artist, date, album-title checks to see whether album is in the database
Returns True if album already present
