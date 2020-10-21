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
    The integer value is the number of make jobs that will be run in parallel
    (on Linux and macOS).  There is also a corresponding command line option.

**make**
    The boolean value specifies if :program:`make` (or :program:`nmake` on
    Windows) is executed automatically.  By default it is executed
    automatically.  There is also a corresponding command line option for
    :program:`sip-build`.

**qmake**
    The value is the full path name of the :program:`qmake` executable.  By
    default it is assumed to be on :envvar:`PATH`.  There is also a
    corresponding command line option.

**qmake-settings**
    The value is a list of strings, usually of the form ``NAME += VALUE``, that
    are added to any :program:`qmake` :file:`.pro` file that is created.  There
    is also a corresponding command line option.

**spec**
    The value is passed as the ``-spec`` argument to :program:`qmake` whenever
    it is executed by the builder.  There is also a corresponding command line
    option.


``[tool.sip.project]`` Section
------------------------------

The key/values in this section apply to the project as a whole.  Unless stated
otherwise, all values are strings.  Unless stated otherwise, the values of all
list options may contain environment markers as defined in `PEP 508
<https://www.python.org/dev/peps/pep-0508/>`__.

**android-abis**
    The value is a list of target Android ABIs (e.g. armeabi-v7a, arm64-v8a).
    There is also a corresponding command line option.

**link-full-dll**
    The boolean value specifies if, on Windows, the full Python DLL should be
    linked against rather than the limited API DLL.  There is also a
    corresponding command line option.

**py-pylib-dir**
    The value is the name of the directory containing the target Python
    interpreter library.  By default this is determined dynamically from the
    Python installation.

**py-pylib-lib**
    The value is the name of the target Python interpreter library.  By default
    this is determined dynamically from the Python installation.

**py-pylib-shlib**
    The value is the name of the target Python interpreter library if it is a
    shared library.  By default this is determined dynamically from the Python
    installation.

**qml-debug**
    The boolean value specifies if the QML debugging infrastructure should be
    enabled.  There is also a corresponding command line option.

**tag-prefix**
    The value is the prefix of the timeline tag to use (with the Qt version
    automatically appended).  By default the value of the ``name`` key in the
    ``[tool.sip.metadata]`` section of :file:`pyproject.toml` is used with any
    leading ``Py`` removed.

**target-qt-dir**
    The value specifies the name of the directory where the Qt libraries will
    be found.  By default the location of the Qt libraries being built against
    is used.  If Qt libraries to be included by running :program:`pyqt-bundle`
    are to be used then the value should be :file:`Qt/lib`.  There is also a
    corresponding command line option for :program:`sip-wheel`.

**tests-dir**
    The value is the name of the directory, relative to the directory
    containing :file:`pyproject.toml`, containing any external test programs.
    The default value is :file:`config-tests`.


Bindings Sections
-----------------

Unless stated otherwise, all values are strings.  Unless stated otherwise, the
values of all list options may contain environment markers as defined in `PEP
508 <https://www.python.org/dev/peps/pep-0508/>`__.

**qmake-CONFIG**
    The value is a list of modifications to make to the ``CONFIG`` value in all
    generated :file:`.pro` files.  An element may start with ``-`` to specify
    that the value should be removed.

**qmake-QT**
    The value is a list of modifications to make to the ``QT`` value in all
    generated :file:`.pro` files.  An element may start with ``-`` to specify
    that the value should be removed.

**test-headers**
    The value is a list of :file:`.h` header files to include in any internal
    test program.

**test-statement**
    The value is a C++ statement that will be included in any internal test
    program.
