# Microsoft Sticky Notes to Kanboard sync

A Python script to synchronize notes from [Microsoft Sticky Notes](https://www.microsoft.com/en-us/store/p/microsoft-sticky-notes/9nblggh4qghw) to [Kanboard](https://kanboard.net/).

## Prerequisites

Python 3. May eventually works with Python 2 (not tested).

## Installation

Clone this repo, and then the usual `pip install -r requirements.txt`.

## Configuration

Copy the `.env.example` file to `.env` and fill in the configuration parameters.

Available configuration parameters are:

  - `TIMEZONE` Self-explanatory parameter
  - `KANBOARD_ENDPOINT` URL to the `jsonrpc.php` file of Kanboard's API
  - `KANBOARD_TOKEN` Token used to access your Kanboard instance API
  - `KANBOARD_PROJECT_ID` The project that will store your notes
  - `KANBOARD_COLUMN_ID` The column that will store our notes (define to `0` to automatically use the default column)
  - `KANBOARD_SWIMLANE_ID` The swimlane that will store our notes (define to `0` to automatically use the default swimlane)

## Usage

```
python run.py
```

TODO

## How it works

TODO