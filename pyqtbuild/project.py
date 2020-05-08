# Copyright (c) 2020, Riverbank Computing Limited
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

from sipbuild import Option, Project


# The minimum GLIBC version required by Qt.  Strictly speaking this should
# depend on the Qt version being used.
MINIMUM_GLIBC_VERSION = '2.17'


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

        if self.sip_module is None:
            # TODO: don't hardcode PyQt5 (maybe something based on
            # requires-dist)
            self.sip_module = 'PyQt5.sip'

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

        # Set the default minimum GLIBC version.
        if self.minimum_glibc_version is None:
            self.minimum_glibc_version = MINIMUM_GLIBC_VERSION

        super().apply_nonuser_defaults(tool)

    def apply_user_defaults(self, tool):
        """ Set default values for user options that haven't been set yet. """

        super().apply_user_defaults(tool)

        # Get the details of the default Python interpreter library.  Note that
        # these are actually non-user options but we need the 'link_full_dll'
        # user option in order to set them.
        if self.py_platform == 'win32':
            pylib_dir = os.path.join(sys.base_prefix, 'libs')

            debug_suffix = '_d' if self.py_debug else ''

            # See if we are using the limited API.
            if self.py_debug or self.link_full_dll:
                pylib_lib = 'python{}{}{}'.format(self.py_major_version,
                        self.py_minor_version, debug_suffix)
            else:
                pylib_lib = 'python{}{}'.format(self.py_major_version,
                        debug_suffix)

            # Assume Python is a DLL on Windows.
            pylib_shlib = pylib_lib
        else:
            abi = getattr(sys, 'abiflags', '')
            pylib_lib = 'python{}.{}{}'.format(self.py_major_version,
                    self.py_minor_version, abi)
            pylib_dir = pylib_shlib = ''

            # Use distutils to get the additional configuration.
            from distutils import sysconfig
            from glob import glob

            ducfg = sysconfig.get_config_vars()

            config_args = ducfg.get('CONFIG_ARGS', '')

            dynamic_pylib = '--enable-shared' in config_args
            if not dynamic_pylib:
                dynamic_pylib = '--enable-framework' in config_args

            if dynamic_pylib:
                pylib_shlib = ducfg.get('LDLIBRARY', '')

                exec_prefix = ducfg['exec_prefix']
                multiarch = ducfg.get('MULTIARCH', '')
                libdir = ducfg['LIBDIR']

                if glob('{}/lib/libpython{}.{}*'.format(exec_prefix, self.py_major_version, self.py_minor_version)):
                    pylib_dir = exec_prefix + '/lib'
                elif multiarch != '' and glob('{}/lib/{}/libpython{}.{}*'.format(exec_prefix, multiarch, self.py_major_version, self.py_minor_version)):
                    pylib_dir = exec_prefix + '/lib/' + multiarch
                elif glob('{}/libpython{}.{}*'.format(libdir, self.py_major_version, self.py_minor_version)):
                    pylib_dir = libdir

        # Apply the defaults if necessary.
        if self.py_pylib_dir == '':
            self.py_pylib_dir = pylib_dir

        if self.py_pylib_lib == '':
            self.py_pylib_lib = pylib_lib

        if self.py_pylib_shlib == '':
            self.py_pylib_shlib = pylib_shlib

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

    def update(self, tool):
        """ Re-implemented to carry out any final updates to the confoguration.
        """

        super().update(tool)

        # Set the default minimum macOS version now that we should know the Qt
        # version.  However, don't make any assumptions about the builder used.
        if self.minimum_macos_version == '':
            try:
                qt_version = self.builder.qt_version
            except AttributeError:
                qt_version = 0

            if qt_version >= 0x050e00:
                self.minimum_macos_version = '10.13'
            elif qt_version >= 0x050c00:
                self.minimum_macos_version = '10.12'
            elif qt_version >= 0x050a00:
                self.minimum_macos_version = '10.11'
            elif qt_version >= 0x050900:
                self.minimum_macos_version = '10.10'
            else:
                self.minimum_macos_version = '10.9'
