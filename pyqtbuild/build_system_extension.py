# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from dataclasses import dataclass
from enum import auto, Enum
from typing import List, Optional

from sipbuild import BuildSystemExtension


class PyQtBuildSystemExtension(BuildSystemExtension):
    """ This class implements the PyQt builder extension. """

    def append_class_extension_code(self, klass, name, code):
        """ Append code fragments that implements a class extension data
        structure.
        """

        extension = self.get_extension_data(klass)
        if extension is None:
            return

        pyqt_major = self._pyqt_major_version

        signals_name = name + '_signals'
        if self._pyqt_append_class_signals_table(klass, pyqt_major, signals_name, code):
            qt_signals = f'&{signals_name}'
        else:
            qt_signals = 'SIP_NULLPTR'

        code.append(f'static pyqt{pyqt_major}ClassExtensionDef {name} = {{')

        if pyqt_major == 5:
            code.append(f'    {extension.flags},')

        if extension.is_qobject and not extension.no_qmetaobject:
            cpp_name = self.query_class_cpp_name(klass)
            static_metaobject = f'&{cpp_name}::staticMetaObject'
        else:
            static_metaobject = 'SIP_NULLPTR'

        code.append(f'    {static_metaobject},')

        code.append(f'    {qt_signals},')

        qt_interface = f'"{extension.interface}"' if extension.interface is not None else 'SIP_NULLPTR'
        code.append(f'    {qt_interface},')

        code.append('};')

    def append_mapped_type_extension_code(self, mapped_type, name, code):
        """ Append code fragments that implements a mapped type extension data
        structure.
        """

        # This will only ever be called for PyQt6.

        extension = self.get_extension_data(mapped_type)
        if extension is None:
            return

        code.append(f'static pyqt6MappedTypeExtensionDef {name} = {{{extension.flags}}};\n')

    def append_sip_api_h_code(self, code):
        """ Append code fragments to be included in all generated sipAPI*.h
        files.
        """

        code.append(
                _PYQT6_SIP_API_H_CODE if self._pyqt_major_version == 6 else _PYQT5_SIP_API_H_CODE)

    def complete_class_definition(self, klass):
        """ Complete the definition of a class. """

        module = f'PyQt{self._pyqt_major_version}.QtCore'

        if self.query_class_is_subclass(klass, module, 'QObject'):
            extension = self.get_extension_data(klass, _ClassExtension)
            extension.is_qobject = True

    def complete_function_parse(self, function, scope):
        """ Complete the parsing of a (possibly scoped) function. """

        # We are only interested in class functions.
        if scope is None:
            return

        # Ignore if we are not in a signal or slot section.
        class_extension = self.get_extension_data(scope)
        if class_extension is None or class_extension.current_function_type is None:
            return None

        extension = self.get_extension_data(function, _FunctionExtension)
        extension.type = class_extension.current_function_type

    def get_class_access_specifier_keywords(self):
        """ Return a sequence of class action specifier keywords to be
        recognised by the parser.
        """

        return ('signals', 'Q_SIGNALS', 'slots', 'Q_SLOTS')

    def get_function_keywords(self):
        """ Return a sequence of function keywords to be recognised by the
        parser.
        """

        return ('Q_SIGNAL', 'Q_SLOT')

    def parse_argument_annotation(self, argument, name, raw_value, location):
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

    def parse_class_access_specifier(self, klass, primary, secondary):
        """ Parse a primary and optional secondary class access specifier.  If
        it was parsed return the C++ standard access specifier (ie. 'public',
        'protected' or 'private') to use, otherwise return None.
        """

        if primary in ('public', 'protected', 'private'):
            if secondary is None:
                # It's a standard C++ access specifier.
                function_type = None
            elif secondary in ('slots', 'Q_SLOTS'):
                function_type = FunctionType.SLOT
            else:
                return None
        elif primary in ('signals', 'Q_SIGNALS'):
            if secondary is not None:
                return None

            function_type = FunctionType.SIGNAL
            primary = 'public'

        extension = self.get_extension_data(klass, _ClassExtension)
        extension.current_function_type = function_type

        return primary

    def parse_class_annotation(self, klass, name, raw_value, location):
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

    def parse_function_keyword(self, function, keyword):
        """ Parse a function keyword.  Return True if it was parsed. """

        if keyword == 'Q_SIGNAL':
            extension = self.get_extension_data(function, _FunctionExtension)
            extension.type = FunctionType.SIGNAL
            return True

        if keyword == 'Q_SLOT':
            extension = self.get_extension_data(function, _FunctionExtension)
            extension.type = FunctionType.SLOT
            return True

        return False

    def parse_mapped_type_annotation(self, mapped_type, name, raw_value,
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

    def parse_namespace_annotation(self, namespace, name, raw_value,
            location):
        """ Parse a namespace annotation.  Return True if it was parsed. """

        if name == 'PyQtNoQMetaObject':
            extension = self.get_extension_data(namespace,
                    _NamespaceExtension)
            extension.no_qmetaobject = self.parse_boolean_annotation(name,
                    raw_value, location)
            return True

        return False

    def _pyqt_append_class_emitters(self, klass, code):
        """ Append the code for each signal emitter of a class. """

        # XXX

    def _pyqt_append_class_signals_table(self, klass, pyqt_major, table_name,
            code):
        """ Append the code to generate any signals table for a class.  Return
        True if a table was generated.
        """

        is_table = False

        for group_nr, group in enumerate(self.query_class_function_groups(klass)):
            signals = []
            non_signals = False

            for function in group:
                function_extension = self.get_extension_data(function)
                if function_extension is not None and function_extension.type is FunctionType.SIGNAL:
                    signals.append(function)
                else:
                    non_signals = True

            if not signals:
                continue

            if not non_signals:
                # No non-signals to handle.
                group_nr = -1

            if not is_table:
                is_table = True

                self._pyqt_append_class_emitters(klass, code)

                code.append(f'static const pyqt{pyqt_major}QtSignal {table_name}[] = {{')

            self._pyqt_append_signal_table_entry(function, klass, group_nr,
                    code)

            # Only handle non-signals in the first overload.
            group_nr = -1

        if is_table:
            code.append('    {SIP_NULLPTR, SIP_NULLPTR, SIP_NULLPTR, SIP_NULLPTR}\n};')

        return is_table

    def _pyqt_append_signal_table_entry(self, function, klass, group_nr, code):
        """ Append the code for a single signal in the signal table. """

        klass_name = self.query_class_cpp_name(klass).replace('::', '_')
        signal_name = self.query_function_cpp_name(function)

        # Build the normalised signature.
        need_unstripped = False
        has_optional_args = False

        stripped = []

        for arg in self.query_function_cpp_arguments(function):
            if self.query_argument_is_optional(arg):
                has_optional_args = True

            # See if /ScopesStripped/ was specified for the argument.
            extension = self.get_extension_data(arg)
            if extension is not None:
                need_unstripped = True
                strip = extension.scopes_stripped
            else:
                strip = -1

            arg_decl = self.query_argument_cpp_decl(arg, klass, strip=strip)

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

            for arg in self.query_function_cpp_arguments(function):
                unstripped.append(
                        self.query_argument_cpp_decl(arg, klass, strip=-1))

            unstripped_args = '|(' + ','.join(unstripped) + ')'
        else:
            unstripped_args = ''

        # Get the docstring.
        if self.bindings.docstrings:
            docstring = '"'

            default_docstring = self.query_function_default_docstring(function)
            explicit_docstring = self.query_function_docstring(function)

            if explicit_docstring is None:
                docstring += '\\1'
                docstring += default_docstring
            else:
                if self.query_function_default_docstring_is_prepended(function):
                    docstring += default_docstring
                    docstring += '\\n'

                docstring += explicit_docstring

                if self.query_function_default_docstring_is_appended(function):
                    docstring += '\\n'
                    docstring += default_docstring

            docstring += '"'
        else:
            docstring = 'SIP_NULLPTR'

        # Get the reference to a PyMethodDef structure that implements the
        # non-signal overloads.
        if group_nr >= 0:
            pymethoddef = self.query_class_function_group_pymethoddef_reference(
                    klass, group_nr)
        else:
            pymethoddef = 'SIP_NULLPTR'

        # We enable a hack that supplies any missing optional arguments.  We
        # only include the version with all arguments and provide an emitter
        # function which handles the optional arguments.
        emitter = f'emit_{klass_name}_{signal_name}' if has_optional_args else 'SIP_NULLPTR'

        code.append(f'    {{"{signal_name}({stripped_args}){unstripped_args}", {docstring}, {pymethoddef}, {emitter}}},')

    @property
    def _pyqt_major_version(self):
        """ The PyQt (and Qt) major version number. """

        return self.bindings.project.builder.qt_version >> 16


class FunctionType(Enum):
    """ The PyQt-specific function type. """

    # A signal.
    SIGNAL = auto()

    # A slot.
    SLOT = ()


@dataclass
class _ArgumentExtension:
    """ The additional data held for an argument. """

    # The value of /ScopesStripped/.
    scopes_stripped: int = 0


@dataclass
class _ClassExtension:
    """ The additional data held for a class. """

    # The current function type.
    current_function_type: Optional[FunctionType] = None

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


@dataclass
class _FunctionExtension:
    """ The additional data held for a function. """

    # The PyQt-specific function type.
    type: Optional[FunctionType] = None


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
_PYQT6_SIP_API_H_CODE = '''/*
 * The description of a Qt signal for PyQt6.
 */
typedef int (*pyqt6EmitFn)(void *, PyObject *);

typedef struct _pyqt6QtSignalDef {
    /* The normalised C++ name and signature of the signal. */
    const char *signature;

    /* The optional docstring. */
    const char *docstring;

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
_PYQT5_SIP_API_H_CODE = '''/*
 * The description of a Qt signal for PyQt5.
 */
typedef int (*pyqt5EmitFn)(void *, PyObject *);

typedef struct _pyqt5QtSignalDef {
    /* The normalised C++ name and signature of the signal. */
    const char *signature;

    /* The optional docstring. */
    const char *docstring;

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
