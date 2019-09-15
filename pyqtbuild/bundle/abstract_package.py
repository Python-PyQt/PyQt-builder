# Copyright (c) 2019, Riverbank Computing Limited
# All rights reserved.
#
# This copy of SIP is licensed for use under the terms of the SIP License
# Agreement.  See the file LICENSE for more details.
#
# This copy of SIP may also used under the terms of the GNU General Public
# License v2 or v3 as published by the Free Software Foundation which can be
# found in the files LICENSE-GPL2 and LICENSE-GPL3 included in this package.
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


from abc import ABC
import os
import packaging
from sipbuild import UserException


class AbstractPackage(ABC):
    """ This specifies the API of a package. """

    def __init__(self, version_str, qt_dir):
        """ Initialise the package. """

        # Parse the version string.
        self._version = self._parse_version(version_str)

        # If we set the maintenance number to 0 then this will be the version
        # of Qt the wheel was built against.  (This is not a valid assumption
        # on Windows because of the QAxContainer problem but this is handled
        # elsewhere.)
        _min_qt_version = list(self._version)
        _min_qt_version[-1] = 0

        # Get the Qt version being bundled.
        self._qt_version = self._parse_version(
                os.path.basename(os.path.dirname(qt_dir)))

        # Check the versions are compatible.
        if self._qt_version < _min_qt_version:
            raise UserException("The version of Qt being bundled is too old")

    def bundle_msvc_runtime(self, target_qt_dir):
        """ Bundle the MSVC runtime. """

        # This default implementation does nothing.

    def bundle_openssl(self, target_qt_dir, openssl_dir):
        """ Bundle the OpenSSL DLLs. """

        # This default implementation does nothing.

    def bundle_qt(self, target_qt_dir):
        """ Bundle the relevant parts of the Qt installation. """

        # TODO

    def get_qt_version_str(self):
        """ Return the version number of the Qt installation to bundle. """

        return '.'.join([str(v) for v in self._qt_version])

    def get_target_qt_dir(self):
        """ Return the directory, relative to the wheel root, containing the
        bundled Qt directory.
        """

        return os.path.join('PyQt{}'.format(self._version[0]), 'Qt')

    @staticmethod
    def _parse_version(version_str):
        """ Parse a version string as a 3 element list of major, minor and
        maintenance versions.
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

        return version
