namespace Kiss.Generator
{
   
    public abstract record Generator(string ProjectPath, string ProjectName, GeneratorType Type, bool IsSanitizerEnabled, bool IsCoverageEnabled)
    {
        public abstract bool Generate();
    }
}
