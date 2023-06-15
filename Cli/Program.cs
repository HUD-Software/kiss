/*
 * kiss new 
 *      'lib/dyn/bin' 
 *      {project_name} 
 *      -p/--path {project_dir} (Optional, default is current directory)
 *      -cov/--coverage (Enable code coverage)
 *      -san/--sanitizer (Enable code sanitizer)
 *      -gen/--generator {generator} (Optional, default is "CMake")
 * kiss build/run/test/publish
 *      -p/--path {project_dir} (Optional, default is current directory)
 *      -t/--target {target_platform} (Optional, default is current platform, else -> x86_64_pc_windows_msvc, etc...)
 *      -b/--build_dir {directory} (Optional, default is target/{target_platform}/{generator})
 *      -c/--config {debug/release} (Optional, default is release)
 *      -d/--debug_info (Optional, default is not set if -c is config, set if -c is debug)
 *      -cov/--coverage (Enable code coverage)
 *      -san/--sanitizer (Enable code sanitizer)
 *      -compiler {cl,clang}
 *      
 *      
 *  directories:
 *  proj
 *    -> .kiss
 *      -> cmake
 *          -> CMakeLists.txt
 *          -> cache.yaml
 *    -> src
 *      -> {project_name}/.h (Interface)
 *      -> .h/.cpp/... (Implementation)
 *    -> test
 *      -> main.cpp
 *      -> precompliled.h
 *      -> {test_files}.cpp
 *    -> benchmark
 *    -> kiss.yaml (kiss options)
 *    
 *    kiss.yaml
 *     -> author, address, etc...
 *     -> version (SemVer)
 *     -> platform_specifics
 *      -> enable_coverage: true/false
 *      -> enable_sanitizer: true/false
 *      -> compiler_specifics
 *       -> compile_options_debug
 *       -> compile_options_release
 *       -> compile_options_debug_info
 *      
 */

using Kiss.Creator;
using Kiss.Builder;
using System.CommandLine;
using Kiss.Generator;
using Command;

var rootCommand = new RootCommand("Kiss is used to create, run C/C++ project");

rootCommand.AddCommand(New.Create((command) =>
{
    var ProjectPath = Directory.GetCurrentDirectory();
    var ProjectName = command.Name;
    var IsCoverageEnabled = command.EnableCoverage;
    var IsSanitizerEnabled = command.EnableSanitizer;

    Creator creator = command.Type switch
    {
        Kiss.Project.ProjectType.bin => new BinCreator(ProjectPath, ProjectName, IsCoverageEnabled, IsSanitizerEnabled),
        Kiss.Project.ProjectType.dyn => new DynCreator(ProjectPath, ProjectName, IsCoverageEnabled, IsSanitizerEnabled),
        Kiss.Project.ProjectType.lib => new LibCreator(ProjectPath, ProjectName, IsCoverageEnabled, IsSanitizerEnabled),
        _ => throw new ArgumentException()
    };

    var project = creator.CreateIfNotExist(true);
    if(project == null)
    {
        Console.Error.WriteLine($"Failed to create the project {command.Name}");
    }
}));

rootCommand.AddCommand(Generate.Create((command) =>
{
    if(command is CMakeGenerate cmakeGenerator)
    {
        var ProjectPath = Directory.GetCurrentDirectory();
        var ProjectName = cmakeGenerator.Name;
        var IsCoverageEnabled = cmakeGenerator.EnableCoverage;
        var IsSanitizerEnabled = cmakeGenerator.EnableSanitizer;

        var generator = new CMakeGenerator(ProjectPath, ProjectName, cmakeGenerator.Type, IsCoverageEnabled, IsSanitizerEnabled);

        var result = generator.Generate();
        if (!result)
        {
            Console.Error.WriteLine($"Error while generating the project scripts {command.Name}");
        }
    }

}));

rootCommand.AddCommand(Build.Create((command) =>
{
    var ProjectPath = Directory.GetCurrentDirectory();
    var ProjectName = command.Name;
    var IsCoverageEnabled = command.EnableCoverage;
    var IsSanitizerEnabled = command.EnableSanitizer;

    Builder builder = new CMakeBuilder(ProjectPath, ProjectName, IsCoverageEnabled, IsSanitizerEnabled);

    var result = builder.Build();
    if (!result)
    {
        Console.Error.WriteLine($"Error while building the project {command.Name}");
    }
}));


return await rootCommand.InvokeAsync(args);
