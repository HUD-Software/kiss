namespace Kiss.Builder
{
    public record CMakeBuilder(string ProjectPath, string ProjectName, bool IsSanitizerEnabled, bool IsCoverageEnabled)
        : Builder(ProjectPath, ProjectName, IsSanitizerEnabled, IsCoverageEnabled)
    {
        public override bool Build()
        {
            //ProjectDescriptor projectDescriptor = new ProjectDescriptor(ProjectPath, ProjectName, manifest);

            //var toolset = Toolset.Toolset.Create(Type);
            //if (toolset is null)
            //{
            //    return false;
            //}

            //string cmakeGenerator = Type switch
            //{
            //    GeneratorType.VISUAL_STUDIO_2022_BUILDTOOLS or
            //    GeneratorType.VISUAL_STUDIO_2022_COMMUNITY => "Visual Studio 17 2022",
            //    _ => throw new NotImplementedException()
            //};

            //string[] args = new() { ["-S", $"{Path.GetRelativePath(manifest.ManifestFile.Filepath(), projectDescriptor.BuildDirectory)}"]}

            //Exec.RunProcess("cmake", new[] { "ddsp" });

            throw new NotImplementedException();
        }
    }
}
