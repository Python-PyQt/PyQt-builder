An Example
==========

TODO

If you are developing a set of bindings based on PyQt then you should place the
following line in the ``[build-system]`` section of your :file:`pyproject.toml`
file::

    requires = ["PyQt-builder >=1, <2"]

This will ensure that ``PyQt-builder`` is automatically installed if a user
uses :program:`pip` to install your project.
