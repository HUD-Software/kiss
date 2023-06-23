namespace Kiss.Generator
{
    public enum GeneratorType
    {
        VISUAL_STUDIO_2022_BUILDTOOLS,
        VISUAL_STUDIO_2022_COMMUNITY
    }

    public static class GeneratorTypeExtensions
    {
        const string VISUAL_STUDIO_2022_BUILDTOOL = "Visual Studio 2022 BuildTools";
        const string VISUAL_STUDIO_2022_COMMUNITY = "Visual Studio 2022 Community";

        public static string[] ToList()
        {
            return new string[] { VISUAL_STUDIO_2022_BUILDTOOL, VISUAL_STUDIO_2022_COMMUNITY };
        }

        public static GeneratorType FromString(string value) => value switch
        {
            VISUAL_STUDIO_2022_BUILDTOOL => GeneratorType.VISUAL_STUDIO_2022_BUILDTOOLS,
            VISUAL_STUDIO_2022_COMMUNITY => GeneratorType.VISUAL_STUDIO_2022_COMMUNITY,
            _ => throw new Exception("Invalid value")
        };
    }
}
