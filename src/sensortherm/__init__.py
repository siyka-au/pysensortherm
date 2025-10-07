"""
PySensortherm
========

Python wrapper functions for communicating with surveying
instruments over a serial connection.

The implementations use the Leica GeoCOM ASCII RPC procotol primarily.
For older instruments, that do not support it, the GSI Online commands
are used instead.

The package provides
    1. Utility data types for handling instrument responses
    2. Instrument software specific low level commands

Documentation
-------------

Public classes and methods are provided with proper docstrings, that can
be viewed in the source code, through introspection tools or editor
utilities. The docstrings follow the NumPy style conventions. In addition
to the in-code documentation, a complete, rendered reference is avaialable
on the `GeoComPy documentation <https://geocompy.readthedocs.io>`_ site.

Some docstrings provide examples. These examples assume that `geocompy`
has been imported as ``gc``:

    >>> import geocompy as gc

Subpackages
-----------

``geocompy.geo``
    Communication through GeoCOM protocol.

``geocompy.gsi``
    Communication through GSI Online protocol.

Submodules
----------

``pysensortherm.``
    Utilities for data handling.

Reexports
---------

``geocompy.data.Angle``
    Angle value primitive.

``geocompy.data.Vector``
    3D vector primitive.
"""
# try:
#     from _version import __version__ as __version__
# except Exception:  # pragma: no coverage
#     __version__ = "0.0.0"  # Placeholder value for source installs