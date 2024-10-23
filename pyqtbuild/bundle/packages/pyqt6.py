# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from ..qt_metadata import VersionedMetadata

from .pyqt import PyQt


# The Qt meta-data for this package.
_QT_METADATA = {
    'QAxContainer':
        VersionedMetadata(dll=False),

    'QtBluetooth':
        VersionedMetadata(version=(6, 2, 0)),

    'QtCore': (
        VersionedMetadata(version=(6, 7, 0),
            other_lib_deps={
                'linux': ('libicui18n.so.73', 'libicuuc.so.73',
                          'libicudata.so.73')},
            translations=('qt_', 'qt_help', 'qtbase', 'qtconnectivity',
                'qtdeclarative', 'qtlocation', 'qtmultimedia',
                'qtquickcontrols2', 'qtserialport', 'qtwebsockets'),
            excluded_plugins=('designer', 'qmltooling')),
        VersionedMetadata(version=(6, 2, 0),
            other_lib_deps={
                'linux': ('libicui18n.so.56', 'libicuuc.so.56',
                          'libicudata.so.56')},
            translations=('qt_', 'qt_help', 'qtbase', 'qtconnectivity',
                'qtdeclarative', 'qtlocation', 'qtmultimedia',
                'qtquickcontrols2', 'qtserialport', 'qtwebsockets'),
            excluded_plugins=('designer', 'qmltooling')),
        VersionedMetadata(
            other_lib_deps={
                'linux': ('libicui18n.so.56', 'libicuuc.so.56',
                          'libicudata.so.56')},
            translations=('qt_', 'qt_help', 'qtbase', 'qtdeclarative', 
                'qtquickcontrols2'),
            excluded_plugins=('designer', 'qmltooling'))),

    'QtDBus':
        VersionedMetadata(),

    'QtDesigner':
        VersionedMetadata(),

    'QtGui': (
        VersionedMetadata(version=(6, 2, 0),
                lib_deps={
                        'linux': ('QtWaylandClient',
                                'QtWaylandEglClientHwIntegration',
                                'QtWlShellIntegration', 'QtXcbQpa')},
                other_lib_deps={
                        'win': ('d3dcompiler_47.dll', 'opengl32sw.dll')}),
        VersionedMetadata(lib_deps={'linux': ('QtWaylandClient', 'QtXcbQpa')},
                other_lib_deps={
                        'win': ('d3dcompiler_47.dll', 'opengl32sw.dll')})),

    'QtHelp':
        VersionedMetadata(),

    #'QtLocation':
    #    VersionedMetadata(),

    'QtMultimedia': (
        VersionedMetadata(version=(6, 8, 0),
                lib_deps={'': ('QtMultimediaQuick', )},
                other_lib_deps={
                    'macos': ('libavcodec.61.dylib', 'libavformat.61.dylib',
                            'libavutil.59.dylib', 'libswresample.5.dylib',
                            'libswscale.8.dylib'),
                    'win': ('avcodec-61.dll', 'avformat-61.dll',
                            'avutil-59.dll', 'swresample-5.dll',
                            'swscale-8.dll')},
                ),
        VersionedMetadata(version=(6, 7, 1),
                lib_deps={'': ('QtMultimediaQuick', )},
                other_lib_deps={
                    'macos': ('libavcodec.60.dylib', 'libavformat.60.dylib',
                            'libavutil.58.dylib', 'libswresample.4.dylib',
                            'libswscale.7.dylib'),
                    'win': ('avcodec-60.dll', 'avformat-60.dll',
                            'avutil-58.dll', 'swresample-4.dll',
                            'swscale-7.dll')},
                ),
        VersionedMetadata(version=(6, 7, 0),
                lib_deps={'': ('QtMultimediaQuick', )},
                other_lib_deps={
                    'win': ('avcodec-60.dll', 'avformat-60.dll',
                            'avutil-58.dll', 'swresample-4.dll',
                            'swscale-7.dll')},
                ),
        VersionedMetadata(version=(6, 2, 0),
                lib_deps={'': ('QtMultimediaQuick', )},
                )),

    'QtMultimediaWidgets':
        VersionedMetadata(version=(6, 2, 0)),

    'QtNetwork':
        VersionedMetadata(),

    'QtNfc':
        VersionedMetadata(version=(6, 2, 0)),

    'QtOpenGL':
        VersionedMetadata(),

    'QtOpenGLWidgets':
        VersionedMetadata(),

    'QtPdf':
        VersionedMetadata(version=(6, 4, 0),
                lib_deps={'': ('QtPdfQuick', )}),

    'QtPdfWidgets':
        VersionedMetadata(version=(6, 4, 0)),

    'QtPositioning':
        VersionedMetadata(version=(6, 2, 0),
                lib_deps={'': ('QtPositioningQuick', )},
                ),

    'QtPrintSupport':
        VersionedMetadata(),

    'QtQml': (
        VersionedMetadata(version=(6, 8, 0),
                lib_deps={'': ('QtQmlMeta', 'QtQmlModels', 'QtQmlWorkerScript',
                        'QtLabsAnimation', 'QtLabsFolderListModel',
                        'QtLabsPlatform', 'QtLabsQmlModels', 'QtLabsSettings',
                        'QtLabsSharedImage', 'QtLabsWavefrontMesh')},
                ),
        VersionedMetadata(version=(6, 5, 0),
                lib_deps={'': ('QtQmlModels', 'QtQmlWorkerScript',
                        'QtLabsAnimation', 'QtLabsFolderListModel',
                        'QtLabsQmlModels', 'QtLabsSettings',
                        'QtLabsSharedImage', 'QtLabsWavefrontMesh')},
                ),
        VersionedMetadata(
                lib_deps={'': ('QtQmlModels', 'QtQmlWorkerScript')},
                )),

    'QtQuick': (
        VersionedMetadata(version=(6, 8, 0),
                lib_deps={'': ('QtQuickControls2', 'QtQuickControls2Basic',
                        'QtQuickControls2BasicStyleImpl',
                        'QtQuickControls2Fusion',
                        'QtQuickControls2FusionStyleImpl',
                        'QtQuickControls2IOSStyleImpl',
                        'QtQuickControls2Imagine',
                        'QtQuickControls2ImagineStyleImpl',
                        'QtQuickControls2Impl',
                        'QtQuickControls2MacOSStyleImpl',
                        'QtQuickControls2Material',
                        'QtQuickControls2MaterialStyleImpl',
                        'QtQuickControls2Universal',
                        'QtQuickControls2UniversalStyleImpl',
                        'QtQuickDialogs2', 'QtQuickDialogs2QuickImpl',
                        'QtQuickDialogs2Utils', 'QtQuickEffects',
                        'QtQuickLayouts',
                        'QtQuickParticles', 'QtQuickShapes',
                        'QtQuickTemplates2', 'QtQuickTest',
                        'QtQuickTimeline', 'QtQuickTimelineBlendTrees',
                        'QtQuickVectorImage', 'QtQuickVectorImageGenerator')},
                ),
        VersionedMetadata(version=(6, 7, 0),
                lib_deps={'': ('QtQuickControls2', 'QtQuickControls2Basic',
                        'QtQuickControls2BasicStyleImpl',
                        'QtQuickControls2Fusion',
                        'QtQuickControls2FusionStyleImpl',
                        'QtQuickControls2IOSStyleImpl',
                        'QtQuickControls2Imagine',
                        'QtQuickControls2ImagineStyleImpl',
                        'QtQuickControls2Impl',
                        'QtQuickControls2MacOSStyleImpl',
                        'QtQuickControls2Material',
                        'QtQuickControls2MaterialStyleImpl',
                        'QtQuickControls2Universal',
                        'QtQuickControls2UniversalStyleImpl',
                        'QtQuickDialogs2', 'QtQuickDialogs2QuickImpl',
                        'QtQuickDialogs2Utils', 'QtQuickEffects',
                        'QtQuickLayouts',
                        'QtQuickParticles', 'QtQuickShapes',
                        'QtQuickTemplates2', 'QtQuickTest',
                        'QtQuickTimeline', 'QtQuickTimelineBlendTrees')},
                ),
        VersionedMetadata(version=(6, 6, 3),
                lib_deps={'': ('QtQuickControls2', 'QtQuickControls2Basic',
                        'QtQuickControls2BasicStyleImpl',
                        'QtQuickControls2Fusion',
                        'QtQuickControls2FusionStyleImpl',
                        'QtQuickControls2IOSStyleImpl',
                        'QtQuickControls2Imagine',
                        'QtQuickControls2ImagineStyleImpl',
                        'QtQuickControls2Impl', 'QtQuickControls2Material',
                        'QtQuickControls2MaterialStyleImpl',
                        'QtQuickControls2Universal',
                        'QtQuickControls2UniversalStyleImpl',
                        'QtQuickDialogs2', 'QtQuickDialogs2QuickImpl',
                        'QtQuickDialogs2Utils', 'QtQuickLayouts',
                        'QtQuickParticles', 'QtQuickShapes',
                        'QtQuickTemplates2', 'QtQuickTest',
                        'QtQuickTimeline')},
                ),
        VersionedMetadata(version=(6, 2, 0),
                lib_deps={'': ('QtQuickControls2', 'QtQuickControls2Impl',
                        'QtQuickDialogs2', 'QtQuickDialogs2QuickImpl',
                        'QtQuickDialogs2Utils', 'QtQuickLayouts',
                        'QtQuickParticles', 'QtQuickShapes',
                        'QtQuickTemplates2', 'QtQuickTest',
                        'QtQuickTimeline')},
                ),
        VersionedMetadata(
                lib_deps={'': ('QtQuickControls2', 'QtQuickControls2Impl',
                        'QtQuickLayouts', 'QtQuickParticles', 'QtQuickShapes',
                        'QtQuickTemplates2', 'QtQuickTest')},
                )),

    'QtQuick3D': (
        VersionedMetadata(version=(6, 8, 0),
                lib_deps={
                        '': ('QtConcurrent', 'QtQuick3DAssetImport',
                        'QtQuick3DAssetUtils', 'QtQuick3DEffects',
                        'QtQuick3DGlslParser', 'QtQuick3DHelpers',
                        'QtQuick3DHelpersImpl', 'QtQuick3DIblBaker',
                        'QtQuick3DParticles', 'QtQuick3DPhysics',
                        'QtQuick3DPhysicsHelpers', 'QtQuick3DRuntimeRender',
                        'QtQuick3DUtils', 'QtShaderTools', 'QtQuick3DXr')},
                ),
        VersionedMetadata(version=(6, 7, 0),
                lib_deps={
                        '': ('QtConcurrent', 'QtQuick3DAssetImport',
                        'QtQuick3DAssetUtils', 'QtQuick3DEffects',
                        'QtQuick3DGlslParser', 'QtQuick3DHelpers',
                        'QtQuick3DHelpersImpl', 'QtQuick3DIblBaker',
                        'QtQuick3DParticles', 'QtQuick3DPhysics',
                        'QtQuick3DPhysicsHelpers', 'QtQuick3DRuntimeRender',
                        'QtQuick3DUtils', 'QtShaderTools')},
                ),
        VersionedMetadata(version=(6, 6, 0),
                lib_deps={
                        '': ('QtConcurrent', 'QtQuick3DAssetImport',
                        'QtQuick3DAssetUtils', 'QtQuick3DEffects',
                        'QtQuick3DHelpers', 'QtQuick3DIblBaker',
                        'QtQuick3DParticles', 'QtQuick3DPhysics',
                        'QtQuick3DPhysicsHelpers', 'QtQuick3DRuntimeRender',
                        'QtQuick3DUtils', 'QtShaderTools')},
                ),
        VersionedMetadata(version=(6, 4, 0),
                lib_deps={
                        '': ('QtConcurrent', 'QtQuick3DAssetImport',
                        'QtQuick3DAssetUtils', 'QtQuick3DEffects',
                        'QtQuick3DHelpers', 'QtQuick3DIblBaker',
                        'QtQuick3DParticles', 'QtQuick3DRuntimeRender',
                        'QtQuick3DUtils', 'QtShaderTools')},
                ),
        VersionedMetadata(version=(6, 1, 0),
                lib_deps={
                        '': ('QtQuick3DAssetImport', 'QtQuick3DAssetUtils',
                        'QtQuick3DEffects', 'QtQuick3DHelpers',
                        'QtQuick3DIblBaker', 'QtQuick3DParticles',
                        'QtQuick3DRuntimeRender', 'QtQuick3DUtils',
                        'QtShaderTools')},
                ),
        VersionedMetadata(
                lib_deps={
                        '': ('QtQuick3DAssetImport', 'QtQuick3DRuntimeRender',
                        'QtQuick3DUtils', 'QtShaderTools')},
                )),

    'QtQuickWidgets':
        VersionedMetadata(),

    'QtRemoteObjects':
        VersionedMetadata(version=(6, 2, 0),
                lib_deps={'': ('QtRemoteObjectsQml', )},
                ),

    'QtSensors':
        VersionedMetadata(version=(6, 2, 0),
                lib_deps={'': ('QtSensorsQuick', )},
                ),

    'QtSerialPort':
        VersionedMetadata(version=(6, 2, 0)),

    'QtSpatialAudio':
        VersionedMetadata(version=(6, 5, 0),
                lib_deps={'': ('QtQuick3DSpatialAudio', )}),

    'QtSql':
        VersionedMetadata(),

    'QtSvg':
        VersionedMetadata(),

    'QtSvgWidgets':
        VersionedMetadata(),

    'QtTest':
        VersionedMetadata(),

    'QtTextToSpeech':
        VersionedMetadata(version=(6, 4, 0)),

    'QtWebChannel': (
        # The quick library may have been present from the start.
        VersionedMetadata(version=(6, 6, 0),
                lib_deps={'': ('QtWebChannelQuick', )},
                ),
        VersionedMetadata(version=(6, 2, 0))),

    'QtWebSockets':
        VersionedMetadata(version=(6, 2, 0)),

    'QtWidgets':
        VersionedMetadata(),

    'QtXml':
        VersionedMetadata(),
}


class PyQt6(PyQt):
    """ The PyQt6 package. """

    def get_qt_metadata(self):
        """ Return the package-specific meta-data describing the parts of Qt to
        install.
        """

        return _QT_METADATA
