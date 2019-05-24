# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools, AutoToolsBuildEnvironment
import os


class LibmadConan(ConanFile):
    name = "libmad"
    version = "0.15.1b"
    description = "MAD is a high-quality MPEG audio decoder.format."
    topics = ("conan", "mad", "MPEG", "audio", "decoder")
    url = "https://github.com/bincrafters/conan-libmad"
    homepage = "https://www.underbit.com/products/mad/"
    author = "Bincrafters <bincrafters@gmail.com>"
    license = "GPL-2.0-only"
    exports = ["LICENSE.md"]

    # Options may need to change depending on the packaged library.
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    # Custom attributes for Bincrafters recipe conventions
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    requires = (
        "OpenSSL/1.0.2r@conan/stable",
        "zlib/1.2.11@conan/stable"
    )

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx

    def source(self):
        source_url = "https://vorboss.dl.sourceforge.net/project/mad/libmad/{v}/libmad-{v}.tar.gz".format(v=self.version)
        tools.get(source_url, sha256="bbfac3ed6bfbc2823d3775ebb931087371e142bb0e9bb1bee51a76a6e0078690")
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def build(self):
        with tools.chdir(self._source_subfolder):
            if self.options.shared:
                args = ["--disable-static", "--enable-shared"]
            else:
                args = ["--disable-shared", "--enable-static"]
            env_build = AutoToolsBuildEnvironment(self)
            env_build.configure(args=args)
            env_build.make()
            env_build.install()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)

    def package_info(self):
        self.cpp_info.libs = ["mad"]
