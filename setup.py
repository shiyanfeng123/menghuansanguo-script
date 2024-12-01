from setuptools import setup
from Cython.Build import cythonize

setup(
	ext_modules=cythonize("main.pyc"),
	zip_safe=False,
)
