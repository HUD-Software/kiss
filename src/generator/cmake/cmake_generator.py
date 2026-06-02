import os
import subprocess
from pathlib import Path
from generator.generator import BaseGenerator


class CMakeGenerator(BaseGenerator):

    def name(self) -> str:
        return "cmake"

    # ── Public API ────────────────────────────────────────────────────────────

    def generate(self, project: dict, project_dir: Path) -> None:
        """Write CMakeLists.txt into project_dir."""
        content = self._build_cmake(project, project_dir)
        out = project_dir / "CMakeLists.txt"
        out.write_text(content)

    def build(self, project: dict, project_dir: Path, profile: str = "debug") -> int:
        """Configure + build with CMake. Returns exit code."""
        cmake_profile = self._cmake_build_type(profile)
        build_dir = project_dir / "build" / profile

        build_dir.mkdir(parents=True, exist_ok=True)

        # Configure
        ret = subprocess.call([
            "cmake",
            str(project_dir),
            f"-DCMAKE_BUILD_TYPE={cmake_profile}",
            "-G", "Ninja" if self._ninja_available() else "Unix Makefiles",
        ], cwd=build_dir)
        if ret != 0:
            return ret

        # Build
        return subprocess.call(["cmake", "--build", str(build_dir)])

    # ── CMakeLists.txt generation ─────────────────────────────────────────────

    def _build_cmake(self, project: dict, project_dir: Path) -> str:
        ptype   = project.get("_type", "bin")
        name    = project["name"]
        version = project.get("version", "0.1.0")
        sources = project.get("sources", [])
        includes = project.get("includes", [])
        deps    = project.get("dependencies", [])

        lines = [
            f"cmake_minimum_required(VERSION 3.20)",
            f"project({name} VERSION {version} LANGUAGES CXX)",
            f"",
            f"set(CMAKE_CXX_STANDARD 17)",
            f"set(CMAKE_CXX_STANDARD_REQUIRED ON)",
            f"set(CMAKE_CXX_EXTENSIONS OFF)",
            f"",
        ]

        # Sources
        if sources:
            lines.append("set(SOURCES")
            for src in sources:
                lines.append(f"    {src}")
            lines.append(")")
            lines.append("")

        # Target definition
        if ptype == "bin":
            lines += self._bin_target(name, deps)
        elif ptype == "lib":
            lines += self._lib_target(name, deps)
        elif ptype == "dyn":
            lines += self._dyn_target(name, deps)
        else:
            # Custom type treated as bin
            lines += self._bin_target(name, deps)

        # Include directories
        if includes:
            lines.append("")
            lines.append(f"target_include_directories({name} PUBLIC")
            for inc in includes:
                lines.append(f"    ${{CMAKE_CURRENT_SOURCE_DIR}}/{inc}")
            lines.append(")")

        # Profile-based compile options
        lines += self._profile_options(name)

        # Install rules
        lines += self._install_rules(name, ptype, includes)

        return "\n".join(lines) + "\n"

    # ── Target helpers ────────────────────────────────────────────────────────

    def _bin_target(self, name: str, deps: list) -> list[str]:
        lines = [f"add_executable({name} ${{SOURCES}})"]
        if deps:
            lines.append(f"target_link_libraries({name} PRIVATE {' '.join(deps)})")
        return lines

    def _lib_target(self, name: str, deps: list) -> list[str]:
        lines = [f"add_library({name} STATIC ${{SOURCES}})"]
        if deps:
            lines.append(f"target_link_libraries({name} PRIVATE {' '.join(deps)})")
        return lines

    def _dyn_target(self, name: str, deps: list) -> list[str]:
        NAME = name.upper()
        lines = [
            f"add_library({name} SHARED ${{SOURCES}})",
            f"target_compile_definitions({name} PRIVATE {NAME}_EXPORTS)",
        ]
        if deps:
            lines.append(f"target_link_libraries({name} PRIVATE {' '.join(deps)})")
        return lines

    # ── Profile compile options ───────────────────────────────────────────────

    def _profile_options(self, name: str) -> list[str]:
        return [
            "",
            "# Profile-based compile options",
            f"target_compile_options({name} PRIVATE",
            "    $<$<CONFIG:Debug>:-Od /Zi>",
            "    $<$<CONFIG:Release>:-O2 /O2>",
            "    $<$<CONFIG:RelWithDebInfo>:-O2 /Zi>",
            ")",
        ]

    # ── Install rules ─────────────────────────────────────────────────────────

    def _install_rules(self, name: str, ptype: str, includes: list) -> list[str]:
        lines = [
            "",
            "# Install rules",
            f"install(TARGETS {name}",
        ]
        if ptype == "bin":
            lines.append("    RUNTIME DESTINATION bin")
        elif ptype in ("lib", "dyn"):
            lines.append("    LIBRARY DESTINATION lib")
            lines.append("    ARCHIVE DESTINATION lib")
            lines.append("    RUNTIME DESTINATION bin")
        lines.append(")")

        if includes and ptype in ("lib", "dyn"):
            lines += [
                f"install(DIRECTORY",
            ]
            for inc in includes:
                lines.append(f"    {inc}/")
            lines.append("    DESTINATION include)")

        return lines

    # ── Utilities ─────────────────────────────────────────────────────────────

    def _cmake_build_type(self, profile: str) -> str:
        mapping = {
            "debug":   "Debug",
            "release": "Release",
            "asan":    "Debug",
        }
        return mapping.get(profile.lower(), "Debug")

    def _ninja_available(self) -> bool:
        import shutil
        return shutil.which("ninja") is not None
