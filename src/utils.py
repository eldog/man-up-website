import os

def get_path(origin_path, relative_path):
    return os.path.join(os.path.dirname(origin_path), relative_path)

def path_getter(origin_path):
    def getter(relative_path):
        return get_path(origin_path, relative_path)
    return getter