:file:`pyproject.toml` Reference
================================

PyQt-builder adds the following keys to those `implemented by SIP
<https://www.riverbankcomputing.com/static/Docs/sip/pyproject_toml.html>`__.

.. note::
    Individual projects may also add their own project-specific keys.


``[tool.sip.builder]`` Section
------------------------------

Unless stated otherwise, all values are strings.  Unless stated otherwise, the
values of all list options may contain environment markers as defined in `PEP
508 <https://www.python.org/dev/peps/pep-0508/>`__.

**jobs**
    TODO
    There is also a corresponding command line option.

**make**
    TODO
    There is also a corresponding command line option.

**qmake**
    TODO
    There is also a corresponding command line option.

**qmake-settings**
    TODO
    There is also a corresponding command line option.

**spec**
    TODO
    There is also a corresponding command line option.


``[tool.sip.project]`` Section
------------------------------

The key/values in this section apply to the project as a whole.  Unless stated
otherwise, all values are strings.  Unless stated otherwise, the values of all
list options may contain environment markers as defined in `PEP 508
<https://www.python.org/dev/peps/pep-0508/>`__.

**android-abis**
    TODO
    There is also a corresponding command line option.

**link-full-dll**
    TODO
    There is also a corresponding command line option.

**py-pylib-dir**
    TODO

**py-pylib-lib**
    TODO

**py-pylib-shlib**
    TODO

**qml-debug**
    TODO
    There is also a corresponding command line option.

**tag-prefix**
    TODO

**target-qt-dir**
    TODO
    There is also a corresponding command line option.

**tests-dir**
    TODO


Bindings Sections
-----------------

Unless stated otherwise, all values are strings.  Unless stated otherwise, the
values of all list options may contain environment markers as defined in `PEP
508 <https://www.python.org/dev/peps/pep-0508/>`__.

**qmake-CONFIG**
    TODO
    The value is a list of values that are passed to the builder.  It is up to
    the builder to determine how these values are used.

**qmake-QT**
    TODO
    The value is a list of values that are passed to the builder.  It is up to
    the builder to determine how these values are used.

**test-headers**
    TODO
    The value is a list of values that are passed to the builder.  It is up to
    the builder to determine how these values are used.

**test-statement**
    TODO
    The value, interpreted as a number, specifies that the generated code is
    split into that number of source files.  By default one file is generated
    for each C structure or C++ class.  Specifying a low value can
    significantly speed up the build of large projects.  This is also a user
    option.
