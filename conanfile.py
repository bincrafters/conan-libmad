from conans import ConanFile, tools, AutoToolsBuildEnvironment, MSBuild
import os


class LibmadConan(ConanFile):
    name = "libmad"
    version = "0.15.1b"
    description = "MAD is a high-quality MPEG audio decoder.format."
    topics = ("conan", "mad", "MPEG", "audio", "decoder")
    url = "https://github.com/bincrafters/conan-libmad"
    homepage = "https://www.underbit.com/products/mad/"
    license = "GPL-2.0-only"
    exports = ["LICENSE.md"]
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        source_url = "https://freefr.dl.sourceforge.net/project/mad/libmad/{v}/libmad-{v}.tar.gz".format(v=self.version)
        sha256="bbfac3ed6bfbc2823d3775ebb931087371e142bb0e9bb1bee51a76a6e0078690"
        try:
            tools.get(source_url, sha256=sha256)
        except:
            tools.get("ftp://ftp.mars.org/pub/mpeg/libmad-%s.tar.gz" % self.version, sha256=sha256)
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    @property
    def _is_msvc(self):
        return self.settings.compiler == "Visual Studio"

    def build(self):
        if self._is_msvc:
            self._build_msvc()
        else:
            self._build_configure()

    def _build_msvc(self):
        #if self.settings.arch == "x86_64":
        #    tools.replace_in_file(os.path.join(self._source_subfolder, "mad.h"), "# define FPM_INTEL", "# define FPM_DEFAULT")
        with tools.chdir(os.path.join(self._source_subfolder, "msvc++")):
            # cl : Command line error D8016: '/ZI' and '/Gy-' command-line options are incompatible 
            tools.replace_in_file("libmad.dsp", "/ZI ", "")
            if self.settings.arch == "x86_64":
                tools.replace_in_file("libmad.dsp", "Win32", "x64")
                tools.replace_in_file("libmad.dsp", "FPM_INTEL", "FPM_DEFAULT")
                tools.replace_in_file("mad.h", "# define FPM_INTEL", "# define FPM_DEFAULT")
            with tools.vcvars(self.settings):
                self.run("devenv libmad.dsp /upgrade")
            msbuild = MSBuild(self)
            msbuild.build(project_file="libmad.vcxproj")

    def _build_configure(self):
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
        if self._is_msvc:
            self.copy(pattern="*.lib", dst="lib", src=self._source_subfolder, keep_path=False)
            self.copy(pattern="mad.h", dst="include", src=os.path.join(self._source_subfolder, "msvc++"))

    def package_info(self):
        self.cpp_info.libs = ["libmad" if self._is_msvc else "mad"]
