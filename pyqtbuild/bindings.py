# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


import glob
import os
import sys

from sipbuild import Bindings, BuildableExecutable, UserException, Option


class PyQtBindings(Bindings):
    """ A base class for all PyQt-based bindings. """

    def apply_nonuser_defaults(self, tool):
        """ Set default values for non-user options that haven't been set yet.
        """

        project = self.project

        if self.sip_file is None:
            # The (not very good) naming convention used by MetaSIP.
            self.sip_file = os.path.join(self.name, self.name + 'mod.sip')

        super().apply_nonuser_defaults(tool)

        self._update_builder_settings('CONFIG', self.qmake_CONFIG)
        self._update_builder_settings('QT', self.qmake_QT)

        # Add the sources of any support code.
        qpy_dir = os.path.join(project.root_dir, 'qpy', self.name)
        if os.path.isdir(qpy_dir):
            headers = self._matching_files(os.path.join(qpy_dir, '*.h'))
            c_sources = self._matching_files(os.path.join(qpy_dir, '*.c'))
            cpp_sources = self._matching_files(os.path.join(qpy_dir, '*.cpp'))

            sources = c_sources + cpp_sources

            self.headers.extend(headers)
            self.sources.extend(sources)

            if headers or sources:
                self.include_dirs.append(qpy_dir)

    def apply_user_defaults(self, tool):
        """ Set default values for user options that haven't been set yet. """

        # Although tags is not a user option, the default depends on one.
        if len(self.tags) == 0:
            project = self.project

            self.tags = ['{}_{}'.format(project.tag_prefix,
                    project.builder.qt_version_tag)]

        super().apply_user_defaults(tool)

    def get_options(self):
        """ Return the list of configurable options. """

        options = super().get_options()

        # The list of modifications to make to the CONFIG value in a .pro file.
        # An element may start with '-' to specify that the value should be
        # removed.
        options.append(Option('qmake_CONFIG', option_type=list))

        # The list of modifications to make to the QT value in a .pro file.  An
        # element may start with '-' to specify that the value should be
        # removed.
        options.append(Option('qmake_QT', option_type=list))

        # The list of header files to #include in any internal test program.
        options.append(Option('test_headers', option_type=list))

        # The statement to execute in any internal test program.
        options.append(Option('test_statement'))

        return options

    def handle_test_output(self, test_output):
        """ Handle the output of any external test program and return True if
        the bindings are buildable.
        """

        # This default implementation assumes that the output is a list of
        # disabled features.

        if test_output:
            self.project.progress(
                    "Disabled {} bindings features: {}.".format(self.name,
                            ', '.join(test_output)))

            self.disabled_features.extend(test_output)

        return True

    def is_buildable(self):
        """ Return True of the bindings are buildable. """

        project = self.project

        test = 'cfgtest_' + self.name
        test_source = test + '.cpp'

        test_source_path = os.path.join(project.tests_dir, test_source)
        if os.path.isfile(test_source_path):
            # There is an external test program that should be run.
            run_test = True
        elif self.test_statement:
            # There is an internal test program that doesn't need to be run.
            test_source_path = None
            run_test = False
        else:
            # There is no test program so defer to the super-class.
            return super().is_buildable()

        self.project.progress(
                "Checking to see if the {0} bindings can be built".format(
                        self.name))

        # Create a buildable for the test prgram.
        buildable = BuildableExecutable(project, test, self.name)
        buildable.builder_settings.extend(self.builder_settings)
        buildable.debug = self.debug
        buildable.define_macros.extend(self.define_macros)
        buildable.include_dirs.extend(self.include_dirs)
        buildable.libraries.extend(self.libraries)
        buildable.library_dirs.extend(self.library_dirs)

        if test_source_path is None:
            # Save the internal test to a file.
            includes = ['#include <{}>'.format(h) for h in self.test_headers]

            source_text = '''%s

int main(int, char **)
{
    %s;
}
''' % ('\n'.join(includes), self.test_statement)

            test_source_path = os.path.join(buildable.build_dir, test_source)

            tf = project.open_for_writing(test_source_path)
            tf.write(source_text)
            tf.close()

        buildable.sources.append(test_source_path)

        # Build the test program.
        test_exe = project.builder.build_executable(buildable, fatal=False)
        if test_exe is None:
            return False

        # If the test doesn't need to be run then we are done.
        if not run_test:
            return True

        # Run the test and capture the output as a list of lines.
        test_exe = os.path.join(buildable.build_dir, test_exe)

        # Create the output file, first making sure it doesn't exist.  Note
        # that we don't use a pipe because we may want a copy of the output for
        # debugging purposes.
        out_file = os.path.join(buildable.build_dir, test + '.out')

        try:
            os.remove(out_file)
        except OSError:
            pass

        # Make sure the Qt DLLs get picked up.
        original_path = None

        if sys.platform == 'win32':
            qt_bin_dir = os.path.dirname(project.builder.qmake)
            path = os.environ['PATH']
            path_parts = path.split(os.path.pathsep)

            if qt_bin_dir not in path_parts:
                original_path = path

                path_parts.insert(0, qt_bin_dir)
                os.environ['PATH'] = os.pathsep.join(path_parts)

        self.project.run_command([test_exe, out_file], fatal=False)

        if original_path is not None:
            os.environ['PATH'] = original_path

        if not os.path.isfile(out_file):
            raise UserException(
                    "'{0}' didn't create any output".format(test_exe))

        # Read the details.
        with open(out_file) as f:
            test_output = f.read().strip()

        test_output = test_output.split('\n') if test_output else []

        return self.handle_test_output(test_output)

    @staticmethod
    def _matching_files(pattern):
        """ Return a reproducable list of files that match a pattern. """

        return sorted(glob.glob(pattern))

    def _update_builder_settings(self, name, modifications):
        """ Update the builder settings with a list of modifications to a
        value.
        """

        add = []
        remove = []

        for mod in modifications:
            if mod.startswith('-'):
                remove.append(mod[1:])
            else:
                add.append(mod)

        if add:
            self.builder_settings.append(
                    '{} += {}'.format(name, ' '.join(add)))

        if remove:
            self.builder_settings.append(
                    '{} -= {}'.format(name, ' '.join(remove)))
