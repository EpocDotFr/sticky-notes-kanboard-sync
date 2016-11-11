from file_handlers import SNTFileHandler, SQLiteFileHandler
from watchdog.observers import Observer
from envparse import env, Env
from utils import debug
import platform
import os
import time


class SyncEngine:
    platform_os = None
    platform_version = None

    sticky_notes_directory = None
    sticky_notes_filename = None
    sticky_notes_file_path = None

    def __init__(self):
        Env.read_envfile('.env')

        debug('Initializing')

        self.platform_os = platform.system()
        self.platform_version = platform.release()

    def run_observer(self, handler):
        debug('Watching ' + self.sticky_notes_file_path)

        observer = Observer()
        observer.schedule(handler, path=self.sticky_notes_directory, recursive=False)
        observer.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            debug('Aborting')
            observer.stop()

        observer.join()

    def run(self):
        self.discover_paths()

    def discover_paths(self):
        debug('Discovering Sticky Notes data file')

        handler = None

        if self.platform_os != 'Windows':
            debug('This script is only available on Windows Vista or above (for obvious reasons)', err=True, terminate=True)

        debug('You are using Windows ' + self.platform_version)

        if self.platform_version == 'Vista':
            debug('Not yet implemented', terminate=True) # TODO
        elif self.platform_version == '7':
            self.sticky_notes_directory = os.path.join(env('USERPROFILE'), 'AppData\Roaming\Microsoft\Sticky Notes')
            self.sticky_notes_filename = 'StickyNotes.snt'
            self.sticky_notes_file_path = os.path.join(self.sticky_notes_directory, self.sticky_notes_filename)

            if not os.path.isfile(self.sticky_notes_file_path):
                debug('Sticky Notes file not found', err=True, terminate=True)

            handler = SNTFileHandler(self)
        elif self.platform_version == '8':
            debug('Not yet implemented', terminate=True) # TODO
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

                    handler = SQLiteFileHandler(self)
                else: # Old app is the most recently modified
                    self.sticky_notes_directory = old_sticky_notes_directory
                    self.sticky_notes_filename = old_sticky_notes_filename
                    self.sticky_notes_file_path = old_sticky_notes_file_path

                    handler = SNTFileHandler(self)
            elif os.path.isfile(old_sticky_notes_file_path) and not os.path.isfile(new_sticky_notes_file_path): # Old exists
                self.sticky_notes_directory = old_sticky_notes_directory
                self.sticky_notes_filename = old_sticky_notes_filename
                self.sticky_notes_file_path = old_sticky_notes_file_path

                handler = SNTFileHandler(self)
            elif not os.path.isfile(old_sticky_notes_file_path) and os.path.isfile(new_sticky_notes_file_path): # New exists
                self.sticky_notes_directory = new_sticky_notes_directory
                self.sticky_notes_filename = new_sticky_notes_filename
                self.sticky_notes_file_path = new_sticky_notes_file_path

                handler = SQLiteFileHandler(self)
            else:
                debug('Sticky Notes file not found', err=True, terminate=True)
        else:
            debug('The Windows version you are running is not available', err=True, terminate=True)

        self.run_observer(handler)
