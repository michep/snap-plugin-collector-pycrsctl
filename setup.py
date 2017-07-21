from setuptools import setup

setup(name='snap-plugin-collector-pycrsctl',
      version = '0.1',
      packages = ['snap_pycrsctl'],
      install_requires = ['snap-plugin-lib-py>=1.0.10,<2'],
      url = "https://github.com/michep/snap-plugin-collector-pycrsctl",
      author = "Mike Chepaykin",
      author_email="michep@mail.ru"
      )
