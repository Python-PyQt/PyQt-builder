# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from dataclasses import dataclass
from enum import auto, Enum
from typing import Any, List, Optional, Tuple

from sipbuild import BuildSystemExtension


class PyQtBuildSystemExtension(BuildSystemExtension):
    """ This class implements the PyQt builder extension. """

    def argument_parse_annotation(self, argument, name, raw_value, location):
        """ Parse an argument annotation.  Return True if it was parsed. """

        if name == 'ScopesStripped':
            scopes_stripped = self.parse_integer_annotation(name, raw_value,
                    location)

            if scopes_stripped <= 0:
                self.parsing_error("/ScopesStripped/ must be greater than 0",
                        location)
            else:
                extension = self.get_extension_data(argument,
                        _ArgumentExtension)
                extension.scopes_stripped = scopes_stripped

            return True

        return False

    def class_complete_definition(self, klass):
        """ Complete the definition of a class. """

        module = f'PyQt{self._pyqt_major_version}.QtCore'

        if self.query_class_is_subclass(klass, module, 'QObject'):
            extension = self.get_extension_data(klass, _ClassExtension)
            extension.is_qobject = True

    def class_get_access_specifier_keywords(self):
        """ Return a sequence of class action specifier keywords to be
        recognised by the parser.
        """

        return ('signals', 'Q_SIGNALS', 'slots', 'Q_SLOTS')

    def class_parse_access_specifier(self, klass, primary, secondary):
        """ Parse a primary and optional secondary class access specifier.  If
        it was parsed return the C++ standard access specifier (ie. 'public',
        'protected' or 'private') to use, otherwise return None.
        """

        if primary in ('public', 'protected', 'private'):
            if secondary is not None and secondary not in ('slots', 'Q_SLOTS'):
                return None

            is_signal = False

        elif primary in ('signals', 'Q_SIGNALS'):
            if secondary is not None:
                return None

            is_signal = True
            primary = 'public'

        extension = self.get_extension_data(klass, _ClassExtension)
        extension.functions_are_signals = is_signal

        return primary

    def class_parse_annotation(self, klass, name, raw_value, location):
        """ Parse a class annotation.  Return True if it was parsed. """

        if self._pyqt_major_version == 5:
            if name == 'PyQtFlag':
                extension = self.get_extension_data(klass, _ClassExtension)
                extension.flags = self.parse_integer_annotation(name,
                        raw_value, location)
                return True

            if name == 'PyQtFlagsEnums':
                extension = self.get_extension_data(klass, _ClassExtension)
                extension.flags_enums = self.parse_string_list_annotation(name,
                        raw_value, location)
                extension.flags |= 1
                return True

        if name == 'PyQtInterface':
            extension = self.get_extension_data(klass, _ClassExtension)
            extension.interface = self.parse_string_annotation(name, raw_value,
                    location)
            return True

        if name == 'PyQtNoQMetaObject':
            extension = self.get_extension_data(klass, _ClassExtension)
            extension.no_qmetaobject = self.parse_boolean_annotation(name,
                    raw_value, location)
            return True

        return False

    def class_write_extension_structure(self, klass, output, structure_name):
        """ Write the code that implements a class extension data structure.
        Return True if something was written.
        """

        extension = self.get_extension_data(klass)
        if extension is None:
            return False

        pyqt_major = self._pyqt_major_version

        if extension.signal_data is not None:
            qt_signals = self._pyqt_class_write_signals_table(output, klass,
                    extension, pyqt_major)
        else:
            qt_signals = 'SIP_NULLPTR'

        output.write(f'\nstatic pyqt{pyqt_major}ClassExtensionDef {structure_name} = {{\n')

        if pyqt_major == 5:
            output.write(f'    {extension.flags},\n')

        if extension.is_qobject and not extension.no_qmetaobject:
            fq_cpp_name = self.get_class_fq_cpp_name(klass)
            static_metaobject = f'&{fq_cpp_name}::staticMetaObject'
        else:
            static_metaobject = 'SIP_NULLPTR'

        output.write(f'    {static_metaobject},\n')

        output.write(f'    {qt_signals},\n')

        qt_interface = f'"{extension.interface}"' if extension.interface is not None else 'SIP_NULLPTR'
        output.write(f'    {qt_interface},\n')

        output.write('};\n')

        return True

    def function_complete_parse(self, function, scope):
        """ Complete the parsing of a function. """

        if self.query_scope_is_class(scope):
            # Ignore if we are not in a signal section.
            class_extension = self.get_extension_data(scope)
            if class_extension is not None and class_extension.functions_are_signals:
                extension = self.get_extension_data(function, _FunctionExtension)
                extension.is_signal = True

                # Signals have an implied /ReleaseGIL/.
                self.set_function_release_gil(function)

    def function_get_keywords(self):
        """ Return a sequence of function keywords to be recognised by the
        parser.
        """

        return ('Q_SIGNAL', 'Q_SLOT')

    def function_parse_keyword(self, function, keyword):
        """ Parse a function keyword.  Return True if it was parsed. """

        if keyword == 'Q_SIGNAL':
            extension = self.get_extension_data(function, _FunctionExtension)
            extension.is_signal = True
            return True

        if keyword == 'Q_SLOT':
            return True

        return False

    def function_group_complete_definition(self, function_group, scope):
        """ Update a function group after it has been defined. """

        if not self.query_scope_is_class(scope):
            return

        # Get the signals.
        signal_group = []
        has_non_signals = False

        for function in function_group:
            function_extension = self.get_extension_data(function)
            if function_extension is not None and function_extension.is_signal:
                signal_group.append(function)
            else:
                has_non_signals = True

        if signal_group:
            extension = self.get_extension_data(scope, _ClassExtension)

            if extension.signal_data is None:
                extension.signal_data = []

            extension.signal_data.append((signal_group, has_non_signals))

            # Remove the signals from the original list:
            for signal in signal_group:
                function_group.remove(signal)

    def mapped_type_parse_annotation(self, mapped_type, name, raw_value,
            location):
        """ Parse a mapped type annotation.  Return True if it was parsed. """

        if self._pyqt_major_version == 6:
            if name == 'PyQtFlag':
                extension = self.get_extension_data(mapped_type,
                        _MappedTypeExtension)
                extension.flags = self.parse_integer_annotation(name,
                        raw_value, location)
                return True

        return False

    def mapped_type_write_extension_structure(self, mapped_type, output,
            structure_name):
        """ Write the code that implements a mapped type extension data
        structure.  Return True if something was written.
        """

        # This will only ever be called for PyQt6.

        extension = self.get_extension_data(mapped_type)
        if extension is None:
            return False

        output.write(f'\nstatic pyqt6MappedTypeExtensionDef {structure_name} = {{{extension.flags}}};\n')

        return True

    def namespace_parse_annotation(self, namespace, name, raw_value, location):
        """ Parse a namespace annotation.  Return True if it was parsed. """

        if name == 'PyQtNoQMetaObject':
            extension = self.get_extension_data(namespace,
                    _NamespaceExtension)
            extension.no_qmetaobject = self.parse_boolean_annotation(name,
                    raw_value, location)
            return True

        return False

    def write_sip_api_h_code(self, output):
        """ Write code to be included in all generated sipAPI*.h files. """

        output.write(
                _PYQT6_SIP_API_H_CODE if self._pyqt_major_version == 6 else _PYQT5_SIP_API_H_CODE)

    @property
    def _pyqt_major_version(self):
        """ The PyQt (and Qt) major version number. """

        return self.bindings.project.builder.qt_version >> 16

    def _pyqt_class_write_signals_table(self, output, klass, extension,
            pyqt_major):
        """ Write the code to generate the signals table for a class.  Return a
        C++ reference to the table.
        """

        # The prefix to make sure our generated code doesn't conflict with the
        # standard generated code.
        prefix = 'pyqt_signals_'

        # An emitter helper is generated for any signal overload with an
        # optional argument or %MethodCode.
        emitter_helpers = []

        # There is a docstring for each signal group.
        docstrings = []

        for signal_group, _ in extension.signal_data:
            for signal in signal_group:
                if self.query_function_has_method_code(signal):
                    need_emitter_helper = True
                else:
                    for arg in self.get_function_cpp_arguments(signal):
                        if self.query_argument_is_optional(arg):
                            need_emitter_helper = True
                            break
                    else:
                        need_emitter_helper = False

                if need_emitter_helper:
                    call_ref = self.write_function_group_bindings(signal_group,
                            klass, output, prefix=prefix)
                else:
                    call_ref = 'SIP_NULLPTR'

                emitter_helpers.append(call_ref)

            docstrings.append(
                    self.write_function_group_docstring(signal_group, klass,
                            output, prefix=prefix))

        table_name = prefix + self.get_class_fq_cpp_name(klass).replace(
                '::', '_')

        output.write(f'\nstatic const pyqt{pyqt_major}QtSignalDef {table_name}[] = {{\n')

        signal_group_nr = 0
        signal_nr = 0

        for signal_group, has_non_signals in extension.signal_data:
            docstring_ref, auto_docstring = docstrings[signal_group_nr]

            if has_non_signals:
                non_signal_pymethoddef = self.get_function_group_bindings(
                        signal_group, klass)
            else:
                non_signal_pymethoddef = 'SIP_NULLPTR'

            for signal in signal_group:
                self._pyqt_write_signal_table_entry(output, signal, klass,
                        docstring_ref, auto_docstring, non_signal_pymethoddef,
                        emitter_helpers[signal_nr])

                # These are only set for the first (ie. default) overload.
                docstring_ref = non_signal_pymethoddef = 'SIP_NULLPTR'
                auto_docstring = 0

                signal_nr += 1

            signal_group_nr += 1

        output.write('    {SIP_NULLPTR, SIP_NULLPTR, 0, SIP_NULLPTR, SIP_NULLPTR}\n};\n')

        return '&' + table_name

    def _pyqt_write_signal_table_entry(self, output, signal, klass,
            docstring_ref, auto_docstring, pymethoddef, emitter_helper):
        """ Write the code for a single signal in the signal table. """

        # Build the normalised signature.
        need_unstripped = False

        stripped = []

        for arg in self.get_function_cpp_arguments(signal):
            # See if /ScopesStripped/ was specified for the argument.
            extension = self.get_extension_data(arg)
            if extension is not None:
                need_unstripped = True
                strip = extension.scopes_stripped
            else:
                strip = -1

            arg_decl = self.get_argument_cpp_decl(arg, klass, strip=strip)

            # Do some signal argument normalisation so that Qt doesn't have to.
            # Note that this is too simplistic in the (highly unlikely) event
            # that the argument is a function pointer.
            if arg_decl.startswith('const ') and (arg_decl.endswith('&') or '*' not in arg_decl):
                arg_decl = arg_decl[6:]

                if arg_decl.endswith('&'):
                    arg_decl = arg_decl[:-1]

            stripped.append(arg_decl)

        stripped_args = ','.join(stripped)

        if need_unstripped:
            unstripped = []

            for arg in self.get_function_cpp_arguments(signal):
                unstripped.append(
                        self.get_argument_cpp_decl(arg, klass, strip=-1))

            unstripped_args = '|(' + ','.join(unstripped) + ')'
        else:
            unstripped_args = ''

        signal_name = self.get_function_cpp_name(signal)

        output.write(f'    {{"{signal_name}({stripped_args}){unstripped_args}", {docstring_ref}, {int(auto_docstring)}, {pymethoddef}, {emitter_helper}}},\n')


