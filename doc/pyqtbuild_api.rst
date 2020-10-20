.. py:module:: pyqtbuild
    :synopsis: The PyQt build system.


:py:mod:`pyqtbuild` Module Reference
====================================

TODO: review this.

:py:data:`PYQTBUILD_VERSION`
----------------------------

.. py:data:: PYQTBUILD_VERSION

    This is a Python integer object that represents the version number of the
    :py:mod:`pyqtbuild` module as a 3 part hexadecimal number (e.g. v1.5.0 is
    represented as ``0x010500``).


:py:data:`PYQTBUILD_VERSION_STR`
--------------------------------

.. py:data:: PYQTBUILD_VERSION_STR

    This is a Python string object that defines the version number of the
    :py:mod:`pyqtbuild` as represented as a string.  For development versions
    it will contain ``.dev``.


:py:class:`~pyqtbuild.PyQtBindings`
-----------------------------------

.. py:class:: PyQtBindings(project, name, \*\*kwargs)

    A :py:class:`~sipbuild.Bindings` sub-class that configures a
    :py:class:`~pyqtbuild.QmakeBuilder` builder and supports the use of test
    programs to determine if a set of bindings are buildable and how they
    should be configured.

    Test programs are either internal or external.  An internal test is
    constructed from the ``test-headers`` and ``test-statement`` keys described
    below and is compiled (but not executed) to determine if the bindings are
    buildable.

    An external test is a self contained C++ source file with the same name as
    the bindings with a ``cfgtest_`` prefix and a :file:`.cpp` extension.  The
    source file is compiled and executed and it's output analysed to determine
    if the bindings are buildable.

    :py:mod:`~pyqtbuild.PyQtBindings` adds the following keys to each
    ``[tool.sip.bindings]`` section of :file:`pyproject.toml`:

    **qmake-CONFIG**
        The value is a list of modifications to make to the ``CONFIG`` value in
        all generated :file:`.pro` files.  An element may start with ``-`` to
        specify that the value should be removed.

    **qmake-QT**
        The value is a list of modifications to make to the ``QT`` value in all
        generated :file:`.pro` files.  An element may start with ``-`` to
        specify that the value should be removed.

    **test-headers**
        The value is a list of :file:`.h` header files to include in any
        internal test program.

    **test-statement**
        The value is a C++ statement that will be included in any internal test
        program.

    :param Project project: is the project.
    :param str name: is the name of the bindings.
    :param \*\*kwargs: are keyword arguments that define the initial values of
        any corresponding :py:class:`~sipbuild.Option` defined by the bindings.
        An :py:class:`~sipbuild.Option` value set in this way cannot be
        overridden in the :file:`pyproject.toml` file or by using a tool
        command line option.

    .. py:method:: handle_test_output(test_output)

        Called by the bindings to handle the output from an external test
        program and to determine if the bindings are buildable.  The default
        implementation assumes that the output is a list of disabled features
        and that the bindings are implicitly buildable.

        :param list[str] test_output: is the output from an external test
            program.
        :return: ``True`` if the bindings are buildable.


:py:class:`~pyqtbuild.PyQtProject`
----------------------------------

