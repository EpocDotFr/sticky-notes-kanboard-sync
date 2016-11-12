# Sticky Notes to Kanboard sync

A Python script to synchronize notes from Windows [Sticky Notes](https://en.wikipedia.org/wiki/Sticky_Notes) to [Kanboard](https://kanboard.net/).

Supported Sticky Notes versions are:

  - Windows Vista (Gadget for Windows Sidebar) (TODO)
  - Windows 7 (for technical reasons notes color can't be synchronized for this version)
  - Windows 8 (TODO)
  - Windows 10
    - Initial release version (for technical reasons notes color can't be synchronized for this version)
    - Anniversary Update version

## Prerequisites

Python 3. And obviously Windows.

## Installation

Clone this repo, and then the usual `pip install -r requirements.txt`.

## Configuration

Copy the `.env.example` file to `.env` and fill in the configuration parameters.

Available configuration parameters are:

  - `KANBOARD_ENDPOINT` URL to the `jsonrpc.php` file of Kanboard's API
  - `KANBOARD_TOKEN` Token used to access the Kanboard instance API
  - `KANBOARD_PROJECT_ID` The project that will store your notes
  - `KANBOARD_COLUMN_ID` and `KANBOARD_SWIMLANE_ID` Respectively the column and the swimlane that will be used to store your notes (set to `0` to automatically use the project's defaults)

## Usage

```
python run.py
```

No arguments available at this moment.

## How it works

Once started, this script will detect your Windows version to discover where the Sticky Notes data file is located (see
below). A [file watcher](https://github.com/gorakhargosh/watchdog) is then started to watch this file and will perform
Kanboard synchronization actions (using [its API](https://kanboard.net/documentation/api-json-rpc)) each time the file
is modified.

### Sticky Notes data files

There are three main type of data file used by Sticky Notes to store its data.

#### TODO: Gadget for Windows Sidebar

TODO

#### StickyNotes.snt

Applicable for:

  - Windows 7
  - Windows 8
  - Windows 10 (Initial release)

Usually located in the `%USERPROFILE%\AppData\Roaming\Microsoft\Sticky Notes` directory, it's an [OLE2](https://en.wikipedia.org/wiki/Compound_File_Binary_Format) file.

This script use the [olefile](https://bitbucket.org/decalage/olefileio_pl/) package to read them ([7-Zip](http://www.7-zip.org/) can also open them).

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

  - **(1)** A folder that contains a note's data. It is named after it seems to be the first 20 characters of a [GUID](https://en.wikipedia.org/wiki/Globally_unique_identifier) (counting hyphens)
  - **(2)** This file doesn't seem to contain interesting data. Changing a note's text or color doesn't impact this file
  - **(3)** The note's text in the [RTF](https://en.wikipedia.org/wiki/Rich_Text_Format) format
  - **(4)** The note's text without any formatting, but still it seems to contain special characters I don't know what they are used for
  - **(5)** [TrID](http://mark0.net/soft-trid-e.html) recognize this file as a [Sybase iAnywhere](https://en.wikipedia.org/wiki/Sybase_iAnywhere) database (either an [Advantage Database Server](https://en.wikipedia.org/wiki/Advantage_Database_Server) or [SQL Anywhere](https://en.wikipedia.org/wiki/SQL_Anywhere) one), however I wasn't able to open it either with a tool or with a Python package. Comparing the hex content of this file before and after changing notes color seems to change a specific value but without being able to read this file or without any documentation, it isn't possible to properly parse this file
  - **(6)** Seems to either contain the version of Sticky Notes or the version of the storage shema, in the hex format (e.g `02 00 00 00` for the Windows Seven's version)

#### plum.sqlite

Applicable for:

  - Windows 10 (Anniversary Update)

Usually located in the `%USERPROFILE%\AppData\Local\Packages\Microsoft.MicrosoftStickyNotes_8wekyb3d8bbwe\LocalState` directory, it's simply a [SQLite](https://en.wikipedia.org/wiki/SQLite) database file.
 
It can be opened by the native [sqlite3](https://docs.python.org/3.5/library/sqlite3.html) package.

Notes are stored in the `Note` table. Interesting fields are `Text` (note text in the [RTF](https://en.wikipedia.org/wiki/Rich_Text_Format)
format) and `Theme` (note color). All other fields and tables either doesn't seem to be used at all or aren't interesting.