from flask import current_app


def get_to_account_from_project(allocates: list):
    """
    Copies the 'byUser' from the project field of an allocate to the field 'to'.
    """
    for allocate in allocates:
        if 'project' in allocate and 'to' not in allocate:
            project = current_app.data.find_one_raw('projects', allocate['project'])
            allocate['to'] = project['byUser']
