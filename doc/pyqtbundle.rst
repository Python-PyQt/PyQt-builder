.. _ref-pyqt-bundle:

Bundling Qt Using :program:`pyqt-bundle`
----------------------------------------

The wheels of the GPL version of PyQt on PyPI bundle a copy of the relevant
parts of Qt.  This is done so that users can install a complete PyQt
environment with a single :program:`pip` install.  A new release of Qt does not
require a new release of PyQt but does require an update of the wheels to
include the updated Qt.  Only the wheels for the PyQt version with the same
minor version number as the Qt version are updated.  In other words when a new
release of Qt v\ *x.y* is made, only the wheels for PyQt v\ *x.y* are updated.

However, given the ABI guarantees made by Qt (i.e. that a later version or Qt
should be able to replace an earlier version without having to re-compile an
application) then it should be perfectly possible to bundle a later version of
Qt that has a later minor version number with a version of PyQt that has an
earlier minor version number.  For example it should be possible to bundle Qt
v5.12.5 with PyQt v5.9.0.  The other use case is when you want to bundle a
development version of Qt with a version of PyQt so that the development
version can be tested in a Python environment.

.. note::
    The ABI guarantees made by Qt do not apply to the
    :py:mod:`~PyQt5.QAxContainer` module.  This is only guaranteed to work if
    the version of Qt being bundled is exactly the same as the version of Qt
    that PyQt was built against.

The wheels of the commercial version of PyQt do not have a copy of Qt bundled
because it is not possible to distribute a copy of the commercial version of
Qt.  Therefore a commercial user must bundle their own copy of Qt to create a
complete wheel.

The :program:`pyqt-bundle` program is provided as a means of bundling the
relevant parts of a local Qt installation with a wheel, replacing any existing
copy.  You can also use it to produce a stripped down version of PyQt that
contains only those modules you actually want to use.

:program:`pyqt-bundle` assumes that the Qt installation has been created from
one of the LGPL or commercial binary installers provided by The Qt Company.  It
may also work with a Qt installation built from source but this is unsupported.

On Linux you must have the :program:`chrpath` program installed.

On macOS you must have the :program:`install_name_tool` program installed.
This is a part of Xcode.

On Windows the binary installer for MSVC 2015, MSVC 2017 or MSVC 2019 must be
used.  Also on Windows :program:`pyqt-bundle` also handles the MSVC runtime
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

By convention a wheel (e.g. a commercial wheel) without a copy of Qt bundled
does not have a build tag.  A wheel with a copy of Qt bundled has a build tag
corresponding to the version of Qt.
