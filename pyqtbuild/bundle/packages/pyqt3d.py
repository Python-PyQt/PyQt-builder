# Copyright (c) 2019, Riverbank Computing Limited
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
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


from ..abstract_package import AbstractPackage
from ..qt_metadata import VersionedMetadata


# The Qt meta-data for this package.
_QT_METADATA = {
    # Although Qt3D was actually added in Qt v5.6 it wasn't supported by PyQt
    # until v5.7.
    'Qt3DAnimation':
        VersionedMetadata(version=(5, 10, 0),
            lib_deps={'': ('Qt3DQuickAnimation', )}),

    'Qt3DCore':
        VersionedMetadata(version=(5, 7, 0),
            lib_deps={'': ('Qt3DQuick', )},
            qml=True,
            qml_names=('Qt3D', )),

    'Qt3DExtras':
        VersionedMetadata(version=(5, 7, 0),
            lib_deps={'': ('Qt3DQuickExtras', )}),

    'Qt3DInput': (
        VersionedMetadata(version=(5, 7, 1),
            lib_deps={'': ('Qt3DQuickInput', 'QtGamepad')}),
        VersionedMetadata(version=(5, 7, 0),
            lib_deps={'': ('Qt3DQuickInput', )})),

    'Qt3DLogic':
        VersionedMetadata(version=(5, 7, 0)),

    'Qt3DRender':
        VersionedMetadata(version=(5, 7, 0),
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
