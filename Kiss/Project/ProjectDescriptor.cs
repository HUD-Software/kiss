using Kiss.Manifest;
namespace Kiss.Project
{
    public class ProjectDescriptor
    {
        public ProjectDescriptor(string projectRootPath, string name, Manifest.Manifest manifest)
        {
            ProjectName = name;
            Interface = new Interface(projectRootPath, name);
            Source = new Source(projectRootPath);
            Test = new Test(projectRootPath);
            BuildDirectory = new BuildDirectory(projectRootPath);
            Manifest = manifest;
        }

        public string ProjectName{ get; init; }
        public Interface Interface { get; init; }
        public Source Source { get; init; } 
        public Test Test { get; init; }
        public BuildDirectory BuildDirectory { get; init; }
        public Manifest.Manifest Manifest { get; init; }
    }
}
