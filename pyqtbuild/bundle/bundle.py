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


import base64
import fnmatch
import hashlib
import os
import shutil
import zipfile

from sipbuild import UserException

from . import packages
from .verbose import verbose


def bundle(wheel_path, qt_dir, build_tag_suffix, msvc_runtime, openssl,
        openssl_dir, exclude, ignore_missing):
    """ Bundle a Qt installation with a PyQt wheel. """

    wheel_path = os.path.abspath(wheel_path)
    qt_dir = os.path.abspath(qt_dir)

    if openssl_dir:
        openssl_dir = os.path.abspath(openssl_dir)

    # Deconstruct the wheel name.
    wheel_name = os.path.basename(wheel_path)
    parts = wheel_name.split('-')

    max_nr_parts = 6
    if parts[-1] == 'unlicensed':
        max_nr_parts += 1

    if len(parts) == max_nr_parts:
        # Remove the build tag.
        del parts[2]
    elif len(parts) != max_nr_parts - 1:
        raise UserException(
                "Unable to recognise '{0}' as a wheel name".format(wheel_name))

    # Get the package object.
    package_name = parts[0].split('_')[0]
    package_factory = packages.__dict__.get(package_name)

    if package_factory is None:
        raise UserException(
                "'{0}' is not a supported package".format(package_name))

    package = package_factory(parts[1], qt_dir)

    # Construct the name of the bundled wheel.
    build_tag = package.get_qt_version_str()

    if build_tag_suffix:
        build_tag += build_tag_suffix

    parts.insert(2, build_tag)

    bundled_wheel_name = '-'.join(parts)
    bundled_wheel_path = os.path.abspath(bundled_wheel_name)

    bundled_wheel_dir = bundled_wheel_name
    for tail in ('-unlicensed', '.whl'):
        if bundled_wheel_dir.endswith(tail):
            bundled_wheel_dir = bundled_wheel_dir[:-len(tail)]

    arch = bundled_wheel_dir.split('-')[-1]

    # Create the directory to contain the existing wheel contents.
    shutil.rmtree(bundled_wheel_dir, ignore_errors=True)
    os.mkdir(bundled_wheel_dir)

    # Unpack the existing wheel.
    saved_cwd = os.getcwd()
    os.chdir(bundled_wheel_dir)

    verbose("Unpacking {0}".format(wheel_name))

    try:
        zf = zipfile.ZipFile(wheel_path)
    except FileNotFoundError:
        raise UserException("Unable to find '{0}'".format(wheel_path))

    for zi in zf.infolist():
        zf.extract(zi)
        attr = zi.external_attr >> 16
        if attr:
            os.chmod(zi.filename, attr)

    # Remove any existing bundled Qt installation while protecting some
    # specific directories.
    verbose("Removing any existing Qt bundle")

    target_qt_dir = package.get_target_qt_dir()
    if os.path.isdir(target_qt_dir):
        for fn in os.listdir(target_qt_dir):
            if fn not in ('qsci', ):
                shutil.rmtree(os.path.join(target_qt_dir, fn),
                        ignore_errors=True)

    # Bundle the relevant parts of the Qt installation.
    package.bundle_qt(target_qt_dir, qt_dir, arch, exclude, ignore_missing)

    if arch in ('win32', 'win_amd64'):
        # Bundle the MSVC runtime if required.
        if msvc_runtime:
            package.bundle_msvc_runtime(target_qt_dir, arch)

        # Bundle OpenSSL if required.
        if openssl:
            package.bundle_openssl(target_qt_dir, openssl_dir, arch)

    # Rewrite the wheel's RECORD file.
    verbose("Writing the RECORD file")

    for dist_info in os.listdir('.'):
        if fnmatch.fnmatch(dist_info, '*.dist-info'):
            break
    else:
        raise UserException(
                "'{0}' doesn't contain a .dist-info directory".format(
                        wheel_path))

    record_path = os.path.join(dist_info, 'RECORD')
    os.remove(record_path)

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

    with open(record_path, 'w') as f:
        for name, digest, nbytes in record:
            name = name.replace(os.path.sep, '/')
            f.write('{},sha256={},{}\n'.format(name, digest, nbytes))

        f.write('{},,\n'.format(record_path))

    # Create the bundled wheel.
    verbose("Writing {0}".format(bundled_wheel_name))

    with zipfile.ZipFile(bundled_wheel_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        for name, _, _ in record:
            zf.write(name)

        zf.write(record_path)

    # Tidy up.
    os.chdir(saved_cwd)
    shutil.rmtree(bundled_wheel_dir)

    verbose("Bundling complete.")
