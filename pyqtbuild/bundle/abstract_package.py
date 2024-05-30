# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from abc import ABC, abstractmethod
import os
import packaging

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

        # We don't support anything older that the current LTS release.
        if self.qt_version < (5, 15, 0):
            raise UserException(
                    "Version of Qt older than v5.15 are not supported")

        # Parse any package version string.
        if version_str:
            self._version = self._parse_version(version_str)

            # If we set the maintenance number to 0 then this will be the
            # version of Qt the wheel was built against.  (This is not a valid
            # assumption on Windows because of the QAxContainer problem but
            # this is handled elsewhere.)
            min_qt_version = (self._version[0], self._version[1], 0)

            # Check the versions are compatible.
            if self.qt_version < min_qt_version:
                raise UserException(
                        "The version of Qt being bundled is too old")
        else:
            self._version = None

    def bundle_msvc_runtime(self, target_qt_dir, platform_tag):
        """ Bundle the MSVC runtime. """

        # This default implementation does nothing.

    def bundle_openssl(self, target_qt_dir, openssl_dir, platform_tag):
        """ Bundle the OpenSSL DLLs. """

        # This default implementation does nothing.

    def bundle_qt(self, target_qt_dir, platform_tag, exclude, ignore_missing,
            bindings=True, subwheel=None):
        """ Bundle the relevant parts of the Qt installation.  Returns True if
        the LGPL applies to all bundled parts.
        """

        # Architecture-specific values.
        if platform_tag.startswith('manylinux'):
            module_extensions = ['.abi3.so', '.so']
        elif platform_tag.startswith('macosx'):
            module_extensions = ['.abi3.so', '.so']
        elif platform_tag.startswith('win'):
            module_extensions = ['.pyd']
        else:
            raise UserException(
                    "Unsupported platform tag '{0}'".format(platform_tag))

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
                    if os.path.isfile(os.path.join(package_dir, name + ext)):
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

            metadata.bundle(name, target_qt_dir, self._qt_dir, platform_tag,
                    self.qt_version, ignore_missing, subwheel)

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

        # Assume the current naming of the bundled Qt directory.
        qt_major_version = self.qt_version[0]

        # See if it is an older version.
        if self._version is not None:
            if (6, 0, 0) <= self._version <= (6, 0, 2):
                qt_major_version = ''
            elif self._version <= (5, 15, 3):
                qt_major_version = ''

        return os.path.join('PyQt{}'.format(qt_major_version),
                'Qt{}'.format(qt_major_version))

    @staticmethod
    def missing_executable(exe):
        """ Return True if an executable cannot be found on PATH. """

        for p in os.environ.get('PATH', '').split(os.pathsep):
            exe_path = os.path.join(p, exe)

            if os.access(exe_path, os.X_OK):
                return False

        return True

    @property
    def qt_version_str(self):
        """ The version number of the Qt installation as a string. """

        return '.'.join([str(v) for v in self.qt_version])

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
