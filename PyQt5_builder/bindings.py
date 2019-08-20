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


import glob
import os

from sip5.builder import Bindings, UserException


class PyQt5BindingsMetadata:
    """ This class encapsulates the meta-data about a PyQt5 module. """

    def __init__(self, qmake_QT=None, qpy_lib=False, cpp11=False, internal=False):
        """ Initialise the meta-data. """

        # The values to update qmake's QT variable.
        self.qmake_QT = [] if qmake_QT is None else qmake_QT

        # Set if there is a qpy support library.
        self.qpy_lib = qpy_lib

        # Set if C++11 support is required.
        self.cpp11 = cpp11

        # Set if the module is internal.
        self.internal = internal


class PyQt5Bindings(Bindings):
    """ A base class for all PyQt5-based bindings. """

    # The bindings meta-data.
    metadata = PyQt5BindingsMetadata()

    def __init__(self, name, project):
        """ Initialise the bindings. """

        # The (not very good) naming convention used by MetaSIP.
        sip_file = os.path.join(name, name + 'mod.sip')

        # Make sure any unknown Qt version gets treated as the latest Qt v5.
        backstops = ['Qt_6_0_0']

        # Set the builder-specific settings.
        builder_settings = []

        if self.metadata.cpp11:
            builder_settings.append('CONFIG += c++11')

        add = []
        remove = []

        for qt in self.metadata.qmake_QT:
            if qt.startswith('-'):
                remove.append(qt[1:])
            else:
                add.append(qt)

        if add:
            builder_settings.append('QT += {}'.format(' '.join(add)))

        if remove:
            builder_settings.append('QT -= {}'.format(' '.join(remove)))

        # Get the sources of any support code.
        if self.metadata.qpy_lib:
            qpy_dir = os.path.join(project.root_dir, 'qpy', name)

            include_dirs = [qpy_dir]
            headers = self._matching_files(os.path.join(qpy_dir, '*.h'))
            c_sources = self._matching_files(os.path.join(qpy_dir, '*.c'))
            cpp_sources = self._matching_files(os.path.join(qpy_dir, '*.cpp'))

            sources = c_sources + cpp_sources
        else:
            headers = include_dirs = sources = []

        super().__init__(project, name=name, sip_file=sip_file,
                internal=self.metadata.internal, backstops=backstops,
                builder_settings=builder_settings, headers=headers,
                include_dirs=include_dirs, sources=sources)

    def get_test_source_code(self):
        """ Return the test source code.  If None is returned then there must
        be a file containing the test source code which must also be executed.
        """

        return None

    def handle_test_output(self, test_output):
        """ Handle the output of any external test program and return True if
        the bindings are buildable.
        """

        # We can't use an ABC because this is optional.
        raise NotImplementedError

    def is_buildable(self):
        """ Return True of the bindings are buildable. """

        test_exe = self._compile_test_program()
        if test_exe is None:
            return False

        # If there was no external test program then the bindings are
        # buildable.
        if self.get_test_source_code() is not None:
            return True

        # Run the external test program.
        test_output = self._run_test_program(test_exe)

        return self.handle_test_output(test_output)

    def _compile_test_program(self):
        """ Compile the bindings's test program and return the name of the
        resulting executable or None if the compilation failed.
        """

        project = self.project
        builder = project.builder

        # The derived file names.
        test = 'cfgtest_' + self.name
        test_pro = test + '.pro'
        test_makefile = test + '.mk'
        test_source = test + '.cpp'

        # See if there is an external test program.
        test_source_code = self.get_test_source_code()
        if test_source_code is None:
            test_source_path = os.path.join(project.root_dir, 'config-tests',
                    test_source)
        else:
            test_source_path = os.path.join(project.build_dir, test_source)

            tf = project.open_for_writing(test_source_path)
            tf.write(test_source_code)
            tf.close()

        # Create the .pro file.
        pro_lines = []

        pro_lines.append(
                'CONFIG += {}'.format('debug' if self.debug else 'release'))

        pro_lines.extend(self.builder_settings)
        pro_lines.extend(builder.qmake_settings)
        pro_lines.append('TARGET = {}'.format(test))
        pro_lines.append('SOURCES = {}'.format(
                builder.qmake_quote(test_source_path)))

        pf = project.open_for_writing(test_pro)
        pf.write('\n'.join(pro_lines))
        pf.close()

        if not builder.run_qmake(test_pro, makefile_name=test_makefile, fatal=False):
            return None

        return builder.run_make(test, test_makefile, self.debug)

    @staticmethod
    def _matching_files(pattern):
        """ Return a reproducable list of files that match a pattern. """

        return sorted(glob.glob(pattern))

    def _run_test_program(self, test_exe):
        """ Run a test program and return the output as a list of lines. """

        out_file = 'cfgtest_' + self.name + '.out'

        # Create the output file, first making sure it doesn't exist.  Note
        # that we don't use a pipe because we may want a copy of the output for
        # debugging purposes.
        try:
            os.remove(out_file)
        except OSError:
            pass

        self.project.builder.run_command([test_exe, out_file])

        if not os.path.isfile(out_file):
            raise UserException(
                    "'{0}' didn't create any output".format(test_exe))

        # Read the details.
        with open(out_file) as f:
            test_output = f.read().split('\n')

        return test_output