@dataclass
class _ArgumentExtension:
    """ The additional data held for an argument. """

    # The value of /ScopesStripped/.
    scopes_stripped: int = 0


@dataclass
class _ClassExtension:
    """ The additional data held for a class. """

    # True if functions are currently signals.
    functions_are_signals: bool = False

    # Non-zero if /PyQtFlags/ was specified.  Also implied if /PyQtFlagsEnums/
    # was specified.  PyQt5 only.
    flags: int = 0

    # The list of enum names from /PyQtFlagsEnums/.  Apart from automatically
    # setting /PyQtFlags/ it is only used by the documentation system.
    # PyQt5 only.
    flags_enums: Optional[List[str]] = None

    # The interface name specified by /PyQtInterface/.
    interface: Optional[str] = None

    # Set if the class is QObject or a sub-class.
    is_qobject: bool = False

    # Set if /PyQtNoQMetaObject/ was specified.
    no_qmetaobject: bool = False

    # The signal data.  Each value is a 2-tuple of the signal group and a bool
    # that is set if there were non-signal overloads.
    signal_data: Optional[List[Tuple[Any, bool]]] = None


@dataclass
class _FunctionExtension:
    """ The additional data held for a function. """

    # True if the function is a signal.
    is_signal: bool = False


@dataclass
class _MappedTypeExtension:
    """ The additional data held for a mapped type. """

    # Non-zero if /PyQtFlags/ was specified.  PyQt6 only.
    flags: int = 0


