
namespace Kiss.Builder
{
    public record CMakeBuilder(string ProjectPath, string ProjectName, bool IsSanitizerEnabled, bool IsCoverageEnabled)
        : Builder(ProjectPath, ProjectName, IsSanitizerEnabled, IsCoverageEnabled)
    {
        public override bool Build()
        {
            throw new NotImplementedException();
        }
    }
}
