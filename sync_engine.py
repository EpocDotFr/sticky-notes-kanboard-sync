from file_handlers import SNTFileHandler, SQLiteFileHandler, INIFileHandler
from watchdog.observers import Observer
from envparse import env, Env
from utils import debug
import platform
import os
import time


class SyncEngine:
    """Class responsible of syncing the data from Sticky Notes to Kanboard.

    Reads configuration variables in the .env file and perform OS / Version identification. Once instanciated, the run()
    method must be called to actually run the sync engine."""
    platform_os = None
    platform_version = None

    sticky_notes_directory = None
    sticky_notes_filename = None
    sticky_notes_file_path = None

    handler = None

    def __init__(self):
        Env.read_envfile('.env')

        debug('Initializing')

    def run(self):
        """Run the file watcher of the sync engine, which will make things when the file is changed."""

        self.discover_paths()

        debug('Watching ' + self.sticky_notes_file_path)

        observer = Observer()
        observer.schedule(self.handler, path=self.sticky_notes_directory, recursive=False)
        observer.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            debug('Aborting')
            observer.stop()

        observer.join()

    def discover_paths(self):
        """Discover where is the Sticky Notes data file located."""
        self.platform_os = platform.system()

        if not self.platform_version: # If Windows version wasn't already set manually
            self.platform_version = platform.release()

        debug('Discovering Sticky Notes data file')

        if self.platform_os != 'Windows':
            debug('This script is only available on Windows Vista or above (for obvious reasons)', err=True, terminate=True)

        debug('You are using Windows ' + self.platform_version)

        if self.platform_version == 'Vista':
            self.sticky_notes_directory = os.path.join(env('USERPROFILE'), 'AppData\Local\Microsoft\Windows Sidebar')
            self.sticky_notes_filename = 'Settings.ini'
            self.sticky_notes_file_path = os.path.join(self.sticky_notes_directory, self.sticky_notes_filename)

            if not os.path.isfile(self.sticky_notes_file_path):
                debug('Sticky Notes file not found', err=True, terminate=True)

            self.handler = INIFileHandler(self)
        elif self.platform_version == '7':
            self.sticky_notes_directory = os.path.join(env('USERPROFILE'), 'AppData\Roaming\Microsoft\Sticky Notes')
            self.sticky_notes_filename = 'StickyNotes.snt'
            self.sticky_notes_file_path = os.path.join(self.sticky_notes_directory, self.sticky_notes_filename)

            if not os.path.isfile(self.sticky_notes_file_path):
                debug('Sticky Notes file not found', err=True, terminate=True)

            self.handler = SNTFileHandler(self)
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

                    self.handler = SQLiteFileHandler(self)
                else: # Old app is the most recently modified
                    self.sticky_notes_directory = old_sticky_notes_directory
                    self.sticky_notes_filename = old_sticky_notes_filename
                    self.sticky_notes_file_path = old_sticky_notes_file_path

                    self.handler = SNTFileHandler(self)
            elif os.path.isfile(old_sticky_notes_file_path) and not os.path.isfile(new_sticky_notes_file_path): # Old exists
                self.sticky_notes_directory = old_sticky_notes_directory
                self.sticky_notes_filename = old_sticky_notes_filename
                self.sticky_notes_file_path = old_sticky_notes_file_path

                self.handler = SNTFileHandler(self)
            elif not os.path.isfile(old_sticky_notes_file_path) and os.path.isfile(new_sticky_notes_file_path): # New exists
                self.sticky_notes_directory = new_sticky_notes_directory
                self.sticky_notes_filename = new_sticky_notes_filename
                self.sticky_notes_file_path = new_sticky_notes_file_path

                self.handler = SQLiteFileHandler(self)
            else:
                debug('Sticky Notes file not found', err=True, terminate=True)
        else:
            debug('This Windows version (' + self.platform_version + ') is invalid or is not managed', err=True, terminate=True)
