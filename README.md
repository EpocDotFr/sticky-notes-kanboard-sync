# Sticky Notes to Kanboard sync

A Python script to synchronize notes from Windows [Sticky Notes](https://en.wikipedia.org/wiki/Sticky_Notes) to [Kanboard](https://kanboard.net/).

## Prerequisites

Python 3 and a Windows OS with Sticky Notes. **Only official Sticky Notes applications are supported** (not the ones made by third-parties).

Supported versions are the ones you found in:

  - Windows Vista (Gadget for [Windows Sidebar](https://en.wikipedia.org/wiki/Windows_Desktop_Gadgets))
  - Windows 7 (for technical reasons notes color can't be synchronized for this version)
  - Windows 8 (for technical reasons notes color can't be synchronized for this version)
  - Windows 10
    - Initial release (for technical reasons notes color can't be synchronized for this version)
    - Anniversary Update

## Installation

Clone this repo, and then the usual `pip install -r requirements.txt`.

## Configuration

Copy the `.env.example` file to `.env` and fill in the configuration parameters.

Available configuration parameters are:

  - `KANBOARD_ENDPOINT` URL to the `jsonrpc.php` file of Kanboard's API
  - `KANBOARD_TOKEN` Token used to access the Kanboard instance API
  - `KANBOARD_PROJECT_ID` The project that will store your notes
  - `KANBOARD_COLUMN_ID` The column that will be used to store your notes (set to empty to automatically use the first column)
  - `KANBOARD_SWIMLANE_ID` The swimlane that will be used to store your notes (set to empty to automatically use the default swimlane)

## Usage

**1. Run the script**

```
python run.py [--winversion]
```

  - `--winversion` Windows version. If defined, will force the script to not automatically detect the Windows version and use the one provided instead. Valid values are:
    - `Vista`
    - `7`
    - `8`
    - `10`

**2. Write some notes**

The very first line of the note's text, whatever the Sticky Notes version you use, will always be used as the Kanboard's task title.

## How it works

Once started, this script will detect your Windows version to discover where the Sticky Notes data file is located. A [file watcher](https://github.com/gorakhargosh/watchdog)
is then started to watch this file for each modification made.

This file watcher will perform the Kanboard synchronization actions (using its [JSON-RPC API](https://kanboard.net/documentation/api-json-rpc))
each time the file is finished to be modified, at the end of an idle timeout (5 seconds), because it seems all Sticky Notes versions
"streams" modifications directly to the storage file, thus making the "modified" event be raised a lot of times per seconds. This prevent
to send tens of HTTP requests in a couple of seconds to Kanboard. The [JSON-RPC batch](http://www.jsonrpc.org/specification#batch) requests technique
is used to reduce the number of HTTP requests sent to Kanboard, for obvious optimization reasons.

The script keeps track of synchronization data in the `data/sync.sqlite` [SQLite](https://en.wikipedia.org/wiki/SQLite) database file. It allow
the script to know what notes to create, delete or update in Kanboard.

## Sticky Notes data files retro-engineering

There are three main types of data file used by Sticky Notes to store its data, one for each primary version of Sticky
Notes, which are detailed below.

### Settings.ini

Applicable for:

  - Windows Vista (Gadget for Windows Sidebar)

Located in the `%USERPROFILE%\AppData\Local\Microsoft\Windows Sidebar` directory, it's a simple, [UCS-2 LE](https://en.wikipedia.org/wiki/Universal_Coded_Character_Set)
with BOM encoded, [INI](https://en.wikipedia.org/wiki/INI_file) file. It is also used to store all configuration parameters related to Windows Sidebar.

It can be opened by the native [configparser](https://docs.python.org/3.5/library/configparser.html) package.

This file's structure is the following (non-interesting parts have been deleted):

```
[Root]                                       (1)
...
[Section 1]                                  (2)
NoteCount="3"                                (3)
NoteState="2"                                (4)
ColorSaved="yellow"                          (5)
0="test%0D%0Aa%20new%20line%0D%0A%0D%0Aomg"  }
1="anoter%20one%0D%0A%0D%0Amultiline!"       } (6)
2="wohoo%0D%0A%0D%0Alook%20at%20this"        }
...
```

  - **(1)** This INI section contains general configuration parameters as well as the [GUID](https://en.wikipedia.org/wiki/Globally_unique_identifier) and location of each Windows Sidebar gadgets. Also contains the version of the configuration schema
  - **(2)** Each INI section starting by `Section` represents one gadget
  - **(3)** Total number of saved notes
  - **(4)** The note ID that is currently displayed on the gadget UI
  - **(5)** Notes color (can't be defined individually)
  - **(6)** The note's text, which is [URL encoded](https://en.wikipedia.org/wiki/Percent-encoding). Rich text formatting isn't supported. Keys within this INI section that are strictly integers are considered as the note's ID

References:

  - [Where does Windows Vista's Notes gadget store your notes? - Super User](http://superuser.com/a/119515/214377)

### StickyNotes.snt

Applicable for:

  - Windows 7
  - Windows 8
  - Windows 10 (Initial release)

Located in the `%USERPROFILE%\AppData\Roaming\Microsoft\Sticky Notes` directory, it's an [OLE2](https://en.wikipedia.org/wiki/Compound_File_Binary_Format) file.

This script use the [olefile](https://bitbucket.org/decalage/olefileio_pl/) package to open it.

This file's structure is the following:

```
+-- StickyNotes.snt
|   +-- 876de910-a6c3-11e6-9      (1)
|   |   +-- 1                     (2)
|   |   +-- 0                     (3)
|   |   +-- 3                     (4)
|   +-- d31a5886-a6ab-11e6-9
|   +-- da9fcf58-a6ab-11e6-9
|   +-- Metafile                  (5)
|   +-- Version                   (6)
```

  - **(1)** A folder that contains one note data (the note's ID). It is named after it seems to be the first 20 characters of a [GUID](https://en.wikipedia.org/wiki/Globally_unique_identifier) (counting hyphens). Don't know why it's limited to 20 chars
  - **(2)** This file doesn't seem to contain interesting data. Changing a note's text, color or position doesn't impact it. In addition, its content seems to be the same for each notes (e.g `11 20 04 00 00 00 00 00 00 00` on Windows Seven's version)
  - **(3)** The note's text in the [RTF](https://en.wikipedia.org/wiki/Rich_Text_Format) format
  - **(4)** The note's text, without any formatting, unicode encoded
  - **(5)** See [The Metafile mystery](#The Metafile mystery) below
  - **(6)** Seems to be the version of the storage shema, in the hex format (e.g `02 00 00 00` for the Windows Seven's version)

References:

  - [Where Sticky Notes are saved in Windows 10 1607 - Stack Overflow](http://stackoverflow.com/a/38823429/1252290)
  - [Sticky Notes - Forensics Wiki](http://www.forensicswiki.org/wiki/Sticky_Notes)
  - [Sticky Notes Analysis - Windows Incident Response](http://windowsir.blogspot.fr/2011/08/sticky-notes-analysis.html)

#### The Metafile mystery

There isn't any documentation about this file. So I ran it through [TrID](http://mark0.net/soft-trid-e.html), which recognize it as
a [Sybase iAnywhere](https://en.wikipedia.org/wiki/Sybase_iAnywhere) database file with the `.dbf` extension (although
it is reserved for [DBase](https://en.wikipedia.org/wiki/DBase) files). However I wasn't able to open it with tools dedicated to
open these file types.

This file also doesn't seems to be a [Windows Metafile](https://en.wikipedia.org/wiki/Windows_Metafile).

After opening it in a text editor, it looks like there's references to note IDs in its content, but not all that can exists in
the root `StickyNotes.snt` file.

Comparing the hexadecimal content of this file before and after changing notes color seems to change very specific values.

After some time, I found out that there is an hexadecimal pattern repeated throughout the file: `2C 00 00 00 00 00 00 00`, kind
of a separator or something.

### plum.sqlite

Applicable for:

  - Windows 10 (Anniversary Update)

Located in the `%USERPROFILE%\AppData\Local\Packages\Microsoft.MicrosoftStickyNotes_8wekyb3d8bbwe\LocalState` directory, it's a [SQLite](https://en.wikipedia.org/wiki/SQLite) database file.
 
It can be opened by the native [sqlite3](https://docs.python.org/3.5/library/sqlite3.html) package.

Notes are stored in the `Note` table. Interesting fields are `Text` (note text in the [RTF](https://en.wikipedia.org/wiki/Rich_Text_Format)
format) and `Theme` (note color). All other fields and tables either doesn't seem to be used at all or aren't interesting.

References:

  - [Where Sticky Notes are saved in Windows 10 1607 - Stack Overflow](http://stackoverflow.com/a/39197793/1252290)

## License

> DBAD Public License (see [LICENSE.md](LICENSE.md)).
>
> Copyright (C) 2016 Maxime "Epoc" G.

Please note that the RTF parser in this project wasn't written by me, but by an unknown person. I found this parser
somewhere in a ZIP file that I downloaded, and converted it to be used in Python 3. If you are the author, or if
you know him, I'll happily credit you if you contact me. The `Rtf2Markdown.py` file was written by me, with inspirations
from the `Rtf2Html.py` file.