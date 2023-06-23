using Kiss.Project;
using NuGet.Versioning;

namespace Kiss.Creator
{
    public abstract record Creator(string ProjectPath, string ProjectName, Project.ProjectType ProjectType, bool IsSanitizerEnabled, bool IsCoverageEnabled)
    {
        public ProjectDescriptor? CreateIfNotExist(bool populate) {
            var projectRootPath = Path.Combine(ProjectPath, ProjectName);
            if (!Directory.Exists(projectRootPath) || IsDirectoryEmpty(projectRootPath))
            {
                Directory.CreateDirectory(projectRootPath);
                var projectDescriptor = Create(projectRootPath);
                Populate(projectDescriptor);
                return projectDescriptor;
            }
            
            Logs.PrintErrorLine("Directory already exists and is not empty.");
            return null;
        }

        private bool IsDirectoryEmpty(string directory) => !Directory.EnumerateFileSystemEntries(directory).Any();
        
        protected abstract ProjectDescriptor Create(string projectRootPath);
        protected abstract void Populate(ProjectDescriptor projectDescriptor);
    }
}
