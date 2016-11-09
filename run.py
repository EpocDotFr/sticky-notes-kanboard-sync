import arrow
import click


def debug(message, err=False):
    click.echo('{} - {} - {}'.format(
        arrow.now(env('TIMEZONE')).format('MMM, D YYYY HH:mm:ss'),
        'ERR ' if err else 'INFO',
        message
), err=err)


@click.command()
def run():
    Env.read_envfile('.env')

    debug('Initializing')


if __name__ == '__main__':
    run()