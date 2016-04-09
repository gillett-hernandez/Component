from distutils.core import setup

long_description = \
"""this is a game engine that is structured using the "Component" pattern
an example game has been programmed in `lfclone.py`
and it uses the components found in `components.py`
"""

with open("LICENSE", 'r') as fd:
    LICENSE = fd.read()
    if isinstance(LICENSE, bytes):
        LICENSE = LICENSE.decode()

setup(name="Platformer",
      version="0.1.1",
      description="Game engine",
      long_description=long_description,
      author="Gillett Hernandez",
      author_email="gillett.hernandez@gmail.com",
      url="https://www.github.com/gillett-hernandez/Platformer",
      download_url="https://www.github.com/gillett-hernandez/Platformer",
      license=LICENSE,
      py_modules=["animation", "component", "components", "lfclone", "resources", "vector", "kwargsGroup"],
      data_files=[("resources", ["resources/images/spritesheet.png", "resources/images/clouds2.jpg"]),
                  ("data", ["json/lf_constants.json", "json/lf_keyconfig.json", "json/resources.json"])]
      )
