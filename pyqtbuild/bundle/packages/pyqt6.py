# Copyright (c) 2020, Riverbank Computing Limited
# All rights reserved.
#
# This copy of PyQt-builder is licensed for use under the terms of the SIP
# License Agreement.  See the file LICENSE for more details.
#
# This copy of PyQt-builder may also used under the terms of the GNU General
# Public License v2 or v3 as published by the Free Software Foundation which
# can be found in the files LICENSE-GPL2 and LICENSE-GPL3 included in this
# package.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.


from ..qt_metadata import VersionedMetadata

from .pyqt import PyQt


# The Qt meta-data for this package.
_QT_METADATA = {
    #'QAxContainer':
    #    VersionedMetadata(dll=False),

    #'QtBluetooth':
    #    VersionedMetadata(
    #        lib_deps={
    #            'linux': ('QtConcurrent', ),
    #            'macos': ('QtConcurrent', )},
    #        qml=True),

    'QtCore':
        VersionedMetadata(
            other_lib_deps={
                'linux': ('libicui18n.so.56', 'libicuuc.so.56',
                          'libicudata.so.56')},
            translations=('qt_help', 'qtbase', 'qtdeclarative', 
                'qtquickcontrols2', 'qt_'),
            #translations=('qt_help', 'qtbase', 'qtconnectivity',
            #    'qtdeclarative', 'qtlocation', 'qtmultimedia',
            #    'qtquickcontrols2', 'qtserialport', 'qtwebsockets',
            #    'qtxmlpatterns', 'qt_'),
            excluded_plugins=('designer', 'qmltooling')),

    'QtDBus':
        VersionedMetadata(),

    'QtDesigner':
        VersionedMetadata(),

    'QtGui':
        VersionedMetadata(lib_deps={'linux': ('QtWaylandClient', 'QtXcbQpa')},
                other_lib_deps={
                        'win': ('d3dcompiler_47.dll', 'opengl32sw.dll')}),

    'QtHelp':
        VersionedMetadata(),

    #'QtLocation':
    #    VersionedMetadata(
    #            lib_deps={'': ('QtPositioningQuick', )},
    #            qml=True),

    #'QtMultimedia':
    #    VersionedMetadata(
    #            lib_deps={'linux': ('QtMultimediaGstTools', )},
    #            qml=True, qml_names=('QtAudioEngine', 'QtMultimedia')),

    #'QtMultimediaWidgets':
    #    VersionedMetadata(),

    'QtNetwork':
        VersionedMetadata(),

    #'QtNfc':
    #    VersionedMetadata(qml=True),

    'QtOpenGL':
        VersionedMetadata(),

    'QtOpenGLWidgets':
        VersionedMetadata(),

    #'QtPositioning':
    #    VersionedMetadata(qml=True),

    'QtPrintSupport':
        VersionedMetadata(),

    'QtQml':
        VersionedMetadata(
                lib_deps={'': ('QtQmlModels', 'QtQmlWorkerScript')},
                qml=True),

    'QtQuick':
        VersionedMetadata(
                lib_deps={'': ('QtQuickControls2', 'QtQuickControls2Impl',
                        'QtQuickParticles', 'QtQuickShapes',
                        'QtQuickTemplates2', 'QtQuickTest')},
                qml=True),

    'QtQuick3D':
        VersionedMetadata(
                lib_deps={
                        '': ('QtQuick3DAssetImport', 'QtQuick3DRuntimeRender',
                        'QtQuick3DUtils', 'QtShaderTools')},
                qml=True),

    'QtQuickWidgets':
        VersionedMetadata(),

    #'QtRemoteObjects':
    #    VersionedMetadata(qml=True),

    #'QtSensors':
    #    VersionedMetadata(qml=True),

    #'QtSerialPort':
    #    VersionedMetadata(),

    'QtSql':
        VersionedMetadata(),

    'QtSvg':
        VersionedMetadata(),

    'QtSvgWidgets':
        VersionedMetadata(),

    'QtTest':
        VersionedMetadata(qml=True),

    #'QtTextToSpeech':
    #    VersionedMetadata(),

    #'QtWebChannel':
    #    VersionedMetadata(qml=True),

    #'QtWebSockets':
    #    VersionedMetadata(qml=True),

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
