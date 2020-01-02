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


import glob
import os

from setuptools import find_packages, setup


# Get the version number.
version_file_name = os.path.join('pyqtbuild', 'version.py')
try:
    version_file = open(version_file_name)
    version = version_file.read().strip().split('\n')[1].split()[-1][1:-1]
    version_file.close()
except FileNotFoundError:
    # Provide a minimal version file.
    version = '0.1.0.dev0'
    version_file = open(version_file_name, 'w')
    version_file.write(
            'PYQTBUILD_VERSION = 0\nPYQTBUILD_VERSION_STR = \'%s\'\n' %
                    version)
    version_file.close()

# Do the setup.
setup(
        name='PyQt-builder',
        version=version,
        license='BSD',
        python_requires='>=3.5',
        install_requires=['sip >=5.1, <6'],
        packages=find_packages(),
        package_data={
            'pyqtbuild.bundle': ['dlls/*/*'],
        },
        entry_points={
            'console_scripts': [
                    'pyqt-bundle = pyqtbuild.bundle.main:main']
        }
     )
