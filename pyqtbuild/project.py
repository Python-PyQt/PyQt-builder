# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


import os
import sys

from sipbuild import Option, Project, UserException


class PyQtProject(Project):
    """ Encapsulate a PyQt based project. """

    def apply_nonuser_defaults(self, tool):
        """ Set default values for non-user options that haven't been set yet.
        """

        if self.bindings_factory is None:
            from .bindings import PyQtBindings
            self.bindings_factory = PyQtBindings

        if self.builder_factory is None:
            from .builder import QmakeBuilder
            self.builder_factory = QmakeBuilder

        if self.sip_files_dir is None:
            self.sip_files_dir = 'sip'

        # The tag prefix defaults to the meta-data name without any 'Py'
        # prefix.
        if self.tag_prefix is None:
            self.tag_prefix = self.metadata['name']

            if self.tag_prefix.startswith('Py'):
                self.tag_prefix = self.tag_prefix[2:]

        if self.tests_dir is None:
            self.tests_dir = 'config-tests'

        # Make sure relevent paths are absolute and use native separators.
        self.tests_dir = self.tests_dir.replace('/', os.sep)
        if not os.path.isabs(self.tests_dir):
            self.tests_dir = os.path.join(self.root_dir, self.tests_dir)

        super().apply_nonuser_defaults(tool)

    def apply_user_defaults(self, tool):
        """ Set default values for user options that haven't been set yet. """

        super().apply_user_defaults(tool)

        major = self.py_major_version
        minor = self.py_minor_version

        # Get the details of the default Python interpreter library.  Note that
        # these are actually non-user options but we need the 'link_full_dll'
        # user option in order to set them.
        if self.py_platform == 'win32':
            pylib_dir = os.path.join(sys.base_prefix, 'libs')

            debug_suffix = '_d' if self.py_debug else ''

            # See if we are using the limited API.
            if self.py_debug or self.link_full_dll:
                pylib_lib = f'python{major}{minor}{debug_suffix}'
            else:
                pylib_lib = f'python{major}{debug_suffix}'

            # Assume Python is a DLL on Windows.
            pylib_shlib = pylib_lib
        else:
            abi = getattr(sys, 'abiflags', '')

            pylib_lib = f'python{major}.{minor}{abi}'
            pylib_dir = pylib_shlib = ''

            # Get the additional configuration.
            from glob import glob
            from sysconfig import get_config_vars

            ducfg = get_config_vars()

            config_args = ducfg.get('CONFIG_ARGS', '')

            dynamic_pylib = '--enable-shared' in config_args
            if not dynamic_pylib:
                dynamic_pylib = '--enable-framework' in config_args

            if dynamic_pylib:
                exec_prefix = ducfg['exec_prefix']
                multiarch = ducfg.get('MULTIARCH', '')
                libdir = ducfg['LIBDIR']

                pattern = f'libpython{major}.{minor}*'

                if glob(os.path.join(exec_prefix, 'lib', pattern)):
                    pylib_dir = os.path.join(exec_prefix, 'lib')
                elif multiarch != '' and glob(os.path.join(exec_prefix, 'lib', multiarch, pattern)):
                    pylib_dir = os.path.join(exec_prefix, 'lib', multiarch)
                elif glob(os.path.join(libdir, pattern)):
                    pylib_dir = libdir

                if pylib_dir != '':
                    pylib_shlib = os.path.join(pylib_dir, 'lib' + pylib_lib)

        # Apply the defaults if necessary.
        if self.py_pylib_dir == '':
            self.py_pylib_dir = pylib_dir

        if self.py_pylib_lib == '':
            self.py_pylib_lib = pylib_lib

        if self.py_pylib_shlib == '':
            self.py_pylib_shlib = pylib_shlib

    def get_platform_tag(self):
        """ Return the platform tag to use in a wheel name.  This calls the
        default implementation and applied the target Apple build type.
        """

        platform_tag = super().get_platform_tag()

        if sys.platform == 'darwin':
            parts = platform_tag.split('_')

            # We assume the format is 'macosx_major_minor_arch'.
            if len(parts) == 4:
                if self.apple_universal2:
                    arch = 'universal2'
                else:
                    from platform import machine

                    arch = machine()

                    # For arm64 binaries enforce a valid minimum macOS version.
                    if arch == 'arm64':
                        if int(parts[1]) < 11:
                            parts[1] = '11'
                            parts[2] = '0'

                parts[3] = arch
                platform_tag = '_'.join(parts)

        return platform_tag

    def get_options(self):
        """ Return the list of configurable options. """

        options = super().get_options()

        # The directory containing the target Python interpreter library.
        options.append(Option('py_pylib_dir'))

        # The name of the target Python interpreter library.
        options.append(Option('py_pylib_lib'))

        # The name of the target Python interpreter library if it is a shared
        # library.
        options.append(Option('py_pylib_shlib'))

        # The prefix of the version tag to use (with the Qt version
        # automatically appended).  By default the meta-data name is used with
        # any leading 'Py' removed.
        options.append(Option('tag_prefix'))

        # The name of the directory, relative to the project directory,
        # containing any external test programs.
        options.append(Option('tests_dir', default='config-tests'))

        # The user options.
        options.append(
                Option('android_abis', option_type=list,
                        help="the target Android ABI", metavar="ABI"))

        options.append(
                Option('apple_universal2', option_type=bool,
                        help="build a universal2 project"))

        options.append(
                Option('link_full_dll', option_type=bool,
                        help="on Windows link against the full Python DLL "
                                "rather than the limited API DLL"))

        options.append(
                Option('qml_debug', option_type=bool,
                        help="enable the QML debugging infrastructure"))

        options.append(Option('target_qt_dir',
                help="the Qt libraries will be found in DIR when the wheel is "
                        "installed",
                metavar="DIR", tools=['wheel']))

        return options
