# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from dataclasses import dataclass

from sipbuild import BuildSystemExtension


class PyQtBuildSystemExtension(BuildSystemExtension):
    """ This class implements the PyQt builder extension. """

    def append_mapped_type_extension_code(self, extendable, name, code):
        """ Append code fragments that implements a mapped type extension data
        structure.
        """

        # This will only ever be called for PyQt6.

        mapped_type_extensions = self.get_extension_data(extendable)
        if mapped_type_extensions is not None and mapped_type_extensions.flags:
                code.append(f'static pyqt6MappedTypeExtensionDef {name} = {{{mapped_type_extensions.flags}}};\n')

    def append_sip_api_h_code(self, code):
        """ Append code fragments to be included in all generated sipAPI*.h
        files.
        """

        code.append(
                _PYQT6_SIP_API_H_CODE if self.project.builder.qt_version >= 0x060000 else _PYQT5_SIP_API_H_CODE)

    def parse_mapped_type_annotations(self, extendable, annotations):
        """ Parse any mapped type annotations.  Any annotations dealt with
        should be removed from the dict.
        """

        # This will only ever be called for PyQt6.

        flags = annotations.pop('PyQtFlags', 0)
        if flags:
            mapped_type_extensions = self.get_extension_data(extendable,
                    _PyQt6MappedTypeExtensions)
            mapped_type_extensions.flags = flags


@dataclass
class _PyQt6MappedTypeExtensions:
    """ The additional PyQt6-specific data held for a mapped type. """

    # Non-zero if /PyQtFlags/ was specified.
    flags: int = 0


# The code to include in sipAPI*.h for PyQt6.
_PYQT6_SIP_API_H_CODE = '''/*
 * The description of a Qt signal for PyQt6.
 */
typedef int (*pyqt6EmitFn)(void *, PyObject *);

typedef struct _pyqt6QtSignal {
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
} pyqt6QtSignal;


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
    /* A pointer to the QObject sub-class's staticMetaObject class variable. */
    const void *static_metaobject;

    /*
     * A set of flags.  At the moment only bit 0 is used to say if the type is
     * derived from QFlags.
     */
    unsigned flags;

    /*
     * The table of signals emitted by the type.  These are grouped by signal
     * name.
     */
    const pyqt5QtSignalDef *qt_signals;

    /* The name of the interface that the class defines. */
    const char *qt_interface;
} pyqt5ClassExtensionDef;
'''
