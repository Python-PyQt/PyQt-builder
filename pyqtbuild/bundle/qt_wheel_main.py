# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from argparse import ArgumentParser
import sys

from sipbuild import handle_exception

from ..version import PYQTBUILD_VERSION_STR

from .qt_wheel import qt_wheel
from .verbose import set_verbose


def main():
    """ Create a Qt wheel to support a particular PyQt package. """

    # Parse the command line.
    parser = ArgumentParser(
            description="Create a wheel containing the Qt installation for a PyQt package.")

    parser.add_argument('-V', '--version', action='version',
            version=PYQTBUILD_VERSION_STR)

    parser.add_argument('--verbose', default=False, action='store_true',
            help="enable verbose progress messages")

    if sys.platform == 'darwin':
        parser.add_argument('--arch', choices=('x86_64', 'arm64'),
                help="the architecture to create the wheel for")

    parser.add_argument('--build-tag', metavar='TAG',
            help="use TAG as the build tag in the wheel name")

    parser.add_argument('--exclude', metavar="NAME", default=[],
            action='append', help="exclude the NAME library from the wheel")

    parser.add_argument('--no-msvc-runtime', dest='msvc_runtime', default=True,
            action='store_false',
            help="don't include msvcp140.dll, concrt140.dll and "
                    "vcruntime140.dll in the wheel")

    parser.add_argument('--no-openssl', dest='openssl', default=True,
            action='store_false',
            help="don't include the OpenSSL DLLs in the wheel")

    parser.add_argument('--openssl-dir', metavar='DIR',
            help="replace the OpenSSL DLLs with the versions in DIR")

    parser.add_argument('--qt-dir', metavar='DIR', required=True,
            help="the Qt installation in DIR to be copied to the wheel")

    parser.add_argument('--suffix', metavar='SUFFIX',
            help="append SUFFIX to the Qt version number")

    parser.add_argument(dest='packages', nargs=1, help="the PyQt package",
            metavar="PACKAGE")

    parser.add_argument('--subwheel', choices=('generate', 'exclude'),
            default=None,
            help="generate the package's sub-wheel or exclude the sub-wheel "
                    "contents from the main wheel [default: generate a full "
                    "wheel]")

    args = parser.parse_args()

    try:
        set_verbose(args.verbose)

        try:
            arch = args.arch
        except AttributeError:
            arch = None

        subwheel = args.subwheel

        if subwheel == 'generate':
            subwheel = True
        elif subwheel == 'exclude':
            subwheel = False

        qt_wheel(package=args.packages[0], qt_dir=args.qt_dir,
                build_tag=args.build_tag, suffix=args.suffix,
                msvc_runtime=args.msvc_runtime, openssl=args.openssl,
                openssl_dir=args.openssl_dir, exclude=args.exclude, arch=arch,
                subwheel=subwheel)
    except Exception as e:
        handle_exception(e)

    return 0
