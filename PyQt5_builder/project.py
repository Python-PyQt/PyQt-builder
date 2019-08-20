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

from sip5.builder import Option, Project


class PyQt5Project(Project):
    """ Encapsulate a PyQt5 based project. """

    def __init__(self, **kwargs):
        """ Initialise the project. """

        super().__init__(**kwargs)

        # __init__.py should be installed by the PyQt5 package.
        self.dunder_init = False

        # These can be overridden in pyproject.toml but not by the user on the
        # command line.
        self.sip_files_dir = os.path.abspath('sip')
        self.sip_module = 'PyQt5.sip'

    def apply_defaults(self, tool):
        """ Set default values for options that haven't been set yet. """

        # We need some super-class options to be set first.
        super().apply_defaults(tool)

        # Get the details of the default Python interpreter library.
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

    def get_builder(self):
        """ Get the project builder. """

        from .qmake_builder import QmakeBuilder

        return QmakeBuilder(self)

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

        options.append(
                Option('link_full_dll', option_type=bool,
                        help="on Windows link against the full Python DLL "
                                "rather than the limited API DLL"))

        options.append(
                Option('qml_debug', option_type=bool,
                        help="enable the QML debugging infrastructure"))

        return options
