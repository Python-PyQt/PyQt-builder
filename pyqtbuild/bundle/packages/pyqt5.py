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


import os
import shutil

from ..abstract_package import AbstractPackage
from ..qt_metadata import VersionedMetadata
from ..verbose import verbose


# The directory containing the DLLs.
_DLLS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dlls')


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

    'QtBluetooth': (
        VersionedMetadata(version=(5, 7, 1),
            lib_deps={
                'linux': ('QtConcurrent', ),
                'macos': ('QtConcurrent', )},
            qml=True),
        VersionedMetadata(
            lib_deps={'macos': ('QtConcurrent', )},
            qml=True)),

    'QtCore':
        VersionedMetadata(
            other_lib_deps={
                'linux': ('libicui18n.so.56', 'libicuuc.so.56',
                          'libicudata.so.56'),
                'win': ('icudt*.dll', 'icuin*.dll', 'icuuc*.dll')},
            translations=('qt_help', 'qtbase', 'qtconnectivity',
                'qtdeclarative', 'qtlocation', 'qtmultimedia',
                'qtquickcontrols', 'qtserialport', 'qtwebsockets',
                'qtxmlpatterns', 'qt_', 'xcbglintegrations'),
            excluded_plugins=('canbus', 'designer', 'qmltooling')),

    'QtDBus':
        VersionedMetadata(),

    'QtDesigner':
        VersionedMetadata(),

    'QtGui':
        VersionedMetadata(lib_deps={'linux': ('QtWaylandClient', 'QtXcbQpa')},
                other_lib_deps={
                        'win': ('d3dcompiler_47.dll', 'libEGL.dll',
                                'libGLESv2.dll', 'opengl32sw.dll')}),

    'QtHelp': (
        VersionedMetadata(version=(5, 9, 0)),
        VersionedMetadata(lib_deps={'': ('QtCLucene', )})),

    'QtLocation': (
        VersionedMetadata(version=(5, 11, 0), qml=True,
                lib_deps={'': ('QtPositioningQuick', )}),
        VersionedMetadata(qml=True)),

    'QtMacExtras':
        VersionedMetadata(),

    'QtMultimedia': (
        VersionedMetadata(version=(5, 10, 0),
                lib_deps={'linux': ('QtMultimediaGstTools', )},
                qml=True, qml_names=('QtAudioEngine', 'QtMultimedia')),
        VersionedMetadata(lib_deps={'win': ('QtMultimediaQuick_p', )},
                qml=True, qml_names=('QtAudioEngine', 'QtMultimedia'))),

    'QtMultimediaWidgets':
        VersionedMetadata(),

    'QtNetwork':
        VersionedMetadata(),

    'QtNetworkAuth':
        VersionedMetadata(version=(5, 10, 0)),

    'QtNfc':
        VersionedMetadata(qml=True),

    'QtOpenGL':
        VersionedMetadata(),

    'QtPositioning':
        VersionedMetadata(qml=True),

    'QtPrintSupport':
        VersionedMetadata(),

    'QtQml': (
        VersionedMetadata(version=(5, 14, 0),
                lib_deps={'': ('QtQmlModels', 'QtQmlWorkerScript')},
                qml=True),
        VersionedMetadata(qml=True)),

    'QtQuick':
        VersionedMetadata(
                lib_deps={'': ('QtQuickControls2', 'QtQuickParticles',
                        'QtQuickShapes', 'QtQuickTemplates2', 'QtQuickTest')},
                qml=True,
                qml_names=('QtCanvas3D', 'QtGraphicalEffects', 'QtQuick',
                        'QtQuick.2')),

    'QtQuick3D':
        VersionedMetadata(version=(5, 15, 0),
                lib_deps={
                        '': ('QtQuick3DAssetImport', 'QtQuick3DRender',
                                'QtQuick3DRuntimeRender', 'QtQuick3DUtils')},
                qml=True),

    'QtQuickWidgets':
        VersionedMetadata(),

    'QtRemoteObjects':
        VersionedMetadata(version=(5, 12, 0), qml=True),

    'QtSensors':
        VersionedMetadata(qml=True),

    'QtSerialPort':
        VersionedMetadata(),

    'QtSql':
        VersionedMetadata(),

    'QtSvg':
        VersionedMetadata(),

    'QtTest':
        VersionedMetadata(qml=True),

    'QtTextToSpeech':
        VersionedMetadata(version=(5, 15, 0)),

    'QtWebChannel':
        VersionedMetadata(qml=True),

    'QtWebSockets':
        VersionedMetadata(qml=True),

    'QtWebView':
        VersionedMetadata(qml=True),

    'QtWidgets':
        VersionedMetadata(),

    'QtWinExtras':
        VersionedMetadata(),

    'QtX11Extras':
        VersionedMetadata(),

    'QtXml':
        VersionedMetadata(),

    'QtXmlPatterns':
        VersionedMetadata(
            qml=True,
            qml_names=('Qt', )),
}


class PyQt5(AbstractPackage):
    """ The PyQt5 package. """

    def bundle_msvc_runtime(self, target_qt_dir, arch):
        """ Bundle the MSVC runtime. """

        verbose("Bundling the MSVC runtime")

        self._bundle_dlls(target_qt_dir,
                os.path.join(_DLLS_DIR,
                        'msvc-64' if arch == 'win_amd64' else 'msvc-32'))

    def bundle_openssl(self, target_qt_dir, openssl_dir, arch):
        """ Bundle the OpenSSL DLLs. """

        if openssl_dir:
            verbose(
                    "Bundling the OpenSSL libraries from '{0}'".format(
                            openssl_dir))
        else:
            verbose("Bundling the default OpenSSL libraries")

            openssl_dir = os.path.join(_DLLS_DIR,
                    'openssl-64' if arch == 'win_amd64' else 'openssl-32')

        self._bundle_dlls(target_qt_dir, openssl_dir)

    def get_qt_metadata(self):
        """ Return the package-specific meta-data describing the parts of Qt to
        install.
        """

        return _QT_METADATA

    @staticmethod
    def _bundle_dlls(target_qt_dir, dlls_dir):
        """ Bundle the DLLs in a directory. """

        bin_dir = os.path.join(target_qt_dir, 'bin')
        os.makedirs(bin_dir, exist_ok=True)

        for dll in os.listdir(dlls_dir):
            shutil.copy2(os.path.join(dlls_dir, dll), bin_dir)
