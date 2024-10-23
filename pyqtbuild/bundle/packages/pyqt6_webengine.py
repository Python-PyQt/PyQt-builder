# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from ..abstract_package import AbstractPackage
from ..qt_metadata import VersionedMetadata


# The Qt meta-data for this package.
_QT_METADATA = {
    'QtWebEngineCore':
        VersionedMetadata(version=(6, 2, 0),
            translations=('qtwebengine', ),
            other_lib_deps={
                'macos': ('QtWebEngineCore.framework/Helpers/QtWebEngineProcess.app/Contents/Info.plist', )},
            exes={
                'linux': ('libexec/QtWebEngineProcess', ),
                'macos': ('lib/QtWebEngineCore.framework/Helpers/QtWebEngineProcess.app/Contents/MacOS/QtWebEngineProcess', ),
                'win':   ('bin\\QtWebEngineProcess.exe', )},
            files={
                'win':  (('lib\\Qt6Core.lib',
                        "Enable QtWebEngineProcess to find it's resources.\n"), )},
            others={
                'linux': ('resources', 'translations/qtwebengine_locales'),
                'win':   ('resources', 'translations\\qtwebengine_locales')},
            subwheel_files={
                '':      (('qtlib', 'QtWebEngineCore'), )}),

    'QtWebEngineQuick':
        VersionedMetadata(version=(6, 2, 0),
            lib_deps={'': ('QtWebEngineQuickDelegatesQml', )},
            qml_names=['QtWebEngine']),

    'QtWebEngineWidgets':
        VersionedMetadata(version=(6, 2, 0)),
}


class PyQt6_WebEngine(AbstractPackage):
    """ The PyQt6-WebEngine package. """

    def get_qt_metadata(self):
        """ Return the package-specific meta-data describing the parts of Qt to
        install.
        """

        return _QT_METADATA
