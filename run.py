from envparse import env, Env
import arrow
import click
import platform
import os


def debug(message, err=False, exit=False):
    click.echo('{} - {} - {}'.format(
        arrow.now(env('TIMEZONE')).format('MMM, D YYYY HH:mm:ss'),
        'ERR ' if err else 'INFO',
        message
    ), err=err)

    if exit:
        exit(1)


@click.command()
def run():
    Env.read_envfile('.env')

    debug('Initializing')

    platform_os = platform.system()
    platform_version = platform.release()
    sticky_notes_file = None

    if platform_os != 'Windows':
        debug('This script is only available on Windows Vista or above (for obvious reasons)', err=True, exit=True)

    if platform_version == 'Vista':
        pass
    elif platform_version == '7':
        pass
    elif platform_version == '8':
        pass
    elif platform_version == '10':
        sticky_notes_file = os.path.join(env('APPDATA'), 'Microsoft\Sticky Notes\StickyNotes.snt')
    else:
        debug('Unable to determine the Windows version your are running, aborting', err=True, exit=True)

    debug('You are using Windows ' + platform_version)

    if not os.path.isfile(sticky_notes_file):
        debug('Unable to determine the location of the Sticky Notes file (maybe it is not installed?)', err=True, exit=True)

if __name__ == '__main__':
    run()