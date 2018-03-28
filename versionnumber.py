import os, json

def split(modulename):
    path, filename = os.path.split(modulename)
    base, ext = os.path.splitext(filename)
    return (path,base,ext)

def format(name):
    return "{}_version.json".format(name)

def increment(modulename):
    path, base, ext = split(modulename)
    filepath = os.path.join(path,format(base))
    print(modulename, path, base, ext, filepath)
    if not os.path.exists(filepath):
        with open(filepath, "w") as fd:
            fd.write('{"version":[0,0,0,0]}')
    # with open(filepath, "rw") as fd:
    # fd = open(filepath, "rw")
    with open(filepath, "r") as fd:
        json_obj = json.load(fd)
    json_obj["version"][3] += 1
    with open(filepath, "w") as fd:
        json.dump(json_obj, fd)

def get_version(modulename):
    path, base, ext = split(modulename)
    filepath = os.path.join(path,format(base))
    if not os.path.exists(filepath):
        with open(filepath, "w") as fd:
            fd.write('{"version":[0,0,0,0]}')
    with open(filepath, "r") as fd:
        json_obj = json.load(fd)
    return json_obj["version"]

def render_version(modulename):
    version = get_version(modulename)
    _, name, _ = split(modulename)
    return "{} version {}.{}.{}-{}".format(name, *version[:4])
