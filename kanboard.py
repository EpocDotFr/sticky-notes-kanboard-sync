from jsonrpcclient.http_client import HTTPClient
from jsonrpcclient.request import Request
from jsonrpcclient import config
from envparse import env

config.validate = False

def send_request(request):
    """Send a JSON-RPC request to Kanboard."""
    jsonrpc_client = HTTPClient(env('KANBOARD_ENDPOINT'))
    jsonrpc_client.session.auth = ('jsonrpc', env('KANBOARD_TOKEN'))

    return jsonrpc_client.send(request)


def create_task(title, description=None, color_id=None):
    return Request('createTask',
                   title=title,
                   description=description,
                   color_id=color_id,
                   project_id=env('KANBOARD_PROJECT_ID'),
                   column_id=env('KANBOARD_COLUMN_ID', default=None),
                   swimlane_id=env('KANBOARD_SWIMLANE_ID', default=None)
                   )


def update_task(id, title=None, description=None, color_id=None):
    return Request('updateTask',
                   id=id,
                   title=title,
                   description=description,
                   color_id=color_id
                   )


def remove_task(id):
    return Request('removeTask',
                   task_id=id
                   )