.. py:class:: PyQtProject(\*\*kwargs)

    A :py:class:`~sipbuild.Project` sub-class that provides different defaults
    for some keys in the ``[tool.sip.project]`` section of
    :file:`pyproject.toml`:

    - the default value of ``bindings-factory`` is
      :py:class:`~pyqtbuild.PyQtBindings`

    - the default value of ``builder-factory`` is 
      :py:class:`~pyqtbuild.QmakeBuilder`

    - the default value of ``sip-files-dir`` is :file:`sip`

    - the default value of ``sip-module`` is :py:mod:`PyQt5.sip`.

    :param \*\*kwargs: are keyword arguments that define the initial values of
        any corresponding :py:class:`~sipbuild.Option` defined by the project.
        An :py:class:`~sipbuild.Option` value set in this way cannot be
        overridden in the :file:`pyproject.toml` file or by using a tool
        command line option.

    :py:mod:`~pyqtbuild.PyQtProject` adds the following keys to the
    ``[tool.sip.project]`` section of :file:`pyproject.toml`:

    **android-abis**
        The value is a list of target Android ABIs (e.g. armeabi-v7a,
        arm64-v8a).  This is also a user option.

    **link-full-dll**
        The boolean value specifies if, on Windows, the full Python DLL should
        be linked against rather than the limited API DLL.  This is also a user
        option.

    **py-pylib-dir**
        The value is the name of the directory containing the target Python
        interpreter library.  By default this is determined dynamically from
        the Python installation.

    **py-pylib-lib**
        The value is the name of the target Python interpreter library.  By
        default this is determined dynamically from the Python installation.

    **py-pylib-shlib**
        The value is the name of the target Python interpreter library if it is
        a shared library.  By default this is determined dynamically from the
        Python installation.

    **qml-debug**
        The boolean value specifies if the QML debugging infrastructure should
        be enabled.  This is also a user option.

    **target-qt-dir**
        The value specifies the name of the directory where the Qt libraries
        will be found.  By default the location of the Qt libraries being built
        against is used.  If Qt libraries to be included by running
        :program:`pyqt-bundle` are to be used then the value should be
        :file:`Qt/lib`.  This is also a user option for :program:`sip-wheel`.

    **tag-prefix**
        The value is the prefix of the timeline tag to use (with the Qt version
        automatically appended).  By default the value of the ``name`` key in
        the ``[tool.sip.metadata]`` section of :file:`pyproject.toml` is used
        with any leading ``Py`` removed.

    **tests-dir**
        The value is the name of the directory, relative to the directory
        containing :file:`pyproject.toml`, containing any external test
        programs.  The default value is :file:`config-tests`.


:py:class:`~pyqtbuild.QmakeBuilder`
-----------------------------------

.. py:class:: QmakeBuilder(project, \*\*kwargs)

    A :py:class:`~sipbuild.Builder` sub-class that uses Qt's :program:`qmake`
    program to build and install a project.

    :param Project project: is the :py:class:`~sipbuild.Project` object.
    :param \*\*kwargs: are keyword arguments that define the initial values of
        any corresponding :py:class:`~sipbuild.Option` defined by the project.
        An :py:class:`~sipbuild.Option` value set in this way cannot be
        overridden in the :file:`pyproject.toml` file or by using a tool
        command line option.

    :py:mod:`~pyqtbuild.QmakeBuilder` adds the following keys to the
    ``[tool.sip.builder]`` section of :file:`pyproject.toml`:

    **make**
        The boolean value specifies if :program:`make` (or :program:`nmake` on
        Windows) is executed automatically.  By default it is executed
        automatically.  This is also a user option.

    **qmake**
        The value is the full path name of the :program:`qmake` executable.  By
        default it is assumed to be on :envvar:`PATH`.  This is also a user
        option.

    **qmake-settings**
        The value is a list of strings of the form ``'NAME += VALUE'`` that are
        added to any :file:`.pro` file generated by the builder.  This is also
        a user option.

    **spec**
        The value is passed as the ``-spec`` argument to :program:`qmake`
        whenever it is executed by the builder.  This is also a user option.

    .. py:method:: qmake_quote(path)
        :staticmethod:

        If a file or directory path contains spaces then it is escaped so it
        can be used in a :file:`.pro` file.

        :param str path: the path.
        :return: the path, quoted if necessary.

    .. py:attribute:: qt_configuration

        A dict containing the Qt configuration information returned by running
        ``qmake -query``.


:py:class:`~pyqtbuild.QmakeTargetInstallable`
---------------------------------------------

.. py:class:: QmakeTargetInstallable(target, target_subdir)

    A :py:class:`~sipbuild.Installable` sub-class used to describe the
    ``TARGET`` of a :file:`.pro` file.

    :param str target: is the file name of the target.
    :param str target_subdir: is the relative path name of a sub-directory in
        which the installable’s files will be installed.  If it is an absolute
        path name then it is used as the eventual full target directory.
