using Cli.Command.Generate.Options;

namespace Cli.Command.Generate
{
    internal class GenerateCommand
        : System.CommandLine.Command
    {
        public GenerateCommand(Func<GenerateOptions, int> generateAction)
            : base("generate", "Genereate build scripts of a project")
        {
            // Create subcommand for "generate" command
            var cmakeCommand = new CMakeGenerateCommand(cmakeGenerateAction => generateAction.Invoke(cmakeGenerateAction));
            AddCommand(cmakeCommand);
        }
    }
}
