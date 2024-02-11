An Example
==========

In this section we walk through the :file:`pyproject.toml` file for the
PyQtChart project.  PyQtChart is the set of bindings for the QtCharts v5
library and is built on top of PyQt5.  It comprises a single extension module.
The simplicitly of PyQtChart means that there is no need to provide any
additional code in a :file:`project.py` file.

If you want to look at a more complicated examples that require a
:file:`project.py` file then the QScintilla Python bindings and PyQt itself are
good examples.

We show PyQtChart's :file:`pyproject.toml` file (downloadable from
:download:`here <pyproject.toml>`) in its entirety below.

.. literalinclude:: pyproject.toml

We will now explain each section in turn.  We assume you are familiar with the
examples described in the `SIP documentation
<https://www.riverbankcomputing.com/static/Docs/sip/examples.html>`__.

The ``[build-system]`` section is used to specify the build system package
requirements.  For projects using SIP this will include the version
requirements of the ``sip`` project.  For PyQt projects it must also include
the version requirements of the ``PyQt-builder`` project.  Both SIP and
PyQt-builder use semantic versioning so it is important that an upper version
number is specified for each that will exclude future incompatible versions.

.. note::
    So why does ``sip`` specify an upper version of 7 rather than 6?  The
    answer is that it is known that PyQtChart does not use any SIP v5 features
    that have been removed in SIP v6.

The ``[tool.sip.metadata]`` section specifies the meta-data for the project.
The ``requires-dist`` key is used to specify the minimum version of PyQt that
is required.

The ``[tool.sip]`` section is used to configure the build system itself and we
use the ``project-factory`` key to specify that the
:py:class:`~pyqtbuild.PyQtProject` class is used to implement the concept of a
project in the build system.  This class implements the many PyQt-specific
features of the build system including the definition of additional
PyQt-specific keys in the :file:`pyproject.toml` file itself.

The ``[tool.sip.project]`` section is used to specify one such PyQt-specific
key ``tag-prefix``.  Current versions of PyQtChart use SIP's ``%Timeline``
directive to define tags that are of the form ``QtChart_x_y_0`` where *x* and
*y* correspond to the major and minor versions of PyQtChart and, consequently,
Qt.  Projects that follow this convention do not need to use the ``tags`` key
in the bindings sections to specify the particular ``%Timeline`` tag to use and
can leave it to the build system to determine it dynamically from the version
of Qt being used.

The ``[tool.sip.bindings.QtChart]`` section makes use of another PyQt-specific
key added by PyQt-builder.  This specifies that ``charts`` is added to the
``QT`` variable in any generated ``.pro`` file for this set of bindings.  This
is all that :program:`qmake` needs in order to locate the header files and
libraries of QtCharts.
