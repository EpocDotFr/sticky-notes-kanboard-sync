from sync_engine import SyncEngine
import click
import logging
import sys


@click.command()
def run():
    """Start the sync engine."""
    logging.basicConfig(
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%d/%m/%Y %H:%M:%S',
        stream=sys.stdout
    )

    logging.getLogger().setLevel(logging.INFO)

    sync_engine = SyncEngine()
    sync_engine.run()

if __name__ == '__main__':
    run()
