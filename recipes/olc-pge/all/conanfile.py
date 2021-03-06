from conans import ConanFile, tools, errors
import os

required_conan_version = ">=1.32.0"


class olcPixelGameEngineConan(ConanFile):
    name = "olc-pge"
    homepage = "https://github.com/OneLoneCoder/olcPixelGameEngine"
    description = '''\
The olcPixelGameEngine is a single-file prototyping and game-engine framework created in C++.

Options:

image_loader : The backend to use for loading image data.
    png : Uses libpng, and adds a dependency for it. This is the default on non-Windows platforms.
    stb : Uses stb single-file library, and adds a dependency for it.
    gdi : The default on Windows, uses system "gdi32" and "gdiplus" libraries.
'''
    topics = ("conan", "olc", "pge", "pixelengine", "pixelgameengine", "pgex",
              "game-development", "game-engine", "engine", "gamedev", "gaming", "graphics")
    license = "LicenseRef-LICENSE"
    url = "https://github.com/conan-io/conan-center-index"
    options = {
        "image_loader": ["png", "stb", "gdi"],
    }
    default_options = {
        "image_loader": "png",
    }
    
    settings = "os", "arch", "compiler", "build_type"
    build_policy = "missing"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        # Default option values.. (can be overridden by downstream)
        if self.settings.os == "Windows":
            self.options.image_loader = "gdi"

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 17)
        if self.options.image_loader == "gdi" and self.settings.os != "Windows":
            raise errors.ConanInvalidConfiguration(
                "GDI image loader only supported on Windows")
        if self.settings.os == "Linux":
            # Kludge to check if we can use the system OpenGL available.
            if os.path.exists("/usr/include/GL/glext.h"):
                glext = tools.load("/usr/include/GL/glext.h")
                if "ptrdiff_t" in glext:
                    raise errors.ConanInvalidConfiguration(
                        "Incompatible glext.h header with distro %s %s." % (tools.os_info.linux_distro, tools.os_info.os_version))
        if self.settings.compiler == "Visual Studio" and tools.Version(self.settings.compiler.version) < "15":
            raise errors.ConanInvalidConfiguration(
                "Visual Studio older than 15 not compatible")
        if self.settings.compiler == "apple-clang" and tools.Version(self.settings.compiler.version) < "11.0":
            raise errors.ConanInvalidConfiguration(
                "Xcode older than 11.0 not compatible")
        if self.settings.compiler == "gcc" and tools.Version(self.settings.compiler.version) < "8.0":
            raise errors.ConanInvalidConfiguration(
                "GCC older than 8.0 not compatible")
        if self.settings.compiler == "clang" and tools.Version(self.settings.compiler.version) < "7.0":
            raise errors.ConanInvalidConfiguration(
                "Clang older than 7.0 not compatible")
        # if self.settings.os == "Linux":
        #     if self.settings.compiler == "gcc":
        #         pass
        #     elif self.settings.compiler == "clang":
        #         pass
        #     with tools.chdir("/tmp"):
        #         tools.save()

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  strip_root=True, destination=self._source_subfolder)
        tools.replace_in_file(os.path.join(
            self._source_subfolder, "olcPixelGameEngine.h"), "#define GL_SILENCE_DEPRECATION", "")

    def requirements(self):
        self.requires("opengl/system")
        if self.settings.os == "Linux":
            self.requires("xorg/system")
        if self.options.image_loader == "stb":
            self.requires("stb/20200203")
        elif self.options.image_loader == "png":
            self.requires("libpng/1.6.37")

    def package(self):
        self.copy(pattern="LICENCE.md", dst="licenses",
                  src=self._source_subfolder)
        # The main PGE header.
        self.copy(pattern="olcPixelGameEngine.h",
                  dst="include", src=self._source_subfolder)
        # Also add the included PGEX extensions.
        self.copy(pattern="*.h", dst="include",
                  src=self._source_subfolder+"/Extensions")

    def package_info(self):
        self.cpp_info.libdirs = []
        if self.options.image_loader == "stb":
            self.cpp_info.defines = ["OLC_IMAGE_STB"]
        if self.options.image_loader == "png":
            self.cpp_info.defines = ["OLC_IMAGE_PNG"]
        if self.settings.os == "Windows":
            self.cpp_info.system_libs.extend([
                "user32",
                "shlwapi",
                "dwmapi",
            ])
            if self.options.image_loader == "gdi":
                self.cpp_info.defines = ["OLC_IMAGE_GDI"]
                self.cpp_info.system_libs.extend(["gdi32", "gdiplus", ])
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["pthread", "stdc++fs"]
        if self.settings.os == "Macos":
            self.cpp_info.frameworks.extend(["GLUT"])
