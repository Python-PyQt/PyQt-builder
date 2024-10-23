# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from ..abstract_package import AbstractPackage
from ..qt_metadata import VersionedMetadata


# The Qt meta-data for this package.
_QT_METADATA = {
    'Qt3DAnimation':
        VersionedMetadata(
            lib_deps={'': ('Qt3DQuickAnimation', )}),

    'Qt3DCore':
        VersionedMetadata(
            lib_deps={'': ('Qt3DQuick', )},
            qml_names=('Qt3D', )),

    'Qt3DExtras':
        VersionedMetadata(
            lib_deps={'': ('Qt3DQuickExtras', )}),

    'Qt3DInput':
        VersionedMetadata(
            lib_deps={'': ('Qt3DQuickInput', 'QtGamepad')}),

    'Qt3DLogic':
        VersionedMetadata(),

    'Qt3DRender':
        VersionedMetadata(
            lib_deps={
                'win': ('QtConcurrent', ),
                '': ('Qt3DQuickRender', 'Qt3DQuickScene2D')}),
}


class PyQt3D(AbstractPackage):
    """ The PyQt3D package. """

    def get_qt_metadata(self):
        """ Return the package-specific meta-data describing the parts of Qt to
        install.
        """

        return _QT_METADATA
