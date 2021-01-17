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


import base64
import hashlib
import os
import zipfile

from sipbuild import UserException


def create_wheel(wheel_path, names):
    """ Create the wheel from a list of file names. """

    with zipfile.ZipFile(wheel_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        for name in names:
            zf.write(name)


def unpack_wheel(wheel_path):
    """ Unpack a wheel in the current directory. """

    try:
        zf = zipfile.ZipFile(wheel_path)
    except FileNotFoundError:
        raise UserException("Unable to find '{0}'".format(wheel_path))

    for zi in zf.infolist():
        zf.extract(zi)
        attr = zi.external_attr >> 16
        if attr:
            os.chmod(zi.filename, attr)


def write_record_file(distinfo_dir):
    """ Write the RECORD file for the contents of the current directory.
    Return a list of relative file names that were recorded.
    """

    record_path = os.path.join(distinfo_dir, 'RECORD')
    try:
        os.remove(record_path)
    except FileNotFoundError:
        pass

    # Calculate the signatures of the files.
    record = []

    for dirpath, dirnames, filenames in os.walk('.'):
        # Reproducable builds.
        dirnames.sort()
        filenames.sort()

        for filename in filenames:
            # This will result in a name with no leading '.'.
            name = os.path.relpath(os.path.join(dirpath, filename))

            with open(name, 'rb') as f:
                data = f.read()

            digest = base64.urlsafe_b64encode(
                    hashlib.sha256(data).digest()).rstrip(b'=').decode('ascii')
            record.append((name, digest, len(data)))

    # Write the file.
    names = []

    with open(record_path, 'w') as f:
        for name, digest, nbytes in record:
            name = name.replace(os.path.sep, '/')
            f.write('{},sha256={},{}\n'.format(name, digest, nbytes))
            names.append(name)

        f.write('{},,\n'.format(record_path))
        names.append(record_path)

    return names