@dataclass
class _NamespaceExtension:
    """ The additional data held for a namespace. """

    # Set if /PyQtNoQMetaObject/ was specified.
    no_qmetaobject: bool = False


# The code to include in sipAPI*.h for PyQt6.
_PYQT6_SIP_API_H_CODE = '''
/*
 * The description of a Qt signal for PyQt6.
 */
typedef int (*pyqt6EmitFn)(void *, PyObject *);

typedef struct _pyqt6QtSignalDef {
    /* The normalised C++ name and signature of the signal. */
    const char *signature;

    /* The optional docstring. */
    const char *docstring;

    /*
     * Set if the docstring is automatically generated (ie. has a known
     * format).
     */
    int auto_docstring;

    /*
     * If the signal is an overload of regular methods then this points to the
     * code that implements those methods.
     */
    PyMethodDef *non_signals;

    /*
     * If the signal has optional arguments then this function will implement
     * emit() for the signal.
     */
    pyqt6EmitFn emitter;
} pyqt6QtSignalDef;


/*
 * This is the PyQt6-specific extension to the generated class type structure.
 */
typedef struct _pyqt6ClassExtensionDef {
    /* A pointer to the QObject sub-class's staticMetaObject class variable. */
    const void *static_metaobject;

    /*
     * The table of signals emitted by the type.  These are grouped by signal
     * name.
     */
    const pyqt6QtSignal *qt_signals;

    /* The name of the interface that the class defines. */
    const char *qt_interface;
} pyqt6ClassExtensionDef;


/*
 * This is the PyQt6-specific extension to the generated mapped type structure.
 */
typedef struct _pyqt6MappedTypeExtensionDef {
    /*
     * A set of flags.  At the moment only bit 0 is used to say if the type is
     * mapped to/from QFlags.
     */
    unsigned flags;
} pyqt6MappedTypeExtensionDef;
'''


