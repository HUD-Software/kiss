using Cli.Command.Generate.Options;
using Kiss.Generator;
using System.CommandLine;

namespace Cli.Command.Generate
{
    internal class CMakeGenerateCommand
        : System.CommandLine.Command
    {
        public CMakeGenerateCommand(Func<CMakeGenerateOptions, int> action)
            : base("cmake", "Genereate build scripts of a project using CMake")
        {
            var projectNameArgument = new Argument<string>(
                name: "name",
                description: "name of the project where to generate build scripts"
            );

            var generatorTypeArgument = new Argument<string>(
                name: "generator",
                description: "Generator type to use"
            ).FromAmong(GeneratorTypeExtensions.ToList());

            var enableCoverageOption = new Option<bool>(
                name: "--cov",
                description: "enable code coverage",
                getDefaultValue: () => false
            );

            var enableSanitizerOption = new Option<bool>(
                name: "--san",
                description: "enable code sanitizer",
                getDefaultValue: () => false
            );

            AddArgument(projectNameArgument);
            AddArgument(generatorTypeArgument);
            AddOption(enableCoverageOption);
            AddOption(enableSanitizerOption);

            this.SetHandler(
                (projectName, generatorType, enableCoverage, enableSanitizer) =>
                {
                    int returnCode = action.Invoke(new CMakeGenerateOptions(
                            ProjectName: projectName,
                            Type: GeneratorTypeExtensions.FromString(generatorType),
                            EnableCoverage: enableCoverage,
                            EnableSanitizer: enableSanitizer
                        ));
                    return Task.FromResult(returnCode);
                }, projectNameArgument, generatorTypeArgument, enableCoverageOption, enableSanitizerOption);
        }
    }
}
