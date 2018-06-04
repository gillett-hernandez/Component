import os, json

def split(modulename):
    path, filename = os.path.split(modulename)
    base, ext = os.path.splitext(filename)
    return (path,base,ext)

def hash_of_file(filepath):
    with open(filepath,'r') as fd:
        _hash = hash(fd.read())
    return _hash

def format(name):
    return "{}_version.json".format(name)

def construct_filepath(modulename):
    path, base, ext = split(modulename)
    _filepath =  os.path.join(path,format(base))
    # print(modulename, path, base, ext, _filepath)
    return _filepath

def increment(modulename, should_create=False):
    filepath = construct_filepath(modulename)
    if not os.path.exists(filepath) and should_create:
        with open(filepath, "w") as fd:
            fd.write('{"version":[0,0,0,0]}')
    # with open(filepath, "rw") as fd:
    # fd = open(filepath, "rw")
    with open(filepath, "r") as fd:
        json_obj = json.load(fd)
    _hash = hash_of_file(modulename)

    if json_obj["hash"] != _hash:
        json_obj["version"][3] += 1
        json_obj["hash"] = _hash
        with open(filepath, "w") as fd:
            json.dump(json_obj, fd)
        return True
    else:
        return False

def get_version(modulename, should_create=False):
    filepath = construct_filepath(modulename)
    if not os.path.exists(filepath) and should_create:
        with open(filepath, "w") as fd:
            fd.write('{"version":[0,0,0,0]}')
    with open(filepath, "r") as fd:
        json_obj = json.load(fd)
    return json_obj["version"]

def render_version(modulename, should_create=False):
    version = get_version(modulename, should_create)
    _, name, _ = split(modulename)
    return "{} version {}.{}.{}-{}".format(name, *version[:4])

