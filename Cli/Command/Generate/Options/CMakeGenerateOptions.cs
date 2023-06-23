using Kiss.Generator;

namespace Cli.Command.Generate.Options
{
    internal record CMakeGenerateOptions(string ProjectName, GeneratorType Type, bool EnableCoverage, bool EnableSanitizer)
        : GenerateOptions(ProjectName);
}