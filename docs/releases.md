# Release Notes


## v1.17.2

### Missing Linux multimedia libraries in Qt v6.8

In Qt v6.8 the QtMultimedia ffmpeg Linux backend depends on new libraries
that were not included in the Qt wheels.

Resolves [#29](https://github.com/Python-PyQt/PyQt-builder/issues/29)


## v1.17.1

### Updated the default ABIs used

The default ABIs used now match those explicitly specified by PyQt5 and
PyQt6.

Resolves [#28](https://github.com/Python-PyQt/PyQt-builder/issues/28)

### Set the minimum `glibc` version on x86-64 to v2.28

The minimum version of `glibc` required for Qt v6.8 has been reduced to
v2.28.  This is the same requirement as older versions of Qt6 and
corresponds to the oldest version used by any currently (supported Linux
distribution)[https://doc.qt.io/qt-6/supported-platforms.html].

Resolves [#27](https://github.com/Python-PyQt/PyQt-builder/issues/27)

### Include specific (L)GPL LICENSE file in Qt wheels

Instead of including a generic LICENSE file containing the text of both the
LGPL and the GPL in Qt wheels, a specific LGPL or GPL LICENSE file is now
included.

Resolves [#24](https://github.com/Python-PyQt/PyQt-builder/issues/24)

### Bug fix

A regression that prevented single architecture Qt installations being
bundled on macOS was fixed.

Resolves [#26](https://github.com/Python-PyQt/PyQt-builder/issues/26)


## v1.17.0

### Added support for Qt v6.8

- Added support for the QtGraphs module.
- Linux wheels now require GLIBC v2.35 (eg. Ubuntu 22.04) on Intel and v2.39
  (eg. Ubuntu 24.04) on Arm.

Resolves [#16](https://github.com/Python-PyQt/PyQt-builder/issues/16)

### Re-signing of bundled macOS Qt dynamic libraries

Prior to Qt v6.8 the macOS dynamic libraries were not signed.  They are
signed in v6.8 and the signature becomes invalid when `lipo` is used to
extract the individual architecture-specific libraries (which is done to
produce smaller wheels). The individual architecture-specific libraries are
now re-signed by `pyqt-bundle`.

Resolves [#21](https://github.com/Python-PyQt/PyQt-builder/issues/21)

### Python shared library name on macOS incorrect

The name of the Python shared library on macOS was incorrect which broke
PyQt's `qmlscene` and `Designer` plugins.


## v1.16.4

### Support for Windows on Arm for Qt6

Support was added for creating Qt6 wheels for Windows on Arm.

Resolves [#14](https://github.com/Python-PyQt/PyQt-builder/issues/14)

### Support for Linux on Arm for Qt6

Support was added for creating Qt6 wheels for Linux on Arm.

Resolves [#13](https://github.com/Python-PyQt/PyQt-builder/issues/13)


## v1.16.3

### Link to the stable SIP documentation

The documentation now links to the stable version of the SIP documentation.

Resolves [#11](https://github.com/Python-PyQt/PyQt-builder/issues/11)

### Missing multimedia libraries in Qt v6.7

In Qt v6.7 the QtMultimedia ffmpeg backends depend on new libraries that
were not included in the Qt wheels.  This affected macOS (Qt v6.7.1) and
Windows (Qt v6.7.0).

Resolves [#12](https://github.com/Python-PyQt/PyQt-builder/issues/12)

### Added support for sub-wheels to `pyqt-qt-wheel`

The (undocumented) `pyqt-qt-wheel` utility now supports the splitting of a
project's wheel into the main wheel and a sub-wheel.  Specifying
`--sub-wheel generate` will generate the sub-wheel, and
`--sub-wheel exclude` will generate the main wheel (ie. a normal wheel
without the contents of the sub-wheel).  By default a normal wheel is
generated.


## v1.16.2

### Broken links to SIP documentation

The links to the SIP documentation have been fixed.

### ICU libraries missing from Linux Qt wheels

The ICU libraries were missing from the Linux Qt v6.7 wheels.

Resolves [#10](https://github.com/Python-PyQt/PyQt-builder/issues/10)


## v1.16.1

### Bundle new QtQuick support libraries

The QtQuick3DHelpersImpl, QtQuickControls2MacOSStyleImpl and
QtQuickTimelineBlendTrees libraries added to Qt v6.7.0 are now bundled.

Resolves [#8](https://github.com/Python-PyQt/PyQt-builder/issues/8)

### Missing `LICENSE` file

The missing `LICENSE` file was added.

Resolves [#7](https://github.com/Python-PyQt/PyQt-builder/issues/7)


## v1.16.0

### Migration to GitHub

The project repository has been migrated to
[GitHub](https://github.com/Python-PyQt/PyQt-builder).

PyQt-builder is now licensed under the BSD-2-Clause license.

The project has now been migrated from `setup.py` to `setuptools_scm` and
`pyproject.toml`.

The documentation is now hosted at
[Read the Docs](https://PyQt-builder.readthedocs.io).

Resolves [#1](https://github.com/Python-PyQt/PyQt-builder/issues/1)

### Bundle new QtQuick support libraries

The QtQuickPhysics libraries added to Qt v6.6.0 are now bundled.

The QtQuickControls2 style libraries added to Qt v6.6.3 are now bundled.

Resolves [#6](https://github.com/Python-PyQt/PyQt-builder/issues/6)

### Improvements to example documentation

The example in the documentation no longer uses deprecated features that
will be removed in SIP v7.

The example is now PyQt6-based rather than PyQt5.

Resolves [#5](https://github.com/Python-PyQt/PyQt-builder/issues/5)

### ABI versions

The default ABI versions are now v12.13 and v13.6.
