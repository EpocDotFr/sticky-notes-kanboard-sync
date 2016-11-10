from envparse import env, Env
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import watchdog.events
import olefile
import arrow
import click
import platform
import os
import time
import sys
import sqlite3


def debug(message, err=False, exit=False):
    click.echo('{} - {} - {}'.format(
        arrow.now(env('TIMEZONE')).format('MMM, D YYYY HH:mm:ss'),
        'ERR ' if err else 'INFO',
        message
    ), err=err)

    if exit:
        sys.exit(1)


class FileHandlerInterface(PatternMatchingEventHandler):
    path = None

    def __init__(self, patterns=None, path=None):
        self.path = path

        super().__init__(ignore_directories=True, patterns=patterns)

    def is_valid_event(self, event):
        if self.path != event.src_path:
            return False

        if event.event_type == watchdog.events.EVENT_TYPE_MODIFIED:
            return True
        elif event.event_type == watchdog.events.EVENT_TYPE_DELETED:
            debug(self.path + ' was unexpectedly deleted', err=True, exit=True)
        elif event.event_type == watchdog.events.EVENT_TYPE_MOVED:
            debug(self.path + ' was unexpectedly moved to ' + event.dest_path, err=True, exit=True)
        else:
            debug('Unhandled event type: ' + event.event_type, err=True)
            return False


class SNTFileHandler(FileHandlerInterface):
    def __init__(self, path):
        if not olefile.isOleFile(path):
            debug(path + ' isn\'t a valid Sticky Notes file', err=True, exit=True)

        super().__init__(patterns=['*.snt'], path=path)

    def on_any_event(self, event):
        if not self.is_valid_event(event):
            pass

        snt_file = olefile.OleFileIO(self.path)

        for storage in snt_file.listdir(storages=True, streams=False):
            note_id = storage[0] # It's an UUID-like string
            note_file = '0' # 0: Content in RTF format, 1: ??, 3: Raw content unicode-encoded

            with snt_file.openstream([note_id, note_file]) as note:
                print(note.read()) # TODO

        snt_file.close()


class SQLiteFileHandler(FileHandlerInterface):
    def __init__(self, path):
        super().__init__(patterns=['*.sqlite'], path=path)

    def on_any_event(self, event):
        if not self.is_valid_event(event):
            pass
            
        conn = sqlite3.connect('file:' + self.path + '?mode=ro', uri=True)
        conn.row_factory = sqlite3.Row

        cursor = conn.cursor()
        notes = cursor.execute('SELECT Text, Theme FROM Note')

        conn.close()

        for note in notes:
            print(note['Text'], note['Theme'])

class SyncEngine:
    platform_os = None
    platform_version = None

    sticky_notes_directory = None
    sticky_notes_filename = None
    sticky_notes_file_path = None

    def __init__(self):
        Env.read_envfile('.env')

        debug('Initializing')

    def run_observer(self, handler):
        debug('Watching ' + self.sticky_notes_file_path)

        observer = Observer()
        observer.schedule(handler, path=self.sticky_notes_directory, recursive=False)
        observer.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()

        observer.join()

    def run(self):
        self.discover_paths()

    def discover_paths(self):
        debug('Discovering Sticky Notes data file')

        handler = None

        self.platform_os = platform.system()
        self.platform_version = platform.release()

        if self.platform_os != 'Windows':
            debug('This script is only available on Windows Vista or above (for obvious reasons)', err=True, exit=True)

        debug('You are using Windows ' + self.platform_version)

        if self.platform_version == 'Vista':
            debug('Not yet implemented', exit=True) # TODO
        elif self.platform_version == '7':
            self.sticky_notes_directory = os.path.join(env('USERPROFILE'), 'AppData\Roaming\Microsoft\Sticky Notes')
            self.sticky_notes_filename = 'StickyNotes.snt'
            self.sticky_notes_file_path = os.path.join(self.sticky_notes_directory, self.sticky_notes_filename)

            if not os.path.isfile(self.sticky_notes_file_path):
                debug('Sticky Notes file not found', err=True, exit=True)

            handler = SNTFileHandler(self.sticky_notes_file_path)
        elif self.platform_version == '8':
            debug('Not yet implemented', exit=True) # TODO
        elif self.platform_version == '10':
            # Old app
            old_sticky_notes_directory = os.path.join(env('USERPROFILE'), 'AppData\Roaming\Microsoft\Sticky Notes')
            old_sticky_notes_filename = 'StickyNotes.snt'
            old_sticky_notes_file_path = os.path.join(old_sticky_notes_directory, old_sticky_notes_filename)

            # New app
            new_sticky_notes_directory = os.path.join(env('USERPROFILE'), 'AppData\Local\Packages\Microsoft.MicrosoftStickyNotes_8wekyb3d8bbwe\LocalState')
            new_sticky_notes_filename = 'plum.sqlite'
            new_sticky_notes_file_path = os.path.join(new_sticky_notes_directory, new_sticky_notes_filename)

            if os.path.isfile(old_sticky_notes_file_path) and os.path.isfile(new_sticky_notes_file_path): # Both exists, take the most recent
                if os.path.getmtime(new_sticky_notes_file_path) >= os.path.getmtime(old_sticky_notes_file_path): # New app is the most recently modified
                    self.sticky_notes_directory = new_sticky_notes_directory
                    self.sticky_notes_filename = new_sticky_notes_filename
                    self.sticky_notes_file_path = new_sticky_notes_file_path

                    handler = SQLiteFileHandler(self.sticky_notes_file_path)
                else: # Old app is the most recently modified
                    self.sticky_notes_directory = old_sticky_notes_directory
                    self.sticky_notes_filename = old_sticky_notes_filename
                    self.sticky_notes_file_path = old_sticky_notes_file_path

                    handler = SNTFileHandler(self.sticky_notes_file_path)
            elif os.path.isfile(old_sticky_notes_file_path) and not os.path.isfile(new_sticky_notes_file_path): # Old exists
                self.sticky_notes_directory = old_sticky_notes_directory
                self.sticky_notes_filename = old_sticky_notes_filename
                self.sticky_notes_file_path = old_sticky_notes_file_path

                handler = SNTFileHandler(self.sticky_notes_file_path)
            elif not os.path.isfile(old_sticky_notes_file_path) and os.path.isfile(new_sticky_notes_file_path): # New exists
                self.sticky_notes_directory = new_sticky_notes_directory
                self.sticky_notes_filename = new_sticky_notes_filename
                self.sticky_notes_file_path = new_sticky_notes_file_path

                handler = SQLiteFileHandler(self.sticky_notes_file_path)
            else:
                debug('Sticky Notes file not found', err=True, exit=True)
        else:
            debug('The Windows version you are running is not available', err=True, exit=True)

        self.run_observer(handler)


@click.command()
def run():
    sync_engine = SyncEngine()
    sync_engine.run()

if __name__ == '__main__':
    run()
