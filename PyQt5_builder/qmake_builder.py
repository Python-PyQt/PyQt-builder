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


import os
import sys

from sip5.builder import (Builder, Option, Project, PyProjectOptionException,
        UserException)


class QmakeBuilder(Builder):
    """ A project builder that uses qmake as the underlying build system. """

    def compile(self):
        """ Compile the project.  The returned opaque object is always None.
        """

        # TODO

        return None

    def get_options(self):
        """ Return the sequence of configurable options. """

        # Get the standard options.
        options = super().get_options()

        # Add our new options.
        options.append(Option('qmake_variables', option_type=list))

        options.append(
                Option('make', option_type=bool, inverted=True,
                        help="do not run make or nmake", tools='build'))

        options.append(
                Option('qmake', help="the pathname of qmake is FILE",
                        metavar="FILE", tools='build install wheel'))

        options.append(
                Option('spec', help="pass -spec SPEC to qmake",
                        metavar="SPEC", tools='build install wheel'))

        return options

    def install_into(self, opaque, target_dir, wheel_tag=None):
        """ Install the project into a target directory. """

        # TODO

    def apply_defaults(self):
        """ Set default values for options that haven't been set yet. """

        super().apply_defaults()

        # Check we have a qmake.  Note that we don't do this in
        # verify_configuration() because it is needed by setup() which is
        # called first.
        if self.qmake:
            if not self._is_exe(self.qmake):
                raise PyProjectOptionException('qmake',
                        "'{0}' is not a working qmake".format(self.qmake))
        else:
            self.qmake = self._find_exe('qmake')
            if self.qmake is None:
                raise PyProjectOptionException('qmake',
                        "specify a working qmake or add it to PATH")

        self.qmake = os.path.abspath(self.qmake)

        # Use qmake to get the Qt configuration.
        self._get_qt_configuration()

        # Now apply defaults for any options that depend on the Qt
        # configuration.
        if self.spec is None:
            self.spec = self._qt_configuration['QMAKE_SPEC']

            # The binary OS/X Qt installer used to default to XCode.  If so
            # then use macx-clang.
            if self.spec == 'macx-xcode':
                # This will exist (and we can't check anyway).
                self.spec = 'macx-clang'

    def verify_configuration(self):
        """ Verify the configuration. """

        # Qt (when built with MinGW) assumes that stack frames are 16 byte
        # aligned because it uses SSE.  However the Python Windows installers
        # are built with 4 byte aligned stack frames.  We therefore need to
        # tweak the g++ flags to deal with it.
        if self.spec == 'win32-g++':
            self.qmake_variables.append('QMAKE_CFLAGS += -mstackrealign')
            self.qmake_variables.append('QMAKE_CXXFLAGS += -mstackrealign')

    def _get_qt_configuration(self):
        """ Run qmake to get the details of the Qt configuration. """

        self.project.progress("Querying qmake about your Qt installation")

        self._qt_configuration = {}

        pipe = os.popen(self.qmake + ' -query')

        for line in pipe:
            line = line.strip()

            tokens = line.split(':', maxsplit=1)
            if isinstance(tokens, list):
                if len(tokens) != 2:
                    raise UserException(
                            "Unexpected output from qmake: '{0}'".format(line))

                name, value = tokens
            else:
                name = tokens
                value = None

            name = name.replace('/', '_')

            self._qt_configuration[name] = value

        pipe.close()

        # Get the Qt version.
        self.qt_version = 0
        try:
            qt_version_str = self._qt_configuration['QT_VERSION']
            for v in qt_version_str.split('.'):
                self.qt_version <<= 8
                self.qt_version += int(v)
        except AttributeError:
            qt_version_str = "3"

        if self.qt_version < 0x050000:
            raise UserException(
                    "Qt v5.0 or later is required and you seem to be using "
                            "v{0}".format(qt_version_str))

    @classmethod
    def _find_exe(cls, exe):
        """ Find an executable, ie. the first on the path. """

        if sys.platform == 'win32':
            exe += '.exe'

        for d in os.environ.get('PATH', '').split(os.pathsep):
            exe_path = os.path.join(d, exe)

            if cls._is_exe(exe_path):
                return exe_path

        return None

    @staticmethod
    def _is_exe(exe_path):
        """ Return True if an executable exists. """

        return os.access(exe_path, os.X_OK)
