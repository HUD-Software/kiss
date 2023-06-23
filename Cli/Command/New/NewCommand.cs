using Cli.Command.Generate.Options;
using Cli.Command.New.Options;
using Kiss.Generator;
using Kiss.Project;
using System.CommandLine;

namespace Cli.Command.New
{
    internal class NewCommand
        : System.CommandLine.Command
    {
        public NewCommand(Func<NewOptions, int> action)
            : base("new", "create a new project")
        {
            var newTypeArgument = new Argument<string>(
                    name: "type",
                    description: "type of the project to create"
                ).FromAmong(ProjectTypeExtensions.ToList());

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
            AddArgument(newTypeArgument);
            AddArgument(newProjectNameArgument);
            AddOption(enableCoverage);
            AddOption(enableSanitizer);

            this.SetHandler(
                (type, projectName, enableCoverage, enableSanitizer) =>
                {
                    int returnCode = action.Invoke(new NewOptions(
                        Type: ProjectTypeExtensions.FromString(type),
                        ProjectName: projectName,
                        EnableCoverage: enableCoverage,
                        EnableSanitizer: enableSanitizer));
                    return Task.FromResult(returnCode);
                }, newTypeArgument, newProjectNameArgument, enableCoverage, enableSanitizer);
        }
    }
}