using Kiss.Manifest.File.Json;
using Kiss.Project;

namespace Kiss.Generator
{
    public record CMakeGenerator(string ProjectPath, string ProjectName, GeneratorType Type, bool IsSanitizerEnabled, bool IsCoverageEnabled)
        : Generator(ProjectPath, ProjectName, Type, IsSanitizerEnabled, IsCoverageEnabled)
    {
        static readonly string[] CPP_EXTENSION = new[] { "h", "hpp", "cpp", "c" };

        public override bool Generate()
        {
            var projectRootPath = Path.Combine(ProjectPath, ProjectName);

            // Check if the project directory exists
            if (!Directory.Exists(projectRootPath))
            {
                Logs.PrintErrorLine($"Path not found : {projectRootPath}");
                return false;
            }

            // Load the manifest of the projects
            var manifestFile = JsonManifest.Load(projectRootPath);
            if(manifestFile is null)
            {
                return false;
            }
            Manifest.Manifest manifest = new(manifestFile);

            Logs.PrintTipsLine("Manifest Content");
            Logs.PrintTipsLine("--------------------------");
            Logs.PrintTipsLine($"Authors : {String.Join(",", manifest.Package.Authors)}");
            Logs.PrintTipsLine($"Name : {manifest.Package.Name}");
            Logs.PrintTipsLine($"Version : {manifest.Package.Version}");
            foreach(var profile in manifest.Profiles.AllProfiles)
            {
                Logs.PrintTipsLine($"{profile.Key} :");
                Logs.PrintTipsLine($"  CoverageEnabled : {profile.Value.CoverageEnabled}");
                Logs.PrintTipsLine($"  SanitizerEnabled : {profile.Value.SanitizerEnabled}");
            }

            // Create build directory
            ProjectDescriptor projectDescriptor = new ProjectDescriptor(projectRootPath, ProjectName, manifest);
            projectDescriptor.BuildDirectory.CreateIfNotExist();
            WriteCMakeList(projectDescriptor.BuildDirectory.Path, projectDescriptor);
            

            // Get the toolset for the specified generator
            var toolset = Toolset.Toolset.Create(Type);
            if (toolset is null)
            {
                return false;
            }

            // Match Kiss generator with CMake generator
            string cmakeGenerator = Type switch
            {
                GeneratorType.VISUAL_STUDIO_2022_BUILDTOOLS or
                GeneratorType.VISUAL_STUDIO_2022_COMMUNITY => "Visual Studio 17 2022",
                _ => throw new NotImplementedException()
            };


            // Start CMake
            string[] args = new[] { 
                // Add source path
                "-S", projectDescriptor.BuildDirectory.Path,
                // Add CXX compiler
                $"-DCMAKE_CXX_COMPILER:FILEPATH=\"{toolset.CXXCompilerPath}\"",
                // Add C compiler
                $"-DCMAKE_C_COMPILER:FILEPATH=\"{toolset.CCompilerPath}\"",
                // Add target arch
                $"-A", "x64",
                // Add generator
                "-G", $"\"{cmakeGenerator}\"",
                // Add host arch
                "-T", "host=x64",
            };
            if (projectDescriptor.Manifest.Profiles.DefaultProfile().CoverageEnabled == true)
            {
                args.Append("-DCOVERAGE:BOOL=TRUE");
            }
            if (projectDescriptor.Manifest.Profiles.DefaultProfile().SanitizerEnabled== true)
            {
                args.Append("-DSANITIZER:BOOL=TRUE");
            }

            int exitCode = Exec.RunProcess("cmake", args);
            if (exitCode != 0)
                return false;
            return true;
        }

        private void WriteCMakeList(string cmakeListDirectory, ProjectDescriptor projectDescriptor)
        {
            var cmakeListPath = Path.Join(cmakeListDirectory, "CMakeLists.txt");
            using (StreamWriter sw = new(cmakeListPath))
            {
                WriteRootInCMakeList(sw, projectDescriptor);
                WriteSrcInCMakeList(sw, projectDescriptor, cmakeListDirectory);
                WriteTestInCMakeList(sw, projectDescriptor, cmakeListDirectory);
            }
        }

        private void WriteRootInCMakeList(StreamWriter sw, ProjectDescriptor projectDescriptor)
        {
            sw.WriteLine("cmake_minimum_required(VERSION 3.18)");
            sw.WriteLine("");
            sw.WriteLine($"project({projectDescriptor.ProjectName} LANGUAGES CXX )");
            sw.WriteLine("");
            if(projectDescriptor.Manifest.Profiles.DefaultProfile().CoverageEnabled == true)
            {
                sw.WriteLine("# If coverage is required, download the coverage module");
                sw.WriteLine("if(COVERAGE)");
                sw.WriteLine("  file(DOWNLOAD https://hud-software.github.io/cmake/coverage.cmake ${CMAKE_BINARY_DIR}/coverage.cmake)");
                sw.WriteLine("  include(${CMAKE_BINARY_DIR}/coverage.cmake)");
                sw.WriteLine("endif()");
                sw.WriteLine("");
            }

            if (projectDescriptor.Manifest.Profiles.DefaultProfile().SanitizerEnabled == true)
            {
                sw.WriteLine("# If sanitizer is required, download the sanitizer module");
                sw.WriteLine("if(SANITIZER)");
                sw.WriteLine("  file(DOWNLOAD https://hud-software.github.io/cmake/sanitizer.cmake ${CMAKE_BINARY_DIR}/sanitizer.cmake)");
                sw.WriteLine("  include(${CMAKE_BINARY_DIR}/sanitizer.cmake)");
                sw.WriteLine("endif()");
                sw.WriteLine("");
            }                
        }

        private void WriteSrcInCMakeList(StreamWriter sw, ProjectDescriptor projectDescriptor, string cmakeListPath)
        {
            sw.WriteLine($"# Add the static library \"{projectDescriptor.ProjectName}\"and separate the interface source files");
            sw.WriteLine("# from the private source files");
            sw.WriteLine($"add_library({projectDescriptor.ProjectName} STATIC)");
            sw.WriteLine("");

            // Write source implementation
            sw.WriteLine($"target_sources({projectDescriptor.ProjectName} PRIVATE");
            IEnumerable<string> sourceFiles = ListSortedFileWithExtensionInDirectory(projectDescriptor.Source.Path, CPP_EXTENSION);
            foreach (var file in sourceFiles)
            {
                sw.WriteLine($"  {Path.GetRelativePath(cmakeListPath, file).Replace(@"\", "/")}");
            }
            sw.WriteLine(")");

            // Add interface files
            sw.WriteLine($"target_sources({projectDescriptor.ProjectName} INTERFACE");
            IEnumerable<string> interfaceFiles = ListSortedFileWithExtensionInDirectory(projectDescriptor.Interface.Path, CPP_EXTENSION);
            foreach (var file in interfaceFiles)
            {
                sw.WriteLine($"  {Path.GetRelativePath(cmakeListPath, file).Replace(@"\", "/")}");
            }
            sw.WriteLine(")");
        }

        private void WriteTestInCMakeList(StreamWriter sw, ProjectDescriptor projectDescriptor, string cmakeListPath)
        {
            // Add executable to the cmakelist file and list all files in test directory
            sw.WriteLine($"# Add the test executable \"test_{projectDescriptor.ProjectName}\" and source files");
            sw.WriteLine("enable_testing()");
            sw.WriteLine($"add_executable(test_{projectDescriptor.ProjectName}");
            IEnumerable<string> testFiles = ListSortedFileWithExtensionInDirectory(projectDescriptor.Test.Path, CPP_EXTENSION);
            foreach (var file in testFiles)
            {
                sw.WriteLine($"  {Path.GetRelativePath(cmakeListPath, file).Replace(@"\", "/")}");
            }
            sw.WriteLine(")");

            // Link the test executable with the library to test
            sw.WriteLine($"# Link \"test_{projectDescriptor.ProjectName}\" with the \"{projectDescriptor.ProjectName}\" library");
            sw.WriteLine($"target_link_libraries(test_{projectDescriptor.ProjectName} PRIVATE {projectDescriptor.ProjectName})");
            sw.WriteLine("");
            sw.WriteLine($"# Add the \"{Path.GetDirectoryName(projectDescriptor.Source.Path)!.Replace(@"\", "/")}\" directory to the include directory path of \"test_{projectDescriptor.ProjectName}\"");
            sw.WriteLine($"target_include_directories(test_{projectDescriptor.ProjectName} PRIVATE {Path.GetRelativePath(cmakeListPath, projectDescriptor.Interface.Path).Replace(@"\", "/")})");

            // Add Google test dependency to the test project
            sw.WriteLine("# Download Google Test and make it available");
            sw.WriteLine("message(STATUS \"Fetching HUD-Software/google-test...\")");
            sw.WriteLine("include(FetchContent)");
            sw.WriteLine("FetchContent_Declare(");
            sw.WriteLine("  google_test");
            sw.WriteLine("  GIT_REPOSITORY  https://github.com/HUD-Software/google-test.git");
            sw.WriteLine("  GIT_TAG         5306f1a0e51f6001c624588fafdb646bb377866c");
            sw.WriteLine(")");
            sw.WriteLine("FetchContent_MakeAvailable(google_test)");
            sw.WriteLine($"# Link \"gtest\" with the \"{projectDescriptor.ProjectName}\" library");
            sw.WriteLine($"target_link_libraries(test_{projectDescriptor.ProjectName} PRIVATE gtest)");
            sw.WriteLine($"# Add a test to the project to be run by CTest");
            sw.WriteLine($"add_test(NAME test_{projectDescriptor.ProjectName} COMMAND test_{projectDescriptor.ProjectName} --gtest_output=xml:test_{projectDescriptor.ProjectName}_report.xml --extra-verbose --gtest_break_on_failure)");

            // Add the precompiled header
            sw.WriteLine($"# Add precompiled header to \"test_{projectDescriptor.ProjectName}\"");
            sw.WriteLine($"target_precompile_headers(test_{projectDescriptor.ProjectName} PRIVATE {Path.GetRelativePath(cmakeListPath, Path.Join(projectDescriptor.Test.Path, "precompiled.h")).Replace(@"\", "/")})");

            // Enable the sanitizer
            if(projectDescriptor.Manifest.Profiles.DefaultProfile().SanitizerEnabled == true)
            {
                sw.WriteLine("# If sanitizer is required enable it");
                sw.WriteLine("if(SANITIZER)");
                sw.WriteLine($"  enable_sanitizer(test_{projectDescriptor.ProjectName} {projectDescriptor.ProjectName})");
                sw.WriteLine("endif()");
            }

            // Enable the coverage
            if (projectDescriptor.Manifest.Profiles.DefaultProfile().CoverageEnabled == true)
            {
                sw.WriteLine("# If coverage is required enable it");
                sw.WriteLine("if(COVERAGE)");
                sw.WriteLine($"  enable_coverage(test_{projectDescriptor.ProjectName} {projectDescriptor.ProjectName})");
                sw.WriteLine("endif()");
            }
        }

        private IEnumerable<string> ListSortedFileWithExtensionInDirectory(string directory, string[] extension)
        {
            List<string> interfaceFiles = new();
            foreach (var ext in extension)
            {
                interfaceFiles.AddRange(Directory.EnumerateFiles(directory, $"*.{ext}"));
            }
            interfaceFiles.Sort();
            return interfaceFiles;
        }
    }
}
