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


def debug(message, err=False, exit=False):
    click.echo('{} - {} - {}'.format(
        arrow.now(env('TIMEZONE')).format('MMM, D YYYY HH:mm:ss'),
        'ERR ' if err else 'INFO',
        message
    ), err=err)

    if exit:
        sys.exit(1)


class FileHandlerInterface(PatternMatchingEventHandler):
    def __init__(self, patterns=None):
        super().__init__(ignore_directories=True, patterns=patterns)


class SNTFileHandler(FileHandlerInterface):
    path = None

    def __init__(self, path):
        self.path = path

        super().__init__(patterns=['*.snt'])

    def on_any_event(self, event):
        if self.path != event.src_path:
            pass

        snt_file = olefile.OleFileIO(self.path)

        if event.event_type == watchdog.events.EVENT_TYPE_MODIFIED:
            for stream in snt_file.listdir(storages=False):
                note_id = stream[0]

                if note_id in ['Metafile', 'Version']:
                    continue

                note_file = stream[1]

                if note_file == '0': # Contains the actual note content (RTF format)
                    with snt_file.openstream([note_id, note_file]) as note:
                        print(note.read()) # TODO

        elif event.event_type == watchdog.events.EVENT_TYPE_DELETED:
            debug(self.path + ' was unexpectedly deleted', err=True, exit=True)
        elif event.event_type == watchdog.events.EVENT_TYPE_MOVED:
            debug(self.path + ' was unexpectedly moved to ' + event.dest_path, err=True, exit=True)
        else:
            debug('Unhandled event type: ' + event.event_type, err=True)


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

        debug('Watching ' + self.sticky_notes_file_path)

    def discover_paths(self):
        handler = None

        self.platform_os = platform.system()
        self.platform_version = platform.release()

        debug('You are using Windows ' + self.platform_version)

        if self.platform_os != 'Windows':
            debug('This script is only available on Windows Vista or above (for obvious reasons)', err=True, exit=True)

        if self.platform_version == 'Vista':
            debug('Not yet implemented', exit=True) # TODO
        elif self.platform_version == '7':
            self.sticky_notes_directory = os.path.join(env('USERPROFILE'), 'AppData\Roaming\Microsoft\Sticky Notes')
            self.sticky_notes_filename = 'StickyNotes.snt'
            self.sticky_notes_file_path = os.path.join(self.sticky_notes_directory, self.sticky_notes_filename)

            if not olefile.isOleFile(self.sticky_notes_file_path):
                debug(self.sticky_notes_file_path + ' isn\'t a valid Sticky Notes file', err=True, exit=True)

            handler = SNTFileHandler(self.sticky_notes_file_path)
        elif self.platform_version == '8':
            debug('Not yet implemented', exit=True) # TODO
        elif self.platform_version == '10':
            self.sticky_notes_directory = os.path.join(env('USERPROFILE'), 'AppData\Local\Packages\Microsoft.MicrosoftStickyNotes_8wekyb3d8bbwe\LocalState')
            self.sticky_notes_filename = 'plum.sqlite'
            self.sticky_notes_file_path = os.path.join(self.sticky_notes_directory, self.sticky_notes_filename)

            if not os.path.isfile(self.sticky_notes_file_path):
                debug('Sticky Notes file not found in ' + self.sticky_notes_file_path + ', trying another location', err=True)

                self.sticky_notes_directory = os.path.join(env('USERPROFILE'), 'AppData\Roaming\Microsoft\Sticky Notes')
                self.sticky_notes_filename = 'StickyNotes.snt'
                self.sticky_notes_file_path = os.path.join(self.sticky_notes_directory, self.sticky_notes_filename)

                if not olefile.isOleFile(self.sticky_notes_file_path):
                    debug(self.sticky_notes_file_path + ' isn\'t a valid Sticky Notes file', err=True, exit=True)

                handler = SNTFileHandler(self.sticky_notes_file_path)
        else:
            debug('Unable to determine the Windows version your are running', err=True, exit=True)

        if not os.path.isfile(self.sticky_notes_file_path):
            debug('Sticky Notes file not found', err=True, exit=True)

        self.run_observer(handler)


@click.command()
def run():
    sync_engine = SyncEngine()
    sync_engine.run()

if __name__ == '__main__':
    run()
