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

from sip5.builder import Builder, Option, Project, PyProjectOptionException


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
        options.append(
                Option('qmake', help="the pathname of qmake is FILE",
                        metavar="FILE", tools='build install wheel'))

        options.append(
                Option('make', option_type=bool, inverted=True,
                        help="do not run make or nmake", tools='build'))

        return options

    def install_into(self, opaque, target_dir, wheel_tag=None):
        """ Install the project into a target directory. """

        # TODO

    def verify_configuration(self):
        """ Verify the configuration. """

        super().verify_configuration()

        # Check we have a qmake.
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
    def _is_exe(exe):
        """ Return True if an executable exists. """

        return os.access(exe_path, os.X_OK)
