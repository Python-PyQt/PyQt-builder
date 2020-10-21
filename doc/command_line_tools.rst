Command Line Tools
==================

PyQt-builder adds the following command line options to `SIP's build tools
<https://www.riverbankcomputing.com/static/Docs/sip/command_line_tools.html>`__.
Unless stated otherwise, each option is added to all of the build tools.

.. note::
    Individual projects may also add their own project-specific command line
    options.

.. option:: --android-abi ABI

    The target Android ABI.  This option may be given any number of times.

.. option:: --jobs N

    On Linux and macOS N make jobs will be run in parallel.

.. option:: --link-full-dll

    On Windows the full Python API and the limited API (as used by PyQt) are
    implemented in different DLLs.  Normally the limited DLL is linked (unless
    a debug version of the Python interpreter is being used.  This option
    forces the full API DLL to be linked instead.

.. option:: --no-make

    Do not automatically invoke :program:`make` or :program:`nmake`.
    (:program:`sip-build` only.)

.. option:: --qmake FILE

    Qt's :program:`qmake` program is used to determine how your Qt installation
    is laid out.  Normally :program:`qmake` is found on your :envvar:`PATH`.
    This option can be used to specify a particular instance of
    :program:`qmake` to use.

.. option:: --qmake-setting 'NAME += VALUE'

    The setting will be added to any :program:`qmake` :file:`.pro` file that is
    created.  This option may be given any number of times.

.. option:: --qml-debug

    Enable the QML debugging infrastructure.  This should not be enabled in a
    production environment.

.. option:: --spec SPEC

    The argument ``-spec SPEC`` will be passed to :program:`qmake`.  The
    default behaviour is platform specific.  On Windows
    the value that is chosen is correct for the version of Python that is
    being used.  (However if you have built Python yourself then you may need
    to explicitly specify ``SPEC``.)  On macOS ``macx-xcode`` will be avoided
    if possible.

.. option:: --target-qt-dir DIR

    The extension modules will be re-targeted to expect the Qt libraries to be
    installed in DIR when the wheel is installed.  (:program:`sip-wheel` only.)
