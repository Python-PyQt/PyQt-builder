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
import subprocess
import sys

from sip5.builder import (Builder, Option, Project, PyProjectOptionException,
        UserException)


class QmakeBuilder(Builder):
    """ A project builder that uses qmake as the underlying build system. """

    def apply_defaults(self, tool):
        """ Set default values for options that haven't been set yet. """

        if tool != 'sdist':
            # Check we have a qmake.
            if self.qmake is None:
                self.qmake = self._find_exe('qmake')
                if self.qmake is None:
                    raise PyProjectOptionException('qmake',
                            "specify a working qmake or add it to PATH")
            elif not self._is_exe(self.qmake):
                raise PyProjectOptionException('qmake',
                        "'{0}' is not a working qmake".format(self.qmake))

            self.qmake = self.quote(os.path.abspath(self.qmake))

            # Use qmake to get the Qt configuration.  We do this now before
            # Project.update() is called.
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

        super().apply_defaults(tool)

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

    @staticmethod
    def qmake_quote(path):
        """ Return a path quoted for qmake if it contains spaces. """

        if ' ' in path:
            path = '$$quote({})'.format(path)

        return path

    @staticmethod
    def quote(path):
        """ Return a path with quotes added if it contains spaces. """

        if ' ' in path:
            path = '"{}"'.format(path)

        return path

    def run_make(self, exe, makefile_name):
        """ Run make against a Makefile to create an executable.  Returns the
        platform specific name of the executable, or None if an executable
        wasn't created.
        """

        project = self.project

        # Guess the name of make and set the default target and platform
        # specific name of the executable.
        if project.py_platform == 'win32':
            if self.spec == 'win32-g++':
                make = 'mingw32-make'
            else:
                make = 'nmake'

            if self.debug:
                makefile_target = 'debug'
                platform_exe = os.path.join('debug', exe + '.exe')
            else:
                makefile_target = 'release'
                platform_exe = os.path.join('release', exe + '.exe')
        else:
            make = 'make'
            makefile_target = None

            if project.py_platform == 'darwin':
                platform_exe = os.path.join(exe + '.app', 'Contents', 'MacOS',
                        exe)
            else:
                platform_exe = os.path.join('.', exe)

        # Make sure the executable doesn't exist.
        self._remove_file(platform_exe)

        args = [make, '-f', makefile_name]

        if makefile_target is not None:
            args.append(makefile_target)

        self._run_command(args)

        return platform_exe if os.path.isfile(platform_exe) else None

    def run_qmake(self, pro_name, makefile_name=None, fatal=True,
            recursive=False):
        """ Run qmake against a .pro file.  fatal is set if a qmake failure is
        considered a fatal error, otherwise False is returned if qmake fails.
        """

        # qmake doesn't behave consistently if it is not run from the directory
        # containing the .pro file - so make sure it is.
        pro_dir, pro_file = os.path.split(pro_name)
        if pro_dir != '':
            cwd = os.getcwd()
            os.chdir(pro_dir)
        else:
            cwd = None

        # Make sure the Makefile doesn't exist.
        mf_name = 'Makefile' if makefile_name is None else makefile_name
        self._remove_file(mf_name)

        # Build the command line.
        args = [self.qmake]

        # If the spec is the same as the default then we don't need to specify
        # it.
        if self.spec != self._qt_configuration['QMAKE_SPEC']:
            args.append('-spec')
            args.append(self.spec)

        if makefile_name is not None:
            args.append('-o')
            args.append(makefile_name)

        if recursive:
            args.append('-recursive')

        args.append(pro_file)

        self._run_command(args)

        # Check that the Makefile was created.
        if not os.path.isfile(mf_name):
            if fatal:
                raise UserException(
                        "{0} failed to create a makefile from {1}".format(
                                self.qmake, pro_name))

            return False

        # Restore the current directory.
        if cwd is not None:
            os.chdir(cwd)

        return True

    def verify_configuration(self, tool):
        """ Verify the configuration. """

        super().verify_configuration(tool)

        # Qt (when built with MinGW) assumes that stack frames are 16 byte
        # aligned because it uses SSE.  However the Python Windows installers
        # are built with 4 byte aligned stack frames.  We therefore need to
        # tweak the g++ flags to deal with it.
        if self.spec == 'win32-g++':
            self.qmake_variables.append('QMAKE_CFLAGS += -mstackrealign')
            self.qmake_variables.append('QMAKE_CXXFLAGS += -mstackrealign')

    @staticmethod
    def _close_command_pipe(pipe):
        """ Close the pipe returned by _open_command_pipe(). """

        pipe.close()

        try:
            os.wait()
        except:
            pass

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

    def _get_qt_configuration(self):
        """ Run qmake to get the details of the Qt configuration. """

        self.project.progress("Querying qmake about your Qt installation")

        self._qt_configuration = {}

        pipe = self._open_command_pipe(self.qmake + ' -query')

        for line in pipe:
            line = str(line, encoding=sys.stdout.encoding)
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

        self._close_command_pipe(pipe)

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

    @staticmethod
    def _is_exe(exe_path):
        """ Return True if an executable exists. """

        return os.access(exe_path, os.X_OK)

    @staticmethod
    def _open_command_pipe(cmd, and_stderr=False):
        """ Return a pipe from which a command's output can be read. """

        stderr = subprocess.STDOUT if and_stderr else subprocess.PIPE

        pipe = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE,
                stdout=subprocess.PIPE, stderr=stderr)

        return pipe.stdout

    @staticmethod
    def _remove_file(fname):
        """ Remove a file which may or may not exist. """

        try:
            os.remove(fname)
        except OSError:
            pass

    def _run_command(self, args):
        """ Run a command and display the output if requested. """

        cmd = ' '.join(args)

        if self.project.verbose:
            print(cmd)

        pipe = self._open_command_pipe(cmd, and_stderr=True)

        # Read stdout and stderr until there is no more output.
        for line in pipe:
            if self.project.verbose:
                sys.stdout.write(str(line, encoding=sys.stdout.encoding))

        self._close_command_pipe(pipe)
