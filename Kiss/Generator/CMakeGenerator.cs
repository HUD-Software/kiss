using Kiss.Project;

namespace Kiss.Generator
{
    public record CMakeGenerator(string ProjectPath, string ProjectName, GeneratorType Type, bool IsSanitizerEnabled, bool IsCoverageEnabled)
        : Generator(ProjectPath, ProjectName, Type, IsSanitizerEnabled, IsCoverageEnabled)
    {
        public override bool Generate()
        {
            var projectRootPath = Path.Combine(ProjectPath, ProjectName);
            // Check if the project directory exists
            if (!Directory.Exists(projectRootPath))
            {
                Console.Error.WriteLine($"Path not found : {projectRootPath}");
                return false;
            }

            // Load the manifest of the projects
            var manifest = Manifest.Manifest.Load(projectRootPath, Manifest.FileType.Json);
            if (manifest is null)
            {
                return false;
            }

            ProjectDescriptor projectDescriptor = new ProjectDescriptor(ProjectPath, ProjectName, manifest);

            var VSInfoList = Toolset.VSWhere.LoadVisualStudioInstallationInfo();
            foreach (var VSInfo in VSInfoList)
            {
                Console.WriteLine($"Product : {VSInfo.Product}");
                Console.WriteLine($"Product name : {VSInfo.ProductName}");
                Console.WriteLine($"Product line version : {VSInfo.ProductLineVersion}");
                Console.WriteLine($"Installation path : {VSInfo.InstallationPath}");
                Console.WriteLine($"Is C++ Build Tool installed : {VSInfo.IsCPPBuildToolInstalled}");
                Console.WriteLine("");
            }
            return true;
        }
    }
}
