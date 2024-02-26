# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from dataclasses import dataclass
from enum import auto, Enum
from typing import List, Optional

from sipbuild import BuildSystemExtension


class PyQtBuildSystemExtension(BuildSystemExtension):
    """ This class implements the PyQt builder extension. """

    def append_class_extension_code(self, extendable, name, code):
        """ Append code fragments that implements a class extension data
        structure.
        """

        extension = self.get_extension_data(extendable)
        if extension is None:
            return

        qt_major = self.project.builder.qt_version >> 16

        code.append(f'static pyqt{qt_major}ClassExtensionDef {name} = {{')

        if qt_major == 5:
            code.append(f'    {extension.flags},')

        if extension.is_qobject and not extension.no_qmetaobject:
            cpp_name = self.query_class_cpp_name(extendable)
            static_metaobject = f'&{cpp_name}::staticMetaObject'
        else:
            static_metaobject = 'SIP_NULLPTR'

        code.append(f'    {static_metaobject},')

        code.append('    SIP_NULLPTR, // XXX qt_signals')

        qt_interface = f'"{extension.interface}"' if extension.interface is not None else 'SIP_NULLPTR'
        code.append(f'    {qt_interface},')

        code.append('};')

    def append_mapped_type_extension_code(self, extendable, name, code):
        """ Append code fragments that implements a mapped type extension data
        structure.
        """

        # This will only ever be called for PyQt6.

        extension = self.get_extension_data(extendable)
        if extension is None:
            return

        code.append(f'static pyqt6MappedTypeExtensionDef {name} = {{{extension.flags}}};\n')

    def append_sip_api_h_code(self, code):
        """ Append code fragments to be included in all generated sipAPI*.h
        files.
        """

        code.append(
                _PYQT6_SIP_API_H_CODE if self.project.builder.qt_version >= 0x060000 else _PYQT5_SIP_API_H_CODE)

    def complete_class(self, extendable):
        """ Complete the definition of a class. """

        qt_major = self.project.builder.qt_version >> 16
        module = f'PyQt{qt_major}.QtCore'

        if self.query_class_is_subclass(extendable, module, 'QObject'):
            extension = self.get_extension_data(extendable, _ClassExtension)
            extension.is_qobject = True

    def get_function_keywords(self):
        """ Return a sequence of function keywords to be recognised by the
        parser.
        """

        return ('Q_SIGNAL', 'Q_SLOT')

    def parse_class_annotation(self, extendable, name, raw_value, location):
        """ Parse a class annotation.  Return True if it was parsed. """

        if self.project.builder.qt_version < 0x060000:
            if name == 'PyQtFlag':
                extension = self.get_extension_data(extendable,
                        _ClassExtension)
                extension.flags = self.parse_integer_annotation(name,
                        raw_value, location)
                return True

            if name == 'PyQtFlagsEnums':
                extension = self.get_extension_data(extendable,
                        _ClassExtension)
                extension.flags_enums = self.parse_string_list_annotation(name,
                        raw_value, location)
                extension.flags |= 1
                return True

        if name == 'PyQtInterface':
            extension = self.get_extension_data(extendable, _ClassExtension)
            extension.interface = self.parse_string_annotation(name, raw_value,
                    location)
            return True

        if name == 'PyQtNoQMetaObject':
            extension = self.get_extension_data(extendable, _ClassExtension)
            extension.no_qmetaobject = self.parse_boolean_annotation(name,
                    raw_value, location)
            return True

        return False

    def parse_function_keyword(self, extendable, keyword):
        """ Parse a function keyword.  Return True if it was parsed. """

        if keyword == 'Q_SIGNAL':
            extension = self.get_extension_data(extendable, _FunctionExtension)
            extension.type = FunctionType.SIGNAL
            return True

        if keyword == 'Q_SLOT':
            extension = self.get_extension_data(extendable, _FunctionExtension)
            extension.type = FunctionType.SLOT
            return True

        return False

    def parse_mapped_type_annotation(self, extendable, name, raw_value,
            location):
        """ Parse a mapped type annotation.  Return True if it was parsed. """

        if self.project.builder.qt_version >= 0x060000:
            if name == 'PyQtFlag':
                extension = self.get_extension_data(extendable,
                        _MappedTypeExtension)
                extension.flags = self.parse_integer_annotation(name,
                        raw_value, location)
                return True

        return False

    def parse_namespace_annotation(self, extendable, name, raw_value,
            location):
        """ Parse a namespace annotation.  Return True if it was parsed. """

        if name == 'PyQtNoQMetaObject':
            extension = self.get_extension_data(extendable,
                    _NamespaceExtension)
            extension.no_qmetaobject = self.parse_boolean_annotation(name,
                    raw_value, location)
            return True

        return False


class FunctionType(Enum):
    """ The PyQt-specific function type. """

    # A signal.
    SIGNAL = auto()

    # A slot.
    SLOT = ()


@dataclass
class _ClassExtension:
    """ The additional data held for a class. """

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
