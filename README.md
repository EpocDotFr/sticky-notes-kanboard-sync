# Sticky Notes to Kanboard sync

A Python script to synchronize notes from Windows [Sticky Notes](https://en.wikipedia.org/wiki/Sticky_Notes) to [Kanboard](https://kanboard.net/).

Supported Sticky Notes versions are:

  - Windows Vista
    - Gadget for Windows Sidebar (TODO)
  - Windows 7
    - Standalone application (for technical reasons notes color can't be synchronized for this version)
  - Windows 8
    - Standalone application (TODO)
  - Windows 10
    - Standalone application (for technical reasons notes color can't be synchronized for this version)
    - Universal Windows Platform application

## Prerequisites

Python 3.

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

TODO

## How it works

TODO