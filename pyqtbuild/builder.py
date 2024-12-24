# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


import os
import sys

from sipbuild import (Buildable, BuildableModule, Builder, Option, Project,
        PyProjectOptionException, UserException)

from .installable import QmakeTargetInstallable
from .version import PYQTBUILD_VERSION_STR


class QmakeBuilder(Builder):
    """ A project builder that uses qmake as the underlying build system. """

    def __init__(self, project, **kwargs):
        """ Initialise the builder. """

        super().__init__(project, **kwargs)

        self.qt_version = 0
        self.qt_version_str = ''
        self.qt_version_tag = ''

        # Assume for the moment that this will be found on PATH.
        self._sip_distinfo = 'sip-distinfo'

    def apply_user_defaults(self, tool):
        """ Set default values for user options that haven't been set yet. """

        if tool in Option.BUILD_TOOLS:
            # A PEP 517 frontend will set PATH so that sip-distinfo is found on
            # it.  However for our own frontends we want to use the version
            # corresponding to the frontend (and, anyway, the frontend may not
            # be on PATH).
            exe_dir, exe_name = os.path.split(sys.argv[0])

            if exe_name.startswith('sip-'):
                self._sip_distinfo = os.path.join(os.path.abspath(exe_dir),
                        self._sip_distinfo)

            # Check we have a qmake.
            if self.qmake is None:
                self.qmake = self._find_exe('qmake')
                if self.qmake is None:
                    raise PyProjectOptionException('qmake',
                            "specify a working qmake or add it to PATH")
            elif not self._is_exe(self.qmake):
                raise PyProjectOptionException('qmake',
                        "'{0}' is not a working qmake".format(self.qmake))

            self.qmake = self._quote(os.path.abspath(self.qmake))

            # Use qmake to get the Qt configuration.
            self._get_qt_configuration()

            # Now apply defaults for any options that depend on the Qt
            # configuration.
            if self.spec is None:
                self.spec = self.qt_configuration['QMAKE_SPEC']

                # The Qt installer used to default to XCode.  If so then use
                # macx-clang.
                if self.spec == 'macx-xcode':
                    # This will exist (and we can't check anyway).
                    self.spec = 'macx-clang'

            # The remaining options influenced by the Qt configuration are
            # project options.
            project = self.project

            # Determine the target platform, ignoring any current value.
            xspec = self.qt_configuration['QMAKE_XSPEC']

            # Note that the order of these tests is important.
            if 'android' in xspec:
                py_platform = 'android'
            elif 'ios' in xspec:
                py_platform = 'ios'
            elif 'macx' in xspec:
                py_platform = 'darwin'
            elif 'wasm' in xspec:
                py_platform = 'wasm'
            elif 'win32' in xspec:
                py_platform = 'win32'
            elif 'mingw-w64' in xspec:
                py_platform = 'win32'
            else:
                # Treat everything else as Linux.
                py_platform = 'linux'

            project.py_platform = py_platform

            # Set the default minimum GLIBC version.  This is actually a
            # function of the build platform and it should really be determined
            # by inspecting the compiled extension module.  These defaults
            # reflect the oldest version used by any of the supported Qt
            # platforms (which may change over time).
            if not project.minimum_glibc_version:
                if self.qt_version >= 0x060000:
                    from platform import processor

                    # The arm64 build is based on Ubuntu 24.04 specifically.
                    if processor() == 'aarch64':
                        project.minimum_glibc_version = '2.39'
                    else:
                        project.minimum_glibc_version = '2.28'
                else:
                    project.minimum_glibc_version = '2.17'

            # Set the default minimum macOS version.
            if not project.minimum_macos_version:
                if self.qt_version >= 0x060000:
                    project.minimum_macos_version = '10.14'
                elif self.qt_version >= 0x050e00:
                    project.minimum_macos_version = '10.13'
                elif self.qt_version >= 0x050c00:
                    project.minimum_macos_version = '10.12'
                elif self.qt_version >= 0x050a00:
                    project.minimum_macos_version = '10.11'
                elif self.qt_version >= 0x050900:
                    project.minimum_macos_version = '10.10'
                else:
                    project.minimum_macos_version = '10.9'

            # Set the default name of the sip module.
            if not project.sip_module:
                project.sip_module = 'PyQt{}.sip'.format(self.qt_version >> 16)

            # Set the default ABI major version of the sip module.  These
            # should track the versions specified by the latest versions of
            # PyQt5 and PyQt6 (and vice versa).  In future this can be removed
            # completely.
            if not project.abi_version:
                if project.sip_module == 'PyQt5.sip':
                    project.abi_version = '12.15'
                elif project.sip_module == 'PyQt6.sip':
                    project.abi_version = '13.8'

        super().apply_user_defaults(tool)

    def build_executable(self, buildable, *, fatal=True):
        """ Build an executable from a BuildableExecutable object and return
        the relative pathname of the executable.
        """

        # The name of the .pro file.
        pro_path = os.path.join(buildable.build_dir, buildable.target + '.pro')

        # Create the .pro file.
        pro_lines = []

        self._update_pro_file(pro_lines, buildable)

        pf = self.project.open_for_writing(pro_path)
        pf.write('\n'.join(pro_lines))
        pf.close()

        saved_cwd = os.getcwd()
        os.chdir(buildable.build_dir)

        if self._run_qmake(pro_path, fatal=fatal):
            exe = self._run_make(buildable.target, buildable.debug,
                    fatal=fatal)
        else:
            exe = None

        os.chdir(saved_cwd)

        return exe

    def build_project(self, target_dir, *, wheel_tag=None):
        """ Build the project. """

        project = self.project

        # Create the .pro file for each set of bindings.
        installed = []
        subdirs = []

        for buildable in project.buildables:
            if isinstance(buildable, BuildableModule):
                self._generate_module_pro_file(buildable, target_dir,
                        installed)
            elif type(buildable) is Buildable:
                for installable in buildable.installables:
                    installable.install(target_dir, installed,
                            do_install=False)
            else:
                raise UserException(
                        "QmakeBuilder cannot build '{0}' buildables".format(
                                type(buildable).__name__))

            subdirs.append(buildable.name)

        # Create the top-level .pro file.
        project.progress("Generating the top-level .pro file")

        pro_lines = []

        pro_lines.append('TEMPLATE = subdirs')
        pro_lines.append('CONFIG += ordered nostrip')
        pro_lines.append('SUBDIRS = {}'.format(' '.join(subdirs)))

        # Add any project-level installables.
        for installable in project.installables:
            self._install(pro_lines, installed, installable, target_dir)

        # Make the .dist-info directory if required.
        if project.distinfo:
            inventory_fn = os.path.join(project.build_dir, 'inventory.txt')
            inventory = project.open_for_writing(inventory_fn)

            for fn in installed:
                print(fn, file=inventory)

            inventory.close()

            args = project.get_sip_distinfo_command_line(self._sip_distinfo,
                    inventory_fn, generator='pyqtbuild',
                    generator_version=PYQTBUILD_VERSION_STR,
                    wheel_tag=wheel_tag)
            args.append(self.qmake_quote(project.get_distinfo_dir(target_dir)))

            pro_lines.append('distinfo.depends = install_subtargets {}'.format(
                    ' '.join(
                            ['install_' + installable.name
                                    for installable in project.installables])))
            pro_lines.append('distinfo.extra = {}'.format(' '.join(args)))
            pro_lines.append(
                    'distinfo.path = {}'.format(self.qmake_quote(target_dir)))
            pro_lines.append('INSTALLS += distinfo')

        pro_name = os.path.join(project.build_dir, project.name + '.pro')
        self._write_pro_file(pro_name, pro_lines)

        # Run qmake to generate the Makefiles.
        project.progress("Generating the Makefiles")

        saved_cwd = os.getcwd()
        os.chdir(project.build_dir)

        self._run_qmake(pro_name, recursive=True)

        # Run make, if requested, to generate the bindings.
        if self.make:
            project.progress("Compiling the project")
            self._run_project_make()

        os.chdir(saved_cwd)

        return None

    def get_options(self):
        """ Return the sequence of configurable options. """

        # Get the standard options.
        options = super().get_options()

        # Add our new options.
        options.append(
                Option('jobs', option_type=int,
                        help="run N make jobs in parallel", metavar='N'))

        options.append(
                Option('make', option_type=bool, inverted=True,
                        help="do not run make or nmake", tools=['build']))

        options.append(
                Option('qmake', help="the pathname of qmake is FILE",
                        metavar="FILE"))

        options.append(
                Option('qmake_settings', option_type=list,
                        help="add the 'NAME += VALUE' setting to any .pro file",
                        metavar="'NAME += VALUE'"))

        options.append(
                Option('spec', help="pass -spec SPEC to qmake",
                        metavar="SPEC"))

        return options

    def install_project(self, target_dir, *, wheel_tag=None):
        """ Install the project into a target directory. """

        project = self.project

        project.progress("Installing the project")

        saved_cwd = os.getcwd()
        os.chdir(project.build_dir)
        self._run_project_make(install=True)
        os.chdir(saved_cwd)

    @staticmethod
    def qmake_quote(path):
        """ Return a path quoted for qmake if it contains spaces. """

        # Also convert to Unix path separators.
        path = path.replace('\\', '/')

        if ' ' in path:
            path = '$$quote({})'.format(path)

        return path

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

    def _find_make(self):
        """ Return the name of a valid make program. """

        if self.project.py_platform == 'win32':
            if 'g++' in self.spec:
                make = 'make'
            else:
                make = 'nmake'
        else:
            make = 'make'

        if self._find_exe(make) is None:
            raise UserException(
                    "'{0}' could not be found on PATH".format(make))

        return make

    def _generate_module_pro_file(self, buildable, target_dir, installed):
        """ Generate the .pro file for an extension module.  The list of
        installed files is updated.
        """

        project = self.project

        project.progress(
                "Generating the .pro file for the {0} module".format(
                            buildable.target))

        pro_lines = ['TEMPLATE = lib']

        pro_lines.append('CONFIG += warn_on')

        if buildable.exceptions:
            pro_lines.append('CONFIG += exceptions')
        else:
            pro_lines.append('CONFIG += exceptions_off')

        if buildable.static:
            pro_lines.append('CONFIG += staticlib hide_symbols')
        else:
            # Note some version of Qt5 (probably incorrectly) implements
            # 'plugin_bundle' instead of 'plugin' so we specify both.
            pro_lines.append('CONFIG += plugin plugin_bundle no_default_rpath')

        if project.qml_debug:
            pro_lines.append('CONFIG += qml_debug')

        # Work around QTBUG-39300.
        pro_lines.append('CONFIG -= android_install')

        if project.android_abis:
            pro_lines.append(
                    'ANDROID_ABIS = "{}"'.format(
                            ' '.join(project.android_abis)))

        self._update_pro_file(pro_lines, buildable)

        # Qt (when built with MinGW) assumes that stack frames are 16 byte
        # aligned because it uses SSE.  However the Python Windows installers
        # are built with 4 byte aligned stack frames.  We therefore need to
        # tweak the g++ flags to deal with it.
        if self.spec == 'win32-g++':
            pro_lines.append('QMAKE_CFLAGS += -mstackrealign')
            pro_lines.append('QMAKE_CXXFLAGS += -mstackrealign')

        # Get the name of the extension module file.
        module = buildable.target

        if project.py_platform == 'win32' and project.py_debug:
            module += '_d'

        module += buildable.get_module_extension()

        if not buildable.static:
            # Without the 'no_check_exist' magic the target.files must exist
            # when qmake is run otherwise the install and uninstall targets are
            # not generated.
            shared = '''
win32 {
    PY_MODULE_SRC = $(DESTDIR_TARGET)
} else {
    macx {
        PY_MODULE_SRC = $(TARGET).plugin/Contents/MacOS/$(TARGET)
        QMAKE_LFLAGS += "-undefined dynamic_lookup"
    } else {
        PY_MODULE_SRC = $(TARGET)
    }
}

QMAKE_POST_LINK = $(COPY_FILE) $$PY_MODULE_SRC %s

target.CONFIG = no_check_exist
target.files = %s
''' % (module, module)

            pro_lines.extend(shared.split('\n'))

        buildable.installables.append(
                QmakeTargetInstallable(module, buildable.get_install_subdir()))

        # Handle an explicit Qt target directory.
        if project.target_qt_dir:
            rpath = '''
CONFIG += no_qt_rpath
linux {
    QMAKE_RPATHDIR = %s
}
macx {
    QMAKE_RPATHDIR = @loader_path/%s
}
''' % (project.target_qt_dir, project.target_qt_dir)

            pro_lines.extend(rpath.split('\n'))

        # This optimisation could apply to other platforms.
        if 'linux' in self.spec and not buildable.static:
            exp = project.open_for_writing(
                    os.path.join(buildable.build_dir,
                            buildable.target + '.exp'))
            exp.write('{ global: PyInit_%s; local: *; };' % buildable.target)
            exp.close()

            pro_lines.append(
                    'QMAKE_LFLAGS += -Wl,--version-script={}.exp'.format(
                            buildable.target))

        pro_lines.append(
                'INCLUDEPATH += {}'.format(
                        self.qmake_quote(project.py_include_dir)))

        # Python.h on Windows seems to embed the need for pythonXY.lib, so tell
        # it where it is.
        # TODO: is this still necessary for Python v3.8?
        if not buildable.static:
            pro_lines.extend(['win32 {',
                    '    LIBS += -L{}'.format(
                            self.qmake_quote(project.py_pylib_dir)),
                    '}'])

        # Add any installables from the buildable.
        for installable in buildable.installables:
            self._install(pro_lines, installed, installable, target_dir)

        # Write the .pro file.
        self._write_pro_file(
                os.path.join(buildable.build_dir, buildable.name + '.pro'),
                pro_lines)

    def _get_qt_configuration(self):
        """ Run qmake to get the details of the Qt configuration. """

        project = self.project

        project.progress("Querying qmake about your Qt installation")

        self.qt_configuration = {}

        for line in project.read_command_pipe([self.qmake, '-query']):
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

            self.qt_configuration[name] = value

        # Get the Qt version.
        self.qt_version = 0
        try:
            self.qt_version_str = self.qt_configuration['QT_VERSION']
            for v in self.qt_version_str.split('.'):
                self.qt_version <<= 8
                self.qt_version += int(v)
        except AttributeError:
            self.qt_version_str = "3"

        # Requiring Qt v5.6 allows us to drop some old workarounds.
        if self.qt_version < 0x050600:
            raise UserException(
                    "Qt v5.6 or later is required and you seem to be using "
                            "v{0}".format(self.qt_version_str))

        # Convert the version number to what would be used in a tag.
        major = (self.qt_version >> 16) & 0xff
        minor = (self.qt_version >> 8) & 0xff
        patch = self.qt_version & 0xff

        # Qt v5.12.4 was the last release where we updated for a patch version.
        # This should be safe to do (given Qt's supposed use of semantic
        # versioning) and removes the need to add new patch versions for old
        # (ie. LTS) versions.  However Qt v5.15 breaks semantic versioning so
        # we need the patch version, but as it is the very last minor version
        # of Qt5 we don't need to worry about old versions.
        if (5, 13) <= (major, minor) < (5, 15) or major >= 6:
            patch = 0
        elif (5, 12, 4) <= (major, minor, patch) < (5, 13, 0):
            patch = 4

        self.qt_version_tag = '{}_{}_{}'.format(major, minor, patch)

    def _install(self, pro_lines, installed, installable, target_dir):
        """ Add the lines to install files to a .pro file and a list of all
        installed files.
        """

        installable.install(target_dir, installed, do_install=False)

        pro_lines.append(
                '{}.path = {}'.format(installable.name,
                        installable.get_full_target_dir(target_dir).replace(
                                '\\', '/')))

        if not isinstance(installable, QmakeTargetInstallable):
            files = [fn.replace('\\', '/') for fn in installable.files]
            pro_lines.append(
                    '{}.files = {}'.format(installable.name, ' '.join(files)))

        pro_lines.append('INSTALLS += {}'.format(installable.name))

    @staticmethod
    def _is_exe(exe_path):
        """ Return True if an executable exists. """

        return os.access(exe_path, os.X_OK)

    @staticmethod
    def _quote(path):
        """ Return a path with quotes added if it contains spaces. """

        if ' ' in path:
            path = '"{}"'.format(path)

        return path

    @staticmethod
    def _remove_file(fname):
        """ Remove a file which may or may not exist. """

        try:
            os.remove(fname)
        except OSError:
            pass

    def _run_make(self, exe, debug, fatal=True):
        """ Run make against a Makefile to create an executable.  Returns the
        platform specific name of the executable, or None if an executable
        wasn't created.
        """

        project = self.project

        # Guess the name of make and set the default target and platform
        # specific name of the executable.
        if project.py_platform == 'win32':
            if debug:
                makefile_target = 'debug'
                platform_exe = os.path.join('debug', exe + '.exe')
            else:
                makefile_target = 'release'
                platform_exe = os.path.join('release', exe + '.exe')
        else:
            makefile_target = None

            if project.py_platform == 'darwin':
                platform_exe = os.path.join(exe + '.app', 'Contents', 'MacOS',
                        exe)
            else:
                platform_exe = os.path.join('.', exe)

        # Make sure the executable doesn't exist.
        self._remove_file(platform_exe)

        args = [self._find_make()]

        if makefile_target is not None:
            args.append(makefile_target)

        project.run_command(args, fatal=fatal)

        return platform_exe if os.path.isfile(platform_exe) else None

    def _run_project_make(self, install=False):
        """ Run make on the project.  The Makefile must be in the current
        directory.
        """

        project = self.project

        args = [self._find_make()]

        if install:
            args.append('install')
        elif project.py_platform != 'win32' and self.jobs:
            args.append('-j')
            args.append(str(self.jobs))

        project.run_command(args)

    def _run_qmake(self, pro_name, fatal=True, recursive=False):
        """ Run qmake against a .pro file.  fatal is set if a qmake failure is
        considered a fatal error, otherwise False is returned if qmake fails.
        The current directory must contain the .pro file.
        """

        # Make sure the Makefile doesn't exist.
        mf_name = 'Makefile'
        self._remove_file(mf_name)

        # Build the command line.
        args = [self.qmake]

        # If the spec is the same as the default then we don't need to specify
        # it.
        if self.spec != self.qt_configuration['QMAKE_SPEC']:
            args.append('-spec')
            args.append(self.spec)

        if recursive:
            args.append('-recursive')

        args.append(os.path.basename(pro_name))

        self.project.run_command(args, fatal=fatal)

        # Check that the Makefile was created.
        if os.path.isfile(mf_name):
            return True

        if fatal:
            raise UserException(
                    "{0} failed to create a makefile from {1}".format(
                            self.qmake, pro_name))

        return False

    def _update_pro_file(self, pro_lines, buildable):
        """ Update a .pro file from a buildable. """

        buildable.make_names_relative()

        if sys.platform == 'darwin' and self.project.apple_universal2:
            pro_lines.append('QMAKE_APPLE_DEVICE_ARCHS = x86_64 arm64')

        # Handle debugging.
        pro_lines.append(
                'CONFIG += {}'.format(
                        'debug' if buildable.debug else 'release'))

        # Add any buildable-specific settings.
        pro_lines.extend(buildable.builder_settings)

        # Add any user-supplied settings.
        pro_lines.extend(self.qmake_settings)

        # Add the target.
        pro_lines.append('TARGET = {}'.format(buildable.target))

        # Handle any #define macros.
        if buildable.define_macros:
            pro_lines.append('DEFINES += {}'.format(
                    ' '.join(buildable.define_macros)))

        # Handle the include directories.
        for include_dir in buildable.include_dirs:
            pro_lines.append(
                    'INCLUDEPATH += {}'.format(self.qmake_quote(include_dir)))

        # Handle any additional libraries.
        libs = []

        for l_dir in buildable.library_dirs:
            libs.append('-L' + self.qmake_quote(l_dir))

        for l in buildable.libraries:
            libs.append('-l' + l)

        if libs:
            pro_lines.append('LIBS += {}'.format(' '.join(libs)))

        headers = [self.qmake_quote(f) for f in buildable.headers]
        pro_lines.append('HEADERS = {}'.format(' '.join(headers)))

        sources = [self.qmake_quote(f) for f in buildable.sources]
        pro_lines.append('SOURCES = {}'.format(' '.join(sources)))

        # Add any extras.
        if buildable.extra_compile_args:
            pro_lines.append(
                    'QMAKE_CXXFLAGS += {}'.format(
                            ' '.join(buildable.extra_compile_args)))

        if buildable.extra_link_args:
            pro_lines.append(
                    'QMAKE_LFLAGS += {}'.format(
                            ' '.join(buildable.extra_link_args)))

        if buildable.extra_objects:
            objects = [self.qmake_quote(f) for f in buildable.objects]
            pro_lines.append('OBJECTS += {}'.format(' '.join(objects)))

    def _write_pro_file(self, pro_fn, pro_lines):
        """ Write a .pro file. """

        pro = self.project.open_for_writing(pro_fn)
        pro.write('\n'.join(pro_lines))
        pro.write('\n')
        pro.close()
