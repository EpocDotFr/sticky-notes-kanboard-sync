from jsonrpcclient.http_client import HTTPClient
from envparse import env


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
                        column_id=env('KANBOARD_COLUMN_ID'),
                        swimlane_id=env('KANBOARD_SWIMLANE_ID')
                        )


def update_task(id, title, description=None, color_id=None):
    return send_request('createTask',
                        title=title,
                        description=description,
                        color_id=color_id
                        )
