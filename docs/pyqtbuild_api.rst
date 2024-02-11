.. py:module:: pyqtbuild
    :synopsis: The PyQt build system.


:py:mod:`pyqtbuild` Module Reference
====================================

The :py:mod:`pyqtbuild` module provides a number of API elements that can be
used by a project's :file:`project.py` file.


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
    :py:mod:`pyqtbuild` module as represented as a string.  For development
    versions it will contain ``.dev``.


:py:class:`~pyqtbuild.PyQtBindings`
-----------------------------------

.. py:class:: PyQtBindings(project, name, **kwargs)

    A :py:class:`sipbuild.Bindings` sub-class that configures a
    :py:class:`~pyqtbuild.QmakeBuilder` builder and supports the use of test
    programs to determine if a set of bindings are buildable and how they
    should be configured.

    Test programs are either internal or external.  An internal test is
    constructed from the ``test-headers`` and ``test-statement`` keys and is
    compiled (but not executed) to determine if the bindings are buildable.

    An external test is a self contained C++ source file with the same name as
    the bindings with a ``cfgtest_`` prefix and a :file:`.cpp` extension.  The
    source file is compiled and executed and it's output analysed to determine
    if the bindings are buildable.

    :param PyQtProject project: is the project.
    :param str name: is the name of the bindings.
    :param \*\*kwargs: are keyword arguments that define the initial values of
        any corresponding :py:class:`sipbuild.Option` defined by the bindings.
        A :py:class:`sipbuild.Option` value set in this way cannot be
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

.. py:class:: PyQtProject(**kwargs)

    A :py:class:`sipbuild.Project` sub-class that provides different defaults
    for some keys in the ``[tool.sip.project]`` section of
    :file:`pyproject.toml`:

    - the default value of ``bindings-factory`` is
      :py:class:`~pyqtbuild.PyQtBindings`

    - the default value of ``builder-factory`` is 
      :py:class:`~pyqtbuild.QmakeBuilder`

    - the default value of ``sip-files-dir`` is :file:`sip`

    - the default value of ``sip-module`` is determined by the version of Qt

    - the default value of ``abi-version`` is determined by the value of
      ``sip-module``.

    :param \*\*kwargs: are keyword arguments that define the initial values of
        any corresponding :py:class:`sipbuild.Option` defined by the project.
        A :py:class:`sipbuild.Option` value set in this way cannot be
        overridden in the :file:`pyproject.toml` file or by using a tool
        command line option.


:py:class:`~pyqtbuild.QmakeBuilder`
-----------------------------------

.. py:class:: QmakeBuilder(project, **kwargs)

    A :py:class:`sipbuild.Builder` sub-class that uses Qt's :program:`qmake`
    program to build and install a project.

    :param Project project: is the :py:class:`sipbuild.Project` object.
    :param \*\*kwargs: are keyword arguments that define the initial values of
        any corresponding :py:class:`sipbuild.Option` defined by the project.
        A :py:class:`sipbuild.Option` value set in this way cannot be
        overridden in the :file:`pyproject.toml` file or by using a tool
        command line option.

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

    A :py:class:`sipbuild.Installable` sub-class used to describe the
    ``TARGET`` of a :file:`.pro` file.

    :param str target: is the file name of the target.
    :param str target_subdir: is the relative path name of a sub-directory in
        which the installable’s files will be installed.  If it is an absolute
        path name then it is used as the eventual full target directory.
