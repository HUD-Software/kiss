using System.CommandLine;

namespace Command
{
    public record Build(string Name, bool EnableCoverage, bool EnableSanitizer)
    {
        public static System.CommandLine.Command Create(Action<Build> action)
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

            var command = new System.CommandLine.Command("build", "build a project");
            command.SetHandler((name, enableCoverage, enableSanitizer) =>
            {
                action.Invoke(new Build(name, enableCoverage, enableSanitizer));
            }, newProjectNameArgument, enableCoverage, enableSanitizer);

            return command;
        }
    }
}