# The code to include in sipAPI*.h for PyQt5.
_PYQT5_SIP_API_H_CODE = '''
/*
 * The description of a Qt signal for PyQt5.
 */
typedef int (*pyqt5EmitFn)(void *, PyObject *);

typedef struct _pyqt5QtSignalDef {
    /* The normalised C++ name and signature of the signal. */
    const char *signature;

    /* The optional docstring. */
    const char *docstring;

    /*
     * Set if the docstring is automatically generated (ie. has a known
     * format).
     */
    int auto_docstring;

    /*
     * If the signal is an overload of regular methods then this points to the
     * code that implements those methods.
     */
    PyMethodDef *non_signals;

    /*
     * If the signal has optional arguments then this function will implement
     * emit() for the signal.
     */
    pyqt5EmitFn emitter;
} pyqt5QtSignalDef;


/*
 * This is the PyQt5-specific extension to the generated class type structure.
 */
typedef struct _pyqt5ClassExtensionDef {
    /*
     * A set of flags.  At the moment only bit 0 is used to say if the type is
     * derived from QFlags.
     */
    unsigned flags;

    /* A pointer to the QObject sub-class's staticMetaObject class variable. */
    const void *static_metaobject;

    /*
     * The table of signals emitted by the type.  These are grouped by signal
     * name.
     */
    const pyqt5QtSignalDef *qt_signals;

    /* The name of the interface that the class defines. */
    const char *qt_interface;
} pyqt5ClassExtensionDef;
'''
