# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from ..qt_metadata import VersionedMetadata

from .pyqt import PyQt


# The Qt meta-data for this package.
_QT_METADATA = {
    'pylupdate':
        VersionedMetadata(dll=False),

    'pyrcc':
        VersionedMetadata(dll=False),

    'QAxContainer':
        VersionedMetadata(dll=False),

    'QtAndroidExtras':
        VersionedMetadata(),

    'QtBluetooth':
        VersionedMetadata(
            lib_deps={
                'linux': ('QtConcurrent', ),
                'macos': ('QtConcurrent', )},
            ),

    'QtCore':
        VersionedMetadata(
            other_lib_deps={
                'linux': ('libicui18n.so.56', 'libicuuc.so.56',
                          'libicudata.so.56'),
                'win': ('icudt*.dll', 'icuin*.dll', 'icuuc*.dll')},
            translations=('qt_help', 'qtbase', 'qtconnectivity',
                'qtdeclarative', 'qtlocation', 'qtmultimedia',
                'qtquickcontrols', 'qtscript', 'qtserialport', 'qtwebsockets',
                'qtxmlpatterns', 'qt_', 'xcbglintegrations'),
            excluded_plugins=('canbus', 'designer', 'egldeviceintegrations',
                    'gamepads', 'qmltooling', 'virtualkeyboard',
                    'wayland-graphics-integration-server')),

    'QtDBus':
        VersionedMetadata(),

    'QtDesigner':
        VersionedMetadata(),

    'QtGui':
        VersionedMetadata(
            lib_deps={'linux': ('QtWaylandClient', 'QtXcbQpa')},
            other_lib_deps={
                'win': ('d3dcompiler_47.dll', 'libEGL.dll', 'libGLESv2.dll',
                        'opengl32sw.dll')}),

    'QtHelp':
        VersionedMetadata(),

    'QtLocation':
        VersionedMetadata(lib_deps={'': ('QtPositioningQuick', )}),

    'QtMacExtras':
        VersionedMetadata(),

    'QtMultimedia':
        VersionedMetadata(
            lib_deps={
                '': ('QtMultimediaQuick', ),
                'linux': ('QtMultimediaGstTools', )
            },
            qml_names=('QtAudioEngine', 'QtMultimedia')),

    'QtMultimediaWidgets':
        VersionedMetadata(),

    'QtNetwork':
        VersionedMetadata(),

    'QtNetworkAuth':
        VersionedMetadata(legacy=True),

    'QtNfc':
        VersionedMetadata(),

    'QtOpenGL':
        VersionedMetadata(),

    'QtPositioning':
        VersionedMetadata(),

    'QtPrintSupport':
        VersionedMetadata(),

    'QtQml':
        VersionedMetadata(lib_deps={'': ('QtQmlModels', 'QtQmlWorkerScript')}),

    'QtQuick':
        VersionedMetadata(
            lib_deps={'': ('QtQuickControls2', 'QtQuickParticles',
                    'QtQuickShapes', 'QtQuickTemplates2', 'QtQuickTest')},
            qml_names=('QtCanvas3D', 'QtGraphicalEffects', 'QtQuick',
                    'QtQuick.2')),

    'QtQuick3D':
        VersionedMetadata(
            lib_deps={
                    '': ('QtQuick3DAssetImport', 'QtQuick3DRender',
                            'QtQuick3DRuntimeRender', 'QtQuick3DUtils')},
            ),

    'QtQuickWidgets':
        VersionedMetadata(),

    'QtRemoteObjects':
        VersionedMetadata(),

    'QtSensors':
        VersionedMetadata(),

    'QtSerialPort':
        VersionedMetadata(),

    'QtSql':
        VersionedMetadata(),

    'QtSvg':
        VersionedMetadata(),

    'QtTest':
        VersionedMetadata(),

    'QtTextToSpeech':
        VersionedMetadata(),

    'QtWebChannel':
        VersionedMetadata(),

    'QtWebSockets':
        VersionedMetadata(),

    'QtWebView':
        VersionedMetadata(),

    'QtWidgets':
        VersionedMetadata(),

    'QtWinExtras':
        VersionedMetadata(),

    'QtX11Extras':
        VersionedMetadata(),

    'QtXml':
        VersionedMetadata(),

    'QtXmlPatterns':
        VersionedMetadata(qml_names=('Qt', )),
}


class PyQt5(PyQt):
    """ The PyQt5 package. """

    def get_qt_metadata(self):
        """ Return the package-specific meta-data describing the parts of Qt to
        install.
        """

        return _QT_METADATA
