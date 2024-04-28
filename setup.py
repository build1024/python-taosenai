# Partially referenced from openfst-python (by Joan Puigcerver)
# https://pypi.org/project/openfst-python/

import sys
import os
import re
import shutil
import subprocess
import multiprocessing
import requests
from setuptools import setup, find_packages, Extension
from setuptools.command.build_ext import build_ext

OPENFST_VERSION = "1.6.9"

def copy(src, dst):
    print("copying {} -> {}".format(src, dst))
    shutil.copy(src, dst)

class OpenFstExtension(Extension):
    def __init__(self):
        Extension.__init__(self, name="taosenai.pywrapfst", sources=[])

class OpenFstBuild(build_ext):
    @property
    def openfst_basename(self):
        return "openfst-%s.tar.gz" % OPENFST_VERSION

    @property
    def openfst_dirname(self):
        return "%s/openfst-%s" % (self.build_temp, OPENFST_VERSION)

    @property
    def openfst_filename(self):
        return "%s/%s" % (self.build_temp, self.openfst_basename)

    @property
    def openfst_url(self):
        base_url = "http://www.openfst.org/twiki/pub/FST/FstDownload"
        return "%s/%s" % (base_url, self.openfst_basename)

    @property
    def openfst_main_lib(self):
        if sys.platform == "cygwin":
            return "%s/src/extensions/python/.libs/pywrapfst.dll" % self.openfst_dirname
        else:
            return "%s/src/extensions/python/.libs/pywrapfst.so" % self.openfst_dirname

    @property
    def openfst_deps_libs(self):
        if sys.platform == "cygwin":
            return [
                "%s/src/extensions/far/.libs/cygfstfar-13.dll" % self.openfst_dirname,
                "%s/src/extensions/far/.libs/cygfstfarscript-13.dll" % self.openfst_dirname,
                "%s/src/script/.libs/cygfstscript-13.dll" % self.openfst_dirname,
                "%s/src/lib/.libs/cygfst-13.dll" % self.openfst_dirname,
            ]
        else:
            return [
                "%s/src/extensions/far/.libs/libfstfar.so.13" % self.openfst_dirname,
                "%s/src/extensions/far/.libs/libfstfarscript.so.13" % self.openfst_dirname,
                "%s/src/script/.libs/libfstscript.so.13" % self.openfst_dirname,
                "%s/src/lib/.libs/libfst.so.13" % self.openfst_dirname,
            ]

    @property
    def output_dir(self):
        return "%s/taosenai" % self.build_lib

    def openfst_download(self):
        if not os.path.isdir(self.build_temp):
            os.makedirs(self.build_temp)

        filename = self.openfst_filename
        if not os.path.isfile(filename):
            r = requests.get(self.openfst_url, verify=False, stream=True)
            r.raw.decode_content = True
            with open(filename, "wb") as f:
                shutil.copyfileobj(r.raw, f)

    def openfst_extract(self):
        if not os.path.exists(self.openfst_dirname):
            self.check_command_existence("tar")
            self.check_command_existence("patch")
            extract_cmd = ["tar", "xzf", self.openfst_filename, "-C", self.build_temp]
            subprocess.check_call(extract_cmd)
            patch_cmd = ["patch", "-p1", os.path.join(self.openfst_dirname, "configure"), "openfst-1.6.9.patch"]
            subprocess.check_call(patch_cmd)

    def openfst_configure_and_make(self):
        if not os.path.exists(self.openfst_main_lib):
            self.check_command_existence("make")
            old_dir = os.getcwd()
            os.chdir(self.openfst_dirname)
            if os.path.exists("Makefile"):
                subprocess.check_call(["make", "distclean"])
            os.environ.update({
                "PYTHON":   sys.executable,
                "CFLAGS":   "-O2",
                "CXXFLAGS": "-O2"
            })
            configure_cmd = [
                "./configure",
                "--enable-python"
            ]
            subprocess.check_call(configure_cmd)
            subprocess.check_call([
                "make",
                "-j", str(multiprocessing.cpu_count()),
                r"LDFLAGS=-no-undefined -Wl,-rpath,'$$ORIGIN'" # --no-undefined: to prevent an error on cygwin
            ])
            os.chdir(old_dir)

    def openfst_copy_libraries(self, ext):
        main_lib_output_path = os.path.join(self.build_lib, ext._file_name)
        copy(self.openfst_main_lib, main_lib_output_path)
        for src in self.openfst_deps_libs:
            dst = "%s/%s" % (self.output_dir, os.path.basename(src))
            copy(src, dst)

    @staticmethod
    def check_command_existence(cmdname):
        with open(os.devnull, "w") as fwnull:
            try:
                subprocess.call([cmdname, "--version"], stdout=fwnull, stderr=fwnull)
            except OSError as ex:
                # add error message (for Python 2.7)
                ex.filename = cmdname
                raise ex

    def run(self):
        self.openfst_download()
        self.openfst_extract()
        self.openfst_configure_and_make()
        self.openfst_copy_libraries(self.extensions[0])

        cmd = self.get_finalized_command("build_py").build_lib
        self.write_stub(cmd, self.extensions[0])

setup(
    name='python-taosenai',
    version='0.0.1',
    url='https://github.com/build1024/python-taosenai',
    author='hira',
    description='A "soramimi"-generation library for Python.',
    packages=['taosenai'],
    ext_modules=[OpenFstExtension()],
    cmdclass=dict(build_ext=OpenFstBuild),
    setup_requires=["requests"]
)
