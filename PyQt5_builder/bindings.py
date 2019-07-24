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

from sip5.builder import Bindings


class PyQt5BindingsMetadata:
    """ This class encapsulates the meta-data about a PyQt5 module. """

    def __init__(self, qmake_QT=None, qmake_TARGET='', qpy_lib=False, cpp11=False, public=True):
        """ Initialise the meta-data. """

        # The values to update qmake's QT variable.
        self.qmake_QT = [] if qmake_QT is None else qmake_QT

        # The value to set qmake's TARGET variable to.  It defaults to the name
        # of the module.
        self.qmake_TARGET = qmake_TARGET

        # Set if there is a qpy support library.
        self.qpy_lib = qpy_lib

        # Set if C++11 support is required.
        self.cpp11 = cpp11

        # Set if the module is public.
        self.public = public


class PyQt5Bindings(Bindings):
    """ A base class for all PyQt5-based bindings. """

    # The bindings meta-data.
    metadata = PyQt5BindingsMetadata()

    def __init__(self, name, project):
        """ Initialise the bindings. """

        # The (not very good) naming convention used by MetaSIP.
        sip_file = os.path.join('sip', name, name + 'mod.sip')

        super().__init__(project, name=name, sip_file=sip_file)

    def compile_test_program(self):
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

        # See if there is the source of a test program in the filesystem.
        test_source_path = os.path.join(project.root_dir, 'config-tests',
                test_source)

        if not os.path.isfile(test_source_path):
            # Get the source from a sub-class.
            test_source_path = os.path.join(project.build_dir, test_source)

            tf = project.open_for_writing(test_source_path)
            tf.write(self.get_test_source_code())
            tf.close()

        # Create the .pro file.
        pro_lines = []
        self._pro_add_qt_dependencies(pro_lines)
        pro_lines.append('TARGET = {}'.format(test))
        pro_lines.append('SOURCES = {}'.format(
                builder.qmake_quote(test_source_path)))

        pf = open_for_writing(name_pro)
        pf.write('\n'.join(pro_lines))
        pf.close()

        if not builder.run_qmake(name_pro, makefile_name=test_makefile, fatal=False):
            return None

        return builder.run_make(test, test_makefile)

    def get_test_source_code(self):
        """ Return the test source code. """

        # We can't use an ABC as it is optional.
        raise NotImplementedError

    def _pro_add_qt_dependencies(self, pro_lines):
        """ Add the Qt dependencies of the bindings to a .pro file. """

        add = []
        remove = []
        for qt in self.metadata.qmake_QT:
            if qt.startswith('-'):
                remove.append(qt[1:])
            else:
                add.append(qt)

        if len(remove) != 0:
            pro_lines.append('QT -= {}'.format(' '.join(remove)))

        if len(add) != 0:
            pro_lines.append('QT += {}'.format(' '.join(add)))

        pro_lines.append(
                'CONFIG += {}'.format('debug' if self.debug else 'release'))

        if self.metadata.cpp11:
            pro_lines.append('CONFIG += c++11')

        pro_lines.extend(self.project.builder.qmake_variables)
