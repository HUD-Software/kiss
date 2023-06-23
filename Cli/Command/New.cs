using Kiss.Project;
using System.CommandLine;

// new lib proj
namespace Command
{
    public record New(ProjectType Type, string Name, bool EnableCoverage, bool EnableSanitizer)
    {
        public static System.CommandLine.Command Create(Func<New, int> action)
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
            var command = new System.CommandLine.Command("new", "create a new project");
            command.AddArgument(newTypeArgument);
            command.AddArgument(newProjectNameArgument);
            command.AddOption(enableCoverage);
            command.AddOption(enableSanitizer);

            command.SetHandler((type, name, enableCoverage, enableSanitizer) =>
            {
                int returnCode = action.Invoke(new New(ProjectTypeExtensions.FromString(type), name, enableCoverage, enableSanitizer));
                return Task.FromResult(returnCode);
            }, newTypeArgument, newProjectNameArgument, enableCoverage, enableSanitizer);

            return command;
        }
    }
}