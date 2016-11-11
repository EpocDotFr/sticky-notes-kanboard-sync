from watchdog.events import PatternMatchingEventHandler
from utils import debug
import watchdog.events
import olefile
import sqlite3


class FileHandlerInterface(PatternMatchingEventHandler):
    sync_engine = None

    def __init__(self, sync_engine, patterns=None):
        self.sync_engine = sync_engine

        super().__init__(ignore_directories=True, patterns=patterns)

    def is_valid_event(self, event):
        if self.sync_engine.sticky_notes_file_path != event.src_path:
            return False

        if event.event_type == watchdog.events.EVENT_TYPE_MODIFIED:
            return True
        elif event.event_type == watchdog.events.EVENT_TYPE_DELETED:
            debug(self.sync_engine.sticky_notes_file_path + ' was unexpectedly deleted', err=True, terminate=True)
        elif event.event_type == watchdog.events.EVENT_TYPE_MOVED:
            debug(self.sync_engine.sticky_notes_file_path + ' was unexpectedly moved to ' + event.dest_path, err=True,
                  terminate=True)
        else:
            debug('Unhandled event type: ' + event.event_type, err=True)
            return False


class SNTFileHandler(FileHandlerInterface):
    def __init__(self, sync_engine):
        if not olefile.isOleFile(sync_engine.sticky_notes_file_path):
            debug(sync_engine.sticky_notes_file_path + ' isn\'t a valid Sticky Notes file', err=True, terminate=True)

        super().__init__(patterns=['*.snt'], sync_engine=sync_engine)

    def on_any_event(self, event):
        if not self.is_valid_event(event):
            pass

        snt_file = olefile.OleFileIO(self.sync_engine.sticky_notes_file_path)

        for storage in snt_file.listdir(storages=True, streams=False):
            note_id = storage[0]  # UUID-like string representing the note ID
            note_content_rtf_file = '0'  # RTF content of the note
            note_content_raw_file = '3'  # Raw text content of the note

            note_content_rtf = ''
            note_content_raw = ''

            with snt_file.openstream([note_id, note_content_raw_file]) as note_content:
                note_content_raw = note_content.read().decode()

            print(note_content_raw) # TODO

        snt_file.close()


class SQLiteFileHandler(FileHandlerInterface):
    def __init__(self, sync_engine):
        super().__init__(patterns=['*.sqlite'], sync_engine=sync_engine)

    def on_any_event(self, event):
        if not self.is_valid_event(event):
            pass

        conn = sqlite3.connect('file:' + self.sync_engine.sticky_notes_file_path + '?mode=ro', uri=True)
        conn.row_factory = sqlite3.Row

        cursor = conn.cursor()
        notes = cursor.execute('SELECT Text, Theme FROM Note')

        conn.close()

        for note in notes:
            print(note['Text'], note['Theme'])  # TODO
