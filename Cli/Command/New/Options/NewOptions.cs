using Kiss.Project;

namespace Cli.Command.New.Options
{
    internal record NewOptions(ProjectType Type, string ProjectName, bool EnableCoverage, bool EnableSanitizer);
}
