.. _ref-pyqt-bundle:

Bundling Qt Using :program:`pyqt-bundle`
----------------------------------------

PyQt wheels can contain a bundled copy of the relevent parts of Qt.  The main
reason for doing this is so that users can install a complete PyQt environment
with a single :program:`pip` install.

A bundled copy may also be replaced by a newer release of Qt.  Given the ABI
guarantees made by Qt (i.e. that a later version of Qt should be able to
replace an earlier version without having to re-compile an application) then it
should be perfectly possible to bundle a later version of Qt that has a later
minor version number with a version of PyQt that has an earlier minor version
number.  For example it should be possible to bundle Qt v5.15.2 with PyQt
v5.12.0.

The other use case is when you want to bundle a development version of Qt with
a version of PyQt so that the development version can be tested in a Python
environment.

.. note::
    The ABI guarantees made by Qt do not apply to the
    :py:mod:`~PyQt5.QAxContainer` module.  This is only guaranteed to work if
    the version of Qt being bundled is exactly the same as the version of Qt
    that PyQt was built against.

The :program:`pyqt-bundle` program is provided as a means of bundling the
relevant parts of a local Qt installation with a wheel, replacing any existing
copy.  You can also use it to produce a stripped down version of PyQt that
contains only those modules you actually want to use.

:program:`pyqt-bundle` assumes that the Qt installation has been created from
one of the LGPL or commercial binary installers provided by The Qt Company.  It
may also work with a Qt installation built from source but this is unsupported.

On Windows the binary installer for the latest supported version of MSVC must
be used.  Also on Windows :program:`pyqt-bundle` also handles the MSVC runtime
DLLs and the OpenSSL DLLs.

.. note::
    :program:`pyqt-bundle` will not update the platform tag of a wheel.  Some
    platform tags can embed additional requirements (e.g. the minimum required
    version of macOS is embedded in the platform tag of a macOS wheel).  If you
    bundle a later version of Qt with a more restrictive requirement then you
    should rename the wheel to reflect this.

The syntax of the :program:`pyqt-bundle` command line is::

    pyqt-bundle [options] wheel

The full set of command line options is:

.. program:: pyqt-bundle

.. option:: -h, --help

    Display a help message and exit.

.. option:: -V, --version

    Display the version number and exit.

.. option:: --build-tag-suffix SUFFIX

    ``SUFFIX`` is appended to the build tag in the name of the updated wheel.
    The build tag is the version number of the copy of Qt being bundled.

.. option:: --arch ARCH

    On macOS, when bundling Qt v6.2 or later, support for the ``ARCH``
    architecture (either ``x86_64`` or ``arm64``) only is included.

.. option:: --exclude NAME

    The ``NAME`` bindings are excluded from the wheel.  This option may be
    specified multiple times.

.. option:: --ignore-missing

    If a file cannot be found in the Qt installation being bundled then it is
    ignored instead of being teated as an error.  This allows unsupported or
    non-standard Qt installation to be bundled but may result in a wheel that
    does not work.

.. option:: --no-msvc-runtime

    On Windows the :file:`msvcp140.dll`, :file:`concrt140.dll` and
    :file:`vcruntime140.dll` MSVC runtime DLLs will not be included in the
    wheel.

.. option:: --no-openssl

    On Windows the OpenSSL DLLs (included with :program:`pyqt-bundle`) will not
    be included in the wheel.

.. option:: --openssl-dir DIR

    On Windows the OpenSSL DLLs included in the wheels are taken from ``DIR``
    instead of the DLLs included with :program:`pyqt-bundle`.  (Qt v5.12.4 and
    later are configured for OpenSSL v1.1.1.  Earlier versions of Qt are
    configured for OpenSSL v1.0.2.)

.. option:: --qt-dir DIR

    ``DIR`` contains the LGPL or commercial Qt installation to be bundled.  The
    directory is what Qt refers to as the *prefix* directory, i.e. the
    architecture specific directory containing the ``bin``, ``lib`` etc.
    directories.  This option must be specified.

By convention a wheel without a copy of Qt bundled does not have a build tag.
A wheel with a copy of Qt bundled has a build tag corresponding to the version
of Qt.


Bundling Qt6 Additional Libraries
.................................

.. note::

    Starting with Qt v6.1.0 the online installer now includes binaries for the
    additional libraries, therefore the steps described below are no longer
    necessary.

Unlike Qt5, the Qt6 online installer only provides binaries for the core Qt
libraries.  It provides the sources for the additional libraries (e.g. Qt 3D)
and these must be built and installed before they can be bundled.  While the Qt
documentation talks about using the :program:`conan` package manager to do
this it isn't actually necessary.

To build and additional library make sure you have :program:`CMake` and
:program:`ninja` installed and on :envvar:`PATH`.  Change to the library's
:file:`Src` subdirectory and run::

    cmake -G Ninja -DCMAKE_INSTALL_PREFIX=/path/to/qt-prefix-directory
    ninja install

The Qt prefix directory is the name of the architecture-specific directory of a
Qt installation.  It is :file:`gcc_64` on Linux, :file:`clang_64` on macos and
:file:`msvc2019_64` on Windows.
