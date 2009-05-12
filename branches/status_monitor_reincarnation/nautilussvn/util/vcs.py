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

def is_normal(path):
    return is_(path, "clean")
 
def is_added(path):
    return is_(path, "added")

def is_modified(path):
    return is_(path, "modified")
 
def is_deleted(path):
    return is_(path, "deleted")

def is_ignored(path):
    return is_(path, "ignored")

def is_locked(path):
    return False
 
def is_missing(path):
    return is_(path, "missing")

def is_conflicted(path):
    return is_(path, "conflict")
 
def is_obstructed(path):
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
 
def has_unversioned(path):
    return has_(path, "unknown")
 
def has_added(path):
    return has_(path, "added")
 
def has_modified(path):
    return has_(path, "modified")

def has_deleted(path):
    return has_(path, "deleted")
 
def has_ignored(path):
    return has_(path, "ignored")
 
def has_locked(path):
    return False

def has_missing(path):
    return has_(path, "missing")
 
def has_conflicted(path):
    return has_(path, "conflict")

def has_obstructed(path):
    return False

