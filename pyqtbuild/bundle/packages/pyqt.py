# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


import os
import shutil

from ..abstract_package import AbstractPackage
from ..verbose import verbose


# The directory containing the DLLs.
_DLLS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dlls')


class PyQt(AbstractPackage):
    """ The base PyQt package. """

    def bundle_msvc_runtime(self, target_qt_dir, platform_tag):
        """ Bundle the MSVC runtime. """

        verbose("Bundling the MSVC runtime")

        self._bundle_dlls(target_qt_dir,
                os.path.join(_DLLS_DIR,
                        'msvc-64' if platform_tag == 'win_amd64' else 'msvc-32'))

    def bundle_openssl(self, target_qt_dir, openssl_dir, platform_tag):
        """ Bundle the OpenSSL DLLs. """

        # Qt v6.2.0 and later include appropriate backends.
        if self.qt_version >= (6, 2, 0):
            verbose(
                    "OpenSSL libraries are not required for Qt v6.2.0 and later")
            return

        if openssl_dir:
            verbose(
                    "Bundling the OpenSSL libraries from '{0}'".format(
                            openssl_dir))
        else:
            verbose("Bundling the default OpenSSL libraries")

            openssl_dir = os.path.join(_DLLS_DIR,
                    'openssl-64' if platform_tag == 'win_amd64' else 'openssl-32')

        self._bundle_dlls(target_qt_dir, openssl_dir)

    @staticmethod
    def _bundle_dlls(target_qt_dir, dlls_dir):
        """ Bundle the DLLs in a directory. """

        bin_dir = os.path.join(target_qt_dir, 'bin')
        os.makedirs(bin_dir, exist_ok=True)

        for dll in os.listdir(dlls_dir):
            shutil.copy2(os.path.join(dlls_dir, dll), bin_dir)
