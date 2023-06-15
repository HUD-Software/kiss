namespace Kiss.Builder
{
    public abstract record Builder(string ProjectPath, string ProjectName, bool IsSanitizerEnabled, bool IsCoverageEnabled)
    {
        public abstract bool Build();
    }
}
