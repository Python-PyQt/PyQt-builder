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

    def compile(self, target_dir):
        """ Compile the project.  The returned opaque object is always None.
        """

        project = self.project

        # Create the .pro file for each set of bindings.
        subdirs = [self._generate_bindings_pro_file(b, target_dir)
                for b in project.bindings]

        # Create the top-level .pro file.
        project.progress("Generating the top-level .pro file")

        pro_name = os.path.join(project.build_dir, project.name + '.pro')
        pro = project.open_for_writing(pro_name)

        pro.write('''TEMPLATE = subdirs
CONFIG += ordered nostrip
SUBDIRS = {}
'''.format(' '.join(subdirs)))

        pro.close()

        # Run qmake to generate the Makefiles.
        # TODO

        # Run make, if requested, to generate the bindings.
        if self.make:
            # TODO
            raise NotImplementedError

        return None

    def get_options(self):
        """ Return the sequence of configurable options. """

        # Get the standard options.
        options = super().get_options()

        # Add our new options.
        options.append(
                Option('make', option_type=bool, inverted=True,
                        help="do not run make or nmake", tools='build'))

        options.append(
                Option('qmake', help="the pathname of qmake is FILE",
                        metavar="FILE", tools='build install wheel'))

        options.append(
                Option('qmake_settings', option_type=list,
                        help="add the 'NAME += VALUE' setting to any .pro file",
                        metavar="'NAME += VALUE'",
                        tools='build install wheel'))

        options.append(
                Option('spec', help="pass -spec SPEC to qmake",
                        metavar="SPEC", tools='build install wheel'))

        return options

    def install_into(self, opaque, target_dir, wheel_tag=None):
        """ Install the project into a target directory. """

        # Run make install to install the bindings.

        # TODO
        raise NotImplementedError

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

    def run_command(self, args):
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

        self.run_command(args)

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

        self.run_command(args)

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

    def _generate_bindings_pro_file(self, bindings, target_dir):
        """ Generate the .pro file for a set of bindings. """

        project = self.project

        project.progress(
                "Generating the .pro file for the '{0}' bindings".format(
                            bindings.name))

        target_name = bindings.name
        if bindings.metadata.qmake_TARGET:
            target_name = bindings.metadata.qmake_TARGET

        pro_lines = ['TEMPLATE = lib']

        pro_lines.append('CONFIG += warn_on exceptions_off')

        if bindings.static:
            pro_lines.append('CONFIG += staticlib hide_symbols')
        else:
            # Note some version of Qt5 (probably incorrectly) implements
            # 'plugin_bundle' instead of 'plugin' so we specify both.
            pro_lines.append('CONFIG += plugin plugin_bundle')

        pro_lines.append(
                'CONFIG += {}'.format(
                        'debug' if bindings.debug else 'release'))

        if project.qml_debug:
            pro_lines.append('CONFIG += qml_debug')

        # Work around QTBUG-39300.
        pro_lines.append('CONFIG -= android_install')

        # Add any bindings-specific settings.
        pro_lines.extend(bindings.builder_settings)

        # Add any user-supplied settings.
        pro_lines.extend(self.qmake_settings)

        pro_lines.append('TARGET = {}'.format(target_name))

        # Qt (when built with MinGW) assumes that stack frames are 16 byte
        # aligned because it uses SSE.  However the Python Windows installers
        # are built with 4 byte aligned stack frames.  We therefore need to
        # tweak the g++ flags to deal with it.
        if self.spec == 'win32-g++':
            pro_lines.append('QMAKE_CFLAGS += -mstackrealign')
            pro_lines.append('QMAKE_CXXFLAGS += -mstackrealign')

        if not bindings.static:
            debug_suffix = '_d' if project.py_debug else ''

            # Without the 'no_check_exist' magic the target.files must exist
            # when qmake is run otherwise the install and uninstall targets are
            # not generated.
            shared = '''
win32 {
    PY_MODULE = %s%s.pyd
    PY_MODULE_SRC = $(DESTDIR_TARGET)
} else {
    PY_MODULE = %s.so

    macx {
        PY_MODULE_SRC = $(TARGET).plugin/Contents/MacOS/$(TARGET)
        QMAKE_LFLAGS += "-undefined dynamic_lookup"
    } else {
        PY_MODULE_SRC = $(TARGET)
    }
}

QMAKE_POST_LINK = $(COPY_FILE) $$PY_MODULE_SRC $$PY_MODULE

target.CONFIG = no_check_exist
target.files = $$PY_MODULE
''' % (target_name, debug_suffix, target_name)

            pro_lines.extend(shared.split('\n'))

        install_path = target_dir.replace('\\', '/') + '/' + project.name

        pro_lines.append('target.path = {}'.format(install_path))
        pro_lines.append('INSTALLS += target')

        # This optimisation could apply to other platforms.
        if 'linux' in self.spec and not bindings.static:
            exp = project.open_for_writing(
                    os.path.join(bindings.name, target_name + '.exp'))
            exp.write('{ global: PyInit_%s; local: *; };' % target_name)
            exp.close()

            pro_lines.append(
                    'QMAKE_LFLAGS += -Wl,--version-script={}.exp'.format(
                            target_name))

        # Handle any #define macros.
        if bindings.generated.define_macros:
            pro_lines.append('DEFINES += {}'.format(
                    ' '.join(bindings.generated.define_macros)))

        # Handle the include directories.
        for include_dir in bindings.generated.include_dirs:
            pro_lines.append(
                    'INCLUDEPATH += {}'.format(self.qmake_quote(include_dir)))

        pro_lines.append(
                'INCLUDEPATH += {}'.format(
                        self.qmake_quote(project.py_include_dir)))

        # Python.h on Windows seems to embed the need for pythonXY.lib, so tell
        # it where it is.
        # TODO: is this still necessary for Python v3.8?
        if not bindings.static:
            pro_lines.extend(['win32 {',
                    '    LIBS += -L{}'.format(project.py_pylib_dir),
                    '}'])

        # Handle any additional libraries.
        libs = []

        for l_dir in bindings.library_dirs:
            libs.append('-L' + self.qmake_quote(l_dir))

        for l in bindings.libraries:
            libs.append('-l' + l)

        if libs:
            pro_lines.append('LIBS += {}'.format(' '.join(libs)))

        #if src_dir != mname:
            #pro_lines.append('INCLUDEPATH += %s' % qmake_quote(src_dir))
            #pro_lines.append('VPATH = %s' % qmake_quote(src_dir))

        pro_lines.append('HEADERS = {}'.format(
                ' '.join(bindings.generated.headers)))
        pro_lines.append('SOURCES = {}'.format(
                ' '.join(bindings.generated.sources)))

        # Write the .pro file.
        pro_name = os.path.join(bindings.generated.sources_dir,
                bindings.name + '.pro')
        pro = project.open_for_writing(pro_name)
        pro.write('\n'.join(pro_lines))
        pro.write('\n')
        pro.close()

        # Return the directory containing the .pro file relative to the build
        # directory.
        return os.path.relpath(bindings.generated.sources_dir,
                project.build_dir)

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

        # Requiring Qt v5.6 allows us to drop some old workarounds.
        if self.qt_version < 0x050600:
            raise UserException(
                    "Qt v5.6 or later is required and you seem to be using "
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
