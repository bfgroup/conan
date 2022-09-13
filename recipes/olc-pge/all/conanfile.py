'''
@author: René Ferdinand Rivera Morell
@copyright: Copyright René Ferdinand Rivera Morell 2021-2022
@license:
    Distributed under the Boost Software License, Version 1.0.
    (See accompanying file LICENSE_1_0.txt or copy at
    http://www.boost.org/LICENSE_1_0.txt)
'''
from conans import ConanFile, tools, errors
import os


required_conan_version = ">=1.52.0"


class Package(ConanFile):
    name = "olc-pge"
    homepage = "https://github.com/OneLoneCoder/olcPixelGameEngine"
    description = "The olcPixelGameEngine is a single-file prototyping and game-engine framework created in C++."
    topics = (
        "olc", "pge", "pixelengine", "pixelgameengine", "pgex",
        "engine", "graphics", "opengl",
        "game-engine", "game-development", "game-dev", "gamedev", "games")
    license = "OLC-3"
    url = "https://github.com/bfgroup/conan/tree/main/recipes/olc-pge"
    options = {
        "image_loader": ["png", "stb", "gdi"],
    }
    default_options = {
        "image_loader": "png",
    }
    settings = "os", "arch", "compiler", "build_type"
    barbarian = {
        "description": {"format": "asciidoc", "file": "README.adoc"}
    }
    exports = "README.adoc"
    source_subfolder = "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  strip_root=True, destination=self.source_subfolder)
        if tools.Version(self.version) <= tools.Version("2.16"):
            tools.replace_in_file(os.path.join(
                self.source_subfolder, "olcPixelGameEngine.h"), "#define GL_SILENCE_DEPRECATION", "")

    no_copy_source = True

    def config_options(self):
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

    def requirements(self):
        self.requires("opengl/system")
        if self.settings.os == "Linux":
            self.requires("xorg/system")
        if self.options.image_loader == "stb":
            self.requires("stb/cci.20210713")
        elif self.options.image_loader == "png":
            self.requires("libpng/1.6.37")

    def package_id(self):
        self.info.header_only()

    def package(self):
        self.copy(pattern="LICENCE.md", dst="licenses",
                  src=self.source_subfolder)
        # The main PGE header.
        self.copy(pattern="olcPixelGameEngine.h",
                  dst="include", src=self.source_subfolder)
        # Also add the included PGEX extensions.
        self.copy(pattern="*.h", dst="include",
                  src=self.source_subfolder+"/Extensions")

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
            self.cpp_info.frameworks.extend(["GLUT", "ObjC"])
