# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


import fnmatch
import os
import shutil

from sipbuild import UserException

from . import packages
from .verbose import verbose
from .wheel import create_wheel, unpack_wheel, write_record_file


def bundle(wheel_path, qt_dir, build_tag_suffix, msvc_runtime, openssl,
        openssl_dir, exclude, ignore_missing, arch):
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

    # If an architecture is specified then it must be supported by the wheel.
    if arch:
        if arch in parts[-1]:
            pass
        elif 'universal2' in parts[-1]:
            parts[-1] = parts[-1].replace('universal2', arch)
        else:
            raise UserException(
                    "'{0}' is not supported by {1}".format(arch, wheel_name))

    # Get the package object.
    sub_parts = parts[0].split('_')
    if sub_parts[-1] == 'commercial':
        sub_parts.pop()

    package_name = '_'.join(sub_parts)
    package_title = package_name.replace('_', '-')
    package_factory = packages.__dict__.get(package_name)

    if package_factory is None:
        raise UserException(
                "'{0}' is not a supported package".format(package_title))

    package = package_factory(qt_dir, parts[1])

    # Construct the name of the bundled wheel.
    build_tag = package.qt_version_str

    if build_tag_suffix:
        build_tag += build_tag_suffix

    parts.insert(2, build_tag)

    bundled_wheel_name = '-'.join(parts)
    bundled_wheel_path = os.path.abspath(bundled_wheel_name)

    bundled_wheel_dir = bundled_wheel_name
    for tail in ('-unlicensed', '.whl'):
        if bundled_wheel_dir.endswith(tail):
            bundled_wheel_dir = bundled_wheel_dir[:-len(tail)]

    platform_tag = bundled_wheel_dir.split('-')[-1]

    # Create the directory to contain the existing wheel contents.
    shutil.rmtree(bundled_wheel_dir, ignore_errors=True)
    os.mkdir(bundled_wheel_dir)

    # Unpack the existing wheel.
    saved_cwd = os.getcwd()
    os.chdir(bundled_wheel_dir)

    verbose("Unpacking {0}".format(wheel_name))
    unpack_wheel(wheel_path)

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
    package.bundle_qt(target_qt_dir, platform_tag, exclude, ignore_missing)

    if platform_tag in ('win32', 'win_amd64'):
        # Bundle the MSVC runtime if required.
        if msvc_runtime:
            package.bundle_msvc_runtime(target_qt_dir, platform_tag)

        # Bundle OpenSSL if required.
        if openssl:
            package.bundle_openssl(target_qt_dir, openssl_dir, platform_tag)

    # Find the .dist-info directory.
    for distinfo_dir in os.listdir('.'):
        if fnmatch.fnmatch(distinfo_dir, '*.dist-info'):
            break
    else:
        raise UserException(
                "'{0}' doesn't contain a .dist-info directory".format(
                        wheel_path))

    # Remove any dependency on an external Qt wheel from the METADATA file.
    update_metadata = False
    updated_metadata = ''
    qt_wheel = package_title + '-Qt'
    metadata_path = os.path.join(distinfo_dir, 'METADATA')

    with open(metadata_path) as f:
        for line in f:
            if 'Requires-Dist:' in line and qt_wheel in line:
                update_metadata = True
            else:
                updated_metadata += line

    if update_metadata:
        verbose("Updating the METADATA file")

        with open(metadata_path, 'w') as f:
            f.write(updated_metadata)

    # Rewrite the wheel's RECORD file.
    verbose("Writing the RECORD file")
    names = write_record_file(distinfo_dir)

    # Create the bundled wheel.
    verbose("Writing {0}".format(bundled_wheel_name))
    create_wheel(bundled_wheel_path, names)

    # Tidy up.
    os.chdir(saved_cwd)
    shutil.rmtree(bundled_wheel_dir)

    verbose("Bundling complete.")
