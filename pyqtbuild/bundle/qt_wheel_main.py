# Copyright (c) 2022, Riverbank Computing Limited
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

    args = parser.parse_args()

    try:
        set_verbose(args.verbose)

        try:
            arch = args.arch
        except AttributeError:
            arch = None

        qt_wheel(package=args.packages[0], qt_dir=args.qt_dir,
                build_tag=args.build_tag, suffix=args.suffix,
                msvc_runtime=args.msvc_runtime, openssl=args.openssl,
                openssl_dir=args.openssl_dir, exclude=args.exclude, arch=arch)
    except Exception as e:
        handle_exception(e)

    return 0
