# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2026 Phil Thompson <phil@riverbankcomputing.com>


from ..abstract_package import AbstractPackage
from ..qt_metadata import VersionedMetadata


# The Qt meta-data for this package.
_QT_METADATA = {
    'QtPdf':
        VersionedMetadata(version=(6, 140, 0),
                lib_deps={'': ('QtPdfQuick', )}),

    'QtPdfWidgets':
        VersionedMetadata(version=(6, 140, 0)),
}


class PyQt6_Pdf(AbstractPackage):
    """ The PyQt6-Pdf package. """

    # The Qt module version is not the same as the Qt version and so must be
    # specified on the command line.
    qt_module_version_required = True

    def get_qt_metadata(self):
        """ Return the package-specific meta-data describing the parts of Qt to
        install.
        """

        return _QT_METADATA
