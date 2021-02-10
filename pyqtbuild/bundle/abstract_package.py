# Copyright (c) 2021, Riverbank Computing Limited
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


from abc import ABC, abstractmethod
import os
import packaging
import subprocess

from sipbuild import UserException

from .qt_metadata import VersionedMetadata
from .verbose import verbose


class AbstractPackage(ABC):
    """ This specifies the API of a package. """

    def __init__(self, qt_dir, version_str=None):
        """ Initialise the package. """

        self._qt_dir = os.path.abspath(qt_dir)

        # Get the Qt version.
        self.qt_version = self._parse_version(
                os.path.basename(os.path.dirname(self._qt_dir)))

        # Parse any package version string.
        if version_str:
            version = self._parse_version(version_str)

            # If we set the maintenance number to 0 then this will be the
            # version of Qt the wheel was built against.  (This is not a valid
            # assumption on Windows because of the QAxContainer problem but
            # this is handled elsewhere.)
            min_qt_version = (version[0], version[1], 0)

            # Check the versions are compatible.
            if self.qt_version < min_qt_version:
                raise UserException(
                        "The version of Qt being bundled is too old")

    def bundle_msvc_runtime(self, target_qt_dir, arch):
        """ Bundle the MSVC runtime. """

        # This default implementation does nothing.

    def bundle_openssl(self, target_qt_dir, openssl_dir, arch):
        """ Bundle the OpenSSL DLLs. """

        # This default implementation does nothing.

    def bundle_qt(self, target_qt_dir, arch, exclude, ignore_missing,
            bindings=True):
        """ Bundle the relevant parts of the Qt installation.  Returns True if
        the LGPL applies to all bundled parts.
        """

        # Architecture-specific values.
        if arch.startswith('manylinux'):
            metadata_arch = 'linux'
            module_extensions = ['.abi3.so', '.so']
        elif arch.startswith('macosx'):
            metadata_arch = 'macos'
            module_extensions = ['.abi3.so', '.so']
        elif arch.startswith('win'):
            metadata_arch = 'win'
            module_extensions = ['.pyd']
        else:
            raise UserException("Unsupported platform tag '{0}'".format(arch))

        package_dir = os.path.dirname(target_qt_dir)
        lgpl = True

        for name, metadata in self.get_qt_metadata().items():
            # Ignore a module if it is explicitly excluded.
            if name in exclude:
                continue

            # Get the metadata for the Qt version.
            if isinstance(metadata, VersionedMetadata):
                metadata = [metadata]

            metadata = [md for md in metadata
                    if md.is_applicable(self.qt_version)]

            if len(metadata) == 0:
                continue

            metadata = metadata[0]

            # See if we need to check if the bindings are present to decide to
            # bundle this part of Qt.
            if bindings:
                # Find the bindings.
                for ext in module_extensions:
                    bindings = os.path.join(package_dir, name + ext)
                    if os.path.isfile(bindings):
                        if self.qt_version < (5, 15, 0):
                            # This isn't necessary for newer wheels built with
                            # '--target-qt-dir' but we still have to handle
                            # older wheels (ie. using versions of Qt released
                            # before '--target-qt-dir' was added.
                            if metadata_arch == 'linux':
                                self._fix_linux_rpath(bindings)
                            elif metadata_arch == 'macos':
                                self._fix_macos_rpath(bindings)

                        break
                else:
                    verbose(
                            "Skipping {0} as it is not in the wheel".format(
                                    name))
                    continue
            elif metadata.legacy:
                # We don't bundle Qt for legacy bindings.
                continue

            lgpl = lgpl and metadata.lgpl

            metadata.bundle(name, target_qt_dir, self._qt_dir, metadata_arch,
                    self.qt_version, ignore_missing)

        return lgpl

    @abstractmethod
    def get_qt_metadata(self):
        """ Return the package-specific meta-data describing the parts of Qt to
        install.
        """

    def get_target_qt_dir(self):
        """ Return the directory, relative to the wheel root, containing the
        bundled Qt directory.
        """

        return os.path.join('PyQt{}'.format(self.qt_version[0]), 'Qt')

    @property
    def qt_version_str(self):
        """ The version number of the Qt installation as a string. """

        return '.'.join([str(v) for v in self.qt_version])

    @classmethod
    def _fix_linux_rpath(cls, bindings):
        """ Fix the rpath for Linux bindings. """

        if cls._missing_executable('chrpath'):
            raise UserException("'chrpath' must be installed on your system")

        subprocess.run(['chrpath', '--replace', '$ORIGIN/Qt/lib', bindings])

    @classmethod
    def _fix_macos_rpath(cls, bindings):
        """ Fix the rpath for macOS bindings. """

        if cls._missing_executable('otool') or cls._missing_executable('install_name_tool'):
            raise UserException(
                    "'otool' and 'install_name_tool' from Xcode must be "
                    "installed on your system")

        # Use otool to get all current rpaths.
        pipe = subprocess.Popen('otool -l {}'.format(bindings), shell=True,
                stdout=subprocess.PIPE, universal_newlines=True)

        # Delete any existing rpaths.
        args = []
        new_rpath = '@loader_path/Qt/lib'
        add_new_rpath = True

        for line in pipe.stdout:
            parts = line.split()

            if len(parts) >= 2 and parts[0] == 'path':
                rpath = parts[1]

                if rpath == new_rpath:
                    add_new_rpath = False
                else:
                    args.append('-delete_rpath')
                    args.append(rpath)

        rc = pipe.wait()
        if rc != 0:
            raise UserException("otool returned a non-zero exit status")

        # Add an rpath for the bundled Qt installation if it is not already
        # there.
        if add_new_rpath:
            args.append('-add_rpath')
            args.append('@loader_path/Qt/lib')

        if args:
            args.insert(0, 'install_name_tool')
            args.append(bindings)
            subprocess.run(args)

    @staticmethod
    def _missing_executable(exe):
        """ Return True if an executable cannot be found on PATH. """

        for p in os.environ.get('PATH', '').split(os.pathsep):
            exe_path = os.path.join(p, exe)

            if os.access(exe_path, os.X_OK):
                return False

        return True

    @staticmethod
    def _parse_version(version_str):
        """ Parse a version string as a 3-tuple of major, minor and maintenance
        versions.
        """

        base_version = packaging.version.parse(version_str).base_version
        base_version = base_version.split('.')
        del base_version[3:]

        while len(base_version) < 3:
            base_version.append('0')

        version = []
        for part in base_version:
            try:
                version.append(int(part))
            except ValueError:
                raise UserException(
                        "Unable to parse '{0}' as a version number".format(
                                version_str))

        return tuple(version)
