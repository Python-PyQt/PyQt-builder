# Copyright (c) 2022, Riverbank Computing Limited
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


import fnmatch
import os
import shutil
import subprocess

from sipbuild import UserException

from .verbose import is_verbose, verbose


class VersionedMetadata:
    """ Encapsulate the meta-data for a set of bindings for a particular
    version of Qt.
    """

    def __init__(self, *, version=None, name=None, lib_deps=None,
            other_lib_deps=None, exes=None, files=None, others=None, dll=True,
            qml=False, qml_names=None, translations=None,
            excluded_plugins=None, lgpl=True, legacy=False):
        """ Initialise the versioned bindings. """

        self._version = version
        self._name = name
        self._lib_deps = {} if lib_deps is None else lib_deps
        self._other_lib_deps = {} if other_lib_deps is None else other_lib_deps
        self._exes = {} if exes is None else exes
        self._files = {} if files is None else files
        self._others = {} if others is None else others
        self._dll = dll
        self._qml = qml
        self._qml_names = qml_names
        self._translations = () if translations is None else translations
        self._excluded_plugins = excluded_plugins

        self.lgpl = lgpl
        self.legacy = legacy

    def bundle(self, name, target_qt_dir, qt_dir, platform_tag, qt_version,
            ignore_missing):
        """ Bundle part of Qt as defined by the meta-data. """

        verbose("Bundling {0}".format(name))

        if self._name is None:
            self._name = name

        # See if a particular macOS architecture has been specified but only
        # for versions of Qt that support universal libraries.
        macos_thin_arch = self._get_macos_thin_arch(platform_tag)
        if qt_version < (6, 2, 0):
            macos_thin_arch = None

        if macos_thin_arch is not None:
            from .abstract_package import AbstractPackage

            if AbstractPackage.missing_executable('lipo'):
                raise UserException(
                        "'lipo' from Xcode must be installed on your system")

            if macos_thin_arch == 'arm64' and AbstractPackage.missing_executable('codesign'):
                raise UserException(
                        "'codesign' from Xcode must be installed on your system")

        # Bundle the Qt library that has been wrapped (if there is one).
        if self._dll:
            self._bundle_qt_library(self._name, target_qt_dir, qt_dir,
                    qt_version, platform_tag, macos_thin_arch, ignore_missing)

        # Bundle any other dependent Qt libraries.
        for metadata_arch, libs in self._lib_deps.items():
            if self._is_platform(metadata_arch, platform_tag):
                for lib in libs:
                    self._bundle_qt_library(lib, target_qt_dir, qt_dir,
                            qt_version, platform_tag, macos_thin_arch,
                            ignore_missing)

        # Bundle any other libraries.
        lib_contents = None

        for metadata_arch, libs in self._other_lib_deps.items():
            if self._is_platform(metadata_arch, platform_tag):
                for lib in libs:
                    if '*' in lib:
                        # A wildcard implies the dependency is optional.  This
                        # is mainly to (historically) deal with ICU on Windows.
                        if lib_contents is None:
                            lib_contents = os.listdir(
                                    self._get_qt_library_dir(qt_dir,
                                            platform_tag))

                        for qt_lib in lib_contents:
                            if fnmatch.fnmatch(qt_lib, lib):
                                self._bundle_library(qt_lib, target_qt_dir,
                                        qt_dir, platform_tag, macos_thin_arch,
                                        ignore_missing)
                    else:
                        self._bundle_library(lib, target_qt_dir, qt_dir,
                                platform_tag, macos_thin_arch, ignore_missing)

        # Bundle any executables.
        for metadata_arch, exes in self._exes.items():
            if self._is_platform(metadata_arch, platform_tag):
                for exe in exes:
                    bundled_exe = self._bundle_file(exe, target_qt_dir, qt_dir,
                            platform_tag, macos_thin_arch, ignore_missing)

                    if bundled_exe is not None:
                        if self._is_platform('linux', platform_tag):
                            self._fix_linux_executable(bundled_exe, qt_version)
                        elif self._is_platform('macos', platform_tag):
                            self._fix_macos_executable(bundled_exe, qt_version,
                                    macos_thin_arch)
                        elif self._is_platform('win', platform_tag):
                            self._fix_win_executable(bundled_exe)

        # Bundle any QML files.
        if self._qml:
            qml_names = self._qml_names
            if qml_names is None:
                qml_names = [self._name]

            for qml_subdir in qml_names:
                self._bundle_nondebug(os.path.join('qml', qml_subdir),
                        target_qt_dir, qt_dir, platform_tag, macos_thin_arch,
                        ignore_missing)

        # Bundle any plugins.  We haven't done the analysis of which plugins
        # belong to which package so we assume that only the QtCore package
        # will specify any to exclude and we bundle all of them with that.
        if self._excluded_plugins is not None:
            self._bundle_nondebug('plugins', target_qt_dir, qt_dir,
                    platform_tag, macos_thin_arch, ignore_missing,
                    exclude=self._excluded_plugins)

        # Bundle any translations:
        if self._translations:
            target_tr_dir = os.path.join(target_qt_dir, 'translations')
            tr_dir = os.path.join(qt_dir, 'translations')

            for qm in os.listdir(tr_dir):
                if qm.endswith('.qm'):
                    for prefix in self._translations:
                        if qm.startswith(prefix):
                            self._bundle_file(qm, target_tr_dir, tr_dir,
                                    platform_tag, macos_thin_arch,
                                    ignore_missing,
                                    might_be_code=False)

        # Bundle any dynamically created files.
        for metadata_arch, files in self._files.items():
            if self._is_platform(metadata_arch, platform_tag):
                for fn, content in files:
                    fn = os.path.join(target_qt_dir, fn)
                    os.makedirs(os.path.dirname(fn), exist_ok=True)

                    with open(fn, 'w') as f:
                        f.write(content)

        # Bundle anything else.
        for metadata_arch, others in self._others.items():
            if self._is_platform(metadata_arch, platform_tag):
                for oth in others:
                    self._bundle_file(oth, target_qt_dir, qt_dir,
                            platform_tag, macos_thin_arch, ignore_missing,
                            might_be_code=False)

    def is_applicable(self, qt_version):
        """ Returns True if this meta-data is applicable for a particular Qt
        version.
        """

        return self._version is None or qt_version >= self._version

    @classmethod
    def _bundle_nondebug(cls, src_dir, target_qt_dir, qt_dir, platform_tag,
            macos_thin_arch, ignore_missing, exclude=None):
        """ Bundle the non-debug contents of a directory. """

        if exclude is None:
            exclude = ()

        for dirpath, dirnames, filenames in os.walk(os.path.join(qt_dir, src_dir)):
            for ignore in exclude:
                try:
                    dirnames.remove(ignore)
                except ValueError:
                    pass

            for name in list(dirnames):
                if cls._is_debug(name, platform_tag):
                    dirnames.remove(name)

            for name in filenames:
                if cls._is_debug(name, platform_tag):
                    continue

                cls._bundle_file(
                        os.path.relpath(os.path.join(dirpath, name), qt_dir),
                        target_qt_dir, qt_dir, platform_tag, macos_thin_arch,
                        ignore_missing)

    @staticmethod
    def _bundle_file(name, target_dir, src_dir, platform_tag, macos_thin_arch,
            ignore_missing, ignore=None, might_be_code=True):
        """ Bundle a file (or directory) and return the name of the installed
        file (or directory) or None if it was missing.
        """

        src = os.path.join(src_dir, name)
        dst = os.path.join(target_dir, name)

        os.makedirs(os.path.dirname(dst), exist_ok=True)

        if os.path.isdir(src):
            shutil.copytree(src, dst, ignore=ignore)
        elif os.path.isfile(src):
            if macos_thin_arch is not None and might_be_code:
                stderr = None if is_verbose() else subprocess.DEVNULL

                try:
                    subprocess.run(
                            ['lipo', '-thin', macos_thin_arch, '-output', dst,
                                    src],
                            stderr=stderr, check=True)
                except:
                    # If there is any sort of error then just copy it.
                    shutil.copy2(src, dst)
            else:
                shutil.copy2(src, dst)
        elif ignore_missing:
            verbose("Ignoring missing '{0}'".format(name))
            dst = None
        else:
            raise UserException(
                    "'{0}' is missing from the Qt installation".format(name))

        return dst

    @classmethod
    def _bundle_library(cls, name, target_qt_dir, qt_dir, platform_tag,
            macos_thin_arch, ignore_missing, ignore=None):
        """ Bundle a library. """

        cls._bundle_file(name,
                os.path.join(target_qt_dir,
                        cls._get_qt_library_subdir(platform_tag)),
                cls._get_qt_library_dir(qt_dir, platform_tag), platform_tag,
                macos_thin_arch, ignore_missing, ignore=ignore)

    @classmethod
    def _bundle_qt_library(cls, name, target_qt_dir, qt_dir, qt_version,
            platform_tag, macos_thin_arch, ignore_missing):
        """ Bundle a Qt library. """

        cls._bundle_library(
                cls._impl_from_library(name, platform_tag, qt_version),
                target_qt_dir, qt_dir, platform_tag, macos_thin_arch,
                ignore_missing)

        if cls._is_platform('macos', platform_tag):
            # Copy the Resources directory without the unnecessary .prl files.
            cls._bundle_library('{}.framework/Resources'.format(name),
                    target_qt_dir, qt_dir, platform_tag, macos_thin_arch,
                    ignore_missing,
                    ignore=lambda d, c: [f for f in c if f.endswith('.prl')])

    @staticmethod
    def _create_qt_conf(exe):
        """ Create a qt.conf file for an executable. """

        qt_conf = os.path.join(os.path.dirname(exe), 'qt.conf')

        with open(qt_conf, 'w') as f:
            f.write('[Paths]\nPrefix = ..\n')

    @classmethod
    def _fix_linux_executable(cls, exe, qt_version):
        """ Fix a Linux executable. """

        # Note that this assumes the executable is QtWebEngineProcess.

        cls._create_qt_conf(exe)

    @classmethod
    def _fix_macos_executable(cls, exe, qt_version, macos_thin_arch):
        """ Fix a macOS executable. """

        # Note that this assumes the executable is QtWebEngineProcess.

        # pip doesn't support symbolic links in wheels so the executable will
        # be installed in its 'logical' location so adjust rpath so that it can
        # still find the Qt libraries.  The required change is simple so we
        # just patch the binary rather than require install_name_tool.  Note
        # that install_name_tool is now always needed anyway.
        with open(exe, 'rb') as f:
            contents = f.read()

        contents = contents.replace(b'@loader_path/../../../../../../../',
                b'@loader_path/../../../../../\0\0\0\0\0\0')

        with open(exe, 'wb') as f:
            f.write(contents)

        if macos_thin_arch == 'arm64':
            subprocess.run(['codesign', '-s', '-', exe])

    @classmethod
    def _fix_win_executable(cls, exe):
        """ Fix a Windows executable. """

        # Note that this assumes the executable is QtWebEngineProcess.

        cls._create_qt_conf(exe)

    @classmethod
    def _get_macos_thin_arch(cls, platform_tag):
        """ Return the single macOS architecture, or None if the platform is
        not macOS or is universal.
        """

        if cls._is_platform('macos', platform_tag):
            if platform_tag.endswith('_intel') or platform_tag.endswith('_x86_64'):
                return 'x86_64'

            if platform_tag.endswith('_arm64'):
                return 'arm64'

        return None

    @classmethod
    def _get_qt_library_dir(cls, qt_dir, platform_tag):
        """ Return the name of the directory in the Qt installation containing
        the libraries.
        """

        return os.path.join(qt_dir, cls._get_qt_library_subdir(platform_tag))

    @classmethod
    def _get_qt_library_subdir(cls, platform_tag):
        """ Return the name of the sub-directory in the Qt installation
        containing the libraries.
        """

        return 'bin' if cls._is_platform('win', platform_tag) else 'lib'

    @classmethod
    def _impl_from_library(cls, name, platform_tag, qt_version):
        """ Return the architecture-specific name of a Qt library. """

        qt_major = qt_version[0]

        if cls._is_platform('linux', platform_tag):
            return 'libQt{}{}.so.{}'.format(qt_major, name[2:], qt_major)

        if cls._is_platform('macos', platform_tag):
            framework = '5' if qt_major == 5 else 'A'

            return '{}.framework/Versions/{}/{}'.format(name, framework, name)

        if cls._is_platform('win', platform_tag):
            return 'Qt{}{}.dll'.format(qt_major, name[2:])

    @classmethod
    def _is_debug(cls, name, platform_tag):
        """ Return True if a name implies a debug version. """

        if cls._is_platform('linux', platform_tag):
            return name.endswith('.debug')

        if cls._is_platform('macos', platform_tag):
            return name.endswith('_debug.dylib') or name.endswith('.dSYM')

        if cls._is_platform('win', platform_tag):
            # Special case known non-debug DLLs that end with a 'd'.
            if name.endswith('backend.dll'):
                return False

            return name.endswith('.pdb') or name.endswith('d.dll')

    @staticmethod
    def _is_platform(metadata_arch, platform_tag):
        """ Return True if a metadata archtitecture matches a platform tag. """

        # See if it applies to all architectures.
        if metadata_arch == '':
            return True

        if metadata_arch == 'linux' and platform_tag.startswith('manylinux'):
            return True

        if metadata_arch == 'macos' and platform_tag.startswith('macosx'):
            return True

        if metadata_arch == 'win' and platform_tag.startswith('win'):
            return True

        return False
