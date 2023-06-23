namespace Cli.Command.Build.Options
{
    internal record BuildOptions(string ProjectName, bool EnableCoverage, bool EnableSanitizer);
}
