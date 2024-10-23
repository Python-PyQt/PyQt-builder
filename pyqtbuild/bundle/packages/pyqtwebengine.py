# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from ..abstract_package import AbstractPackage
from ..qt_metadata import VersionedMetadata


# The Qt meta-data for this package.
_QT_METADATA = {
    'QtWebEngine':
        VersionedMetadata(translations=('qtwebengine', )),

    'QtWebEngineCore':
        VersionedMetadata(
            other_lib_deps={
                'macos': ('QtWebEngineCore.framework/Helpers/QtWebEngineProcess.app/Contents/Info.plist', )},
            exes={
                'linux': ('libexec/QtWebEngineProcess', ),
                'macos': ('lib/QtWebEngineCore.framework/Helpers/QtWebEngineProcess.app/Contents/MacOS/QtWebEngineProcess', ),
                'win':   ('bin\\QtWebEngineProcess.exe', )},
            files={
                'macos': (('lib/QtWebEngineCore.framework/Libraries/.ignore',
                        "Wheels cannot contain empty directories.\n"), )},
            others={
                'linux': ('resources', 'translations/qtwebengine_locales'),
                'win':   ('resources', 'translations\\qtwebengine_locales')}),

    'QtWebEngineWidgets':
        VersionedMetadata(),
}


class PyQtWebEngine(AbstractPackage):
    """ The PyQtWebEngine package. """

    def get_qt_metadata(self):
        """ Return the package-specific meta-data describing the parts of Qt to
        install.
        """

        return _QT_METADATA
