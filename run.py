from envparse import env, Env
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
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


class StickyNoteHandlerInterface(PatternMatchingEventHandler):
    def __init__(self, patterns=None):
        super().__init__(ignore_directories=True, patterns=patterns)


class Windows7StickyNoteHandler(StickyNoteHandlerInterface):
    def __init__(self):
        super().__init__(patterns=['*.snt'])

    def on_any_event(self, event):
        debug(event.src_path)
        debug(event.event_type)


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
            handler = Windows7StickyNoteHandler()
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
                handler = Windows7StickyNoteHandler()
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
