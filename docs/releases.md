# Release Notes


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
