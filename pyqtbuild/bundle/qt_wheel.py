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


import os
import shutil

from sipbuild import UserException

from . import packages
from .verbose import verbose
from .wheel import create_wheel, write_record_file


def qt_wheel(package, qt_dir, build_tag, suffix, msvc_runtime, openssl,
        openssl_dir, exclude, arch):
    """ Create a wheel containing the subset of a Qt installation required for
    a particular PyQt package.
    """

    if openssl_dir:
        openssl_dir = os.path.abspath(openssl_dir)

    # Normalise the name of the package.
    package_name = package.replace('-', '_')
    package_title = package_name.replace('_', '-')

    # Get the package object.
    package_factory = packages.__dict__.get(package_name)

    if package_factory is None:
        raise UserException(
                "'{0}' is not a supported package".format(package_title))

    package = package_factory(qt_dir)

    version_str = package.qt_version_str
    if suffix:
        version_str += suffix

    # Construct the tag.
    qt_arch = os.path.basename(qt_dir)
    if qt_arch == 'gcc_64':
        platform_tag = 'manylinux{}_x86_64'.format(
                '_2_28' if package.qt_version[0] == 6 else '2014')
    elif qt_arch in ('macos', 'clang_64'):
        if package.qt_version < (6, 2, 0):
            if arch is not None:
                raise UserException(
                        "'--arch' may only be specified for Qt v6.2 and later")

            subarch = 'x86_64'
        elif arch is None:
            subarch = 'universal2'
        else:
            subarch = arch

        if package.qt_version[0] == 5:
            sdk_version = '10_13'
        elif subarch == 'arm64':
            sdk_version = '11_0'
        else:
            sdk_version = '10_14'

        platform_tag = 'macosx_{}_{}'.format(sdk_version, subarch)
    elif qt_arch.startswith('msvc'):
        platform_tag = 'win_amd64' if qt_arch.endswith('_64') else 'win32'
    else:
        raise UserException(
                "Qt architecture '{0}' is unsupported".format(qt_arch))

    tag_parts = ['py3', 'none', platform_tag]
    tag = '-'.join(tag_parts)

    # Construct the name of the wheel.
    name_parts = [package_name + '_Qt' + version_str[0]]
    name_parts.append(version_str)

    distinfo_dir = '-'.join(name_parts) + '.dist-info'

    if build_tag:
        name_parts.append(build_tag)

    name_parts += tag_parts

    wheel_name = '-'.join(name_parts)
    wheel_path = os.path.abspath(wheel_name + '.whl')

    # Create the directory to contain the wheel contents.
    shutil.rmtree(wheel_name, ignore_errors=True)
    os.mkdir(wheel_name)

    saved_cwd = os.getcwd()
    os.chdir(wheel_name)

    # Bundle the relevant parts of the Qt installation.
    target_qt_dir = package.get_target_qt_dir()
    lgpl = package.bundle_qt(target_qt_dir, platform_tag, exclude,
            ignore_missing=True, bindings=False)

    if platform_tag in ('win32', 'win_amd64'):
        # Bundle the MSVC runtime if required.
        if msvc_runtime:
            package.bundle_msvc_runtime(target_qt_dir, platform_tag)

        # Bundle OpenSSL if required.
        if openssl:
            package.bundle_openssl(target_qt_dir, openssl_dir, platform_tag)

    # Create the .dist-info directory and populate it from the prototypes.
    os.mkdir(distinfo_dir)

    proto_dir = os.path.join(os.path.dirname(__file__), 'qt_wheel_distinfo')
    for proto in os.listdir(proto_dir):
        src = os.path.join(proto_dir, proto)
        dst = os.path.join(distinfo_dir, proto)

        if proto == 'METADATA':
            with open(src) as s:
                metadata = s.read()

            metadata = metadata.replace('@RB_PACKAGE@', package_title)
            metadata = metadata.replace('@RB_MAJOR_VERSION@', version_str[0])
            metadata = metadata.replace('@RB_VERSION@', version_str)
            metadata = metadata.replace('@RB_LICENSE@',
                    "LGPL v3" if lgpl else "GPL v3")

            with open(dst, 'w') as d:
                d.write(metadata)
        elif proto == 'WHEEL':
            with open(src) as s:
                wheel_data = s.read()

            with open(dst, 'w') as d:
                d.write(wheel_data)
                d.write('Tag: {}\n'.format(tag))

                if build_tag:
                    d.write('Build: {}\n'.format(build_tag))
        else:
            shutil.copy(src, dst)

    # Write the wheel's RECORD file.
    verbose("Writing the RECORD file")
    names = write_record_file(distinfo_dir)

    # Create the wheel.
    verbose("Writing {0}".format(wheel_name))
    create_wheel(wheel_path, names)

    # Tidy up.
    os.chdir(saved_cwd)
    shutil.rmtree(wheel_name)

    verbose("Wheel build complete.")
