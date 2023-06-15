using Kiss.Project;

namespace Kiss.Creator
{
    public record BinCreator(string ProjectPath, string ProjectName, bool IsSanitizerEnabled, bool IsCoverageEnabled)
        : Creator(ProjectPath, ProjectName, Project.ProjectType.bin, IsSanitizerEnabled, IsCoverageEnabled)
    {
        protected override ProjectDescriptor Create(string projectRootPath)
        {
            throw new NotImplementedException();
        }

        protected override void Populate(ProjectDescriptor projectDescriptor)
        {
            throw new NotImplementedException();
        }
    }
}
