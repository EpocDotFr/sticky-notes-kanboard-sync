from jsonrpcclient.http_client import HTTPClient
from jsonrpcclient import config
from envparse import env

config.validate = False

def send_request(method_name, *args, **kwargs):
    """Send a JSON-RPC request to Kanboard."""
    jsonrpc_client = HTTPClient(env('KANBOARD_ENDPOINT'))
    jsonrpc_client.session.auth = ('jsonrpc', env('KANBOARD_TOKEN'))

    return jsonrpc_client.request(method_name, *args, **kwargs)


def create_task(title, description=None, color_id=None):
    return send_request('createTask',
                        title=title,
                        description=description,
                        color_id=color_id,
                        project_id=env('KANBOARD_PROJECT_ID'),
                        column_id=env('KANBOARD_COLUMN_ID', default=None),
                        swimlane_id=env('KANBOARD_SWIMLANE_ID', default=None)
                        )


def update_task(id, title, description=None, color_id=None):
    return send_request('updateTask',
                        id=id,
                        title=title,
                        description=description,
                        color_id=color_id
                        )
