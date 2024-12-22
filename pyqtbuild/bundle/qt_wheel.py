# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


import os
import shutil

from sipbuild import UserException

from . import packages
from .verbose import verbose
from .wheel import create_wheel, write_record_file


def qt_wheel(package, qt_dir, build_tag, suffix, msvc_runtime, openssl,
        openssl_dir, exclude, arch, subwheel):
    """ Create a wheel containing the subset of a Qt installation required for
    a particular PyQt package.
    """

    if openssl_dir:
        openssl_dir = os.path.abspath(openssl_dir)

    # Normalise the name of the package.
    package_name = package.replace('-', '_')

    # Get the package object.
    package_factory = packages.__dict__.get(package_name)

    if package_factory is None:
        raise UserException(f"'{package}' is not a supported package")

    package = package_factory(qt_dir)

    version_str = package.qt_version_str
    if suffix:
        version_str += suffix

    # Construct the tag.
    qt_arch = os.path.basename(qt_dir)

    if qt_arch.startswith('gcc_'):
        if qt_arch == 'gcc_arm64':
            wheel_arch = 'aarch64'
            manylinux = '_2_39'
        else:
            wheel_arch = 'x86_64'

            if package.qt_version >= (6, 0, 0):
                manylinux = '_2_28'
            else:
                manylinux = '2014'

        platform_tag = f'manylinux{manylinux}_{wheel_arch}'

    elif qt_arch in ('macos', 'clang_64', 'x86_64', 'arm64'):
        if package.qt_version < (5, 15, 10) or (6, 0, 0) <= package.qt_version < (6, 2, 0):
            if arch is not None:
                raise UserException(
                        "'--arch' may only be specified for Qt v5.15.10 and later or Qt v6.2 and later")

            subarch = 'x86_64'
        elif arch is None:
            # Assume it is universal unless the installed Qt architecture is
            # specific.
            subarch = qt_arch if qt_arch in ('x86_64', 'arm64') else 'universal2'
        else:
            subarch = arch

        if subarch == 'arm64':
            sdk_version = '11_0'
        elif package.qt_version[0] == 5:
            sdk_version = '10_13'
        else:
            sdk_version = '10_14'

        platform_tag = 'macosx_{}_{}'.format(sdk_version, subarch)

    elif qt_arch.startswith('msvc'):
        if qt_arch.endswith('_64'):
            platform_tag = 'win_amd64'
        elif qt_arch.endswith('_arm64'):
            platform_tag = 'win_arm64'
        else:
            platform_tag = 'win32'

    else:
        raise UserException(
                "Qt architecture '{0}' is unsupported".format(qt_arch))

    tag_parts = ['py3', 'none', platform_tag]
    tag = '-'.join(tag_parts)

    package_title = package_name.replace('_', '-')
    qt_version_suffix = '-Qt' + version_str[0]

    # Determine sub-wheel dependent values'
    subwheel_full_name = f'{package_title}Subwheel{qt_version_suffix}'

    if subwheel is True:
        package_full_name = subwheel_full_name
        package_requires = ''
    elif subwheel is False:
        package_full_name = package_title + qt_version_suffix
        package_requires = f'Requires-Dist: {subwheel_full_name} (=={version_str})\n'
    else:
        package_full_name = package_title + qt_version_suffix
        package_requires = ''

    # Construct the name of the wheel.
    name_parts = [package_full_name.replace('-', '_')]
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
            ignore_missing=True, bindings=False, subwheel=subwheel)

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
            metadata = metadata.replace('@RB_PACKAGE_NAME@', package_full_name)
            metadata = metadata.replace('@RB_PACKAGE_REQUIRES@',
                    package_requires)
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
        elif proto.startswith('LICENSE.'):
            if proto.endswith('.lgpl3' if lgpl else '.gpl3'):
                shutil.copy(src, os.path.join(distinfo_dir, 'LICENSE'))
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
