from anyvc.workdir import get_workdir_manager_for_path

def is_(path, state):
    workdir_manager = get_workdir_manager_for_path(path)
    statuses_dictionary = dict([
        (status.abspath, status.state) 
        for status in workdir_manager.status(paths=(path,), recursive=False)
        if status.state == state
    ])
    if path in statuses_dictionary: return True
    return False

def is_working_copy(path):
    if get_workdir_manager_for_path(path): return True
    return False
 
def is_in_a_or_a_working_copy(path):
    if get_workdir_manager_for_path(path): return True
    return False
 
def is_versioned(path):
    workdir_manager = get_workdir_manager_for_path(path)
    statuses_dictionary = dict([
        (status.abspath, status.state) 
        for status in workdir_manager.status(paths=(path,), recursive=False)
        if status.state != "unknown"
    ])
    if path in statuses_dictionary: return True
    return False

def has_(path, state):
    workdir_manager = get_workdir_manager_for_path(path)
    statuses_dictionary = dict([
        (status.abspath, status.state) 
        for status in workdir_manager.status(paths=(path,), recursive=True)
        if status.state == state
    ])
    for another_path in statuses_dictionary.keys():
        if statuses_dictionary[another_path] == state: return True
    return False
