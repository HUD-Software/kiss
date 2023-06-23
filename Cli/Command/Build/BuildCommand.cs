using Cli.Command.Generate;
using Cli.Command.Build.Options;
using System.CommandLine;
using System;

namespace Cli.Command.Build
{
    internal class BuildCommand
        : System.CommandLine.Command
    {
        public BuildCommand(Func<BuildOptions, int> action)
            : base("build", "build a project")
        {
            var newProjectNameArgument = new Argument<string>(
                name: "name",
                description: "name of the project to create"
            );

            var enableCoverage = new Option<bool>(
                name: "--cov",
                description: "enable code coverage",
                getDefaultValue: () => false
            );

            var enableSanitizer = new Option<bool>(
                name: "--san",
                description: "enable code sanitizer",
                getDefaultValue: () => false
            );
            AddArgument(newProjectNameArgument);
            AddOption(enableCoverage);
            AddOption(enableSanitizer);

            this.SetHandler(
               (projectName, enableCoverage, enableSanitizer) =>
               {
                   int returnCode = action.Invoke(new BuildOptions(projectName, enableCoverage, enableSanitizer));
                   return Task.FromResult(returnCode);
               }, newProjectNameArgument, enableCoverage, enableSanitizer);
        }
    }
}
