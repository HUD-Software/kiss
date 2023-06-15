namespace Kiss.Project
{
    public enum ProjectType
    {
        bin, lib, dyn
    }

    public static class ProjectTypeExtensions
    {
        public static string[] ToList()
        {
            return new string[] { ProjectType.bin.ToString(), ProjectType.lib.ToString(), ProjectType.dyn.ToString() };
        }

        public static ProjectType FromString(string value) => value switch
        {
            "bin" => ProjectType.bin,
            "lib" => ProjectType.lib,
            "dyn" => ProjectType.dyn,
            _ => throw new Exception("Invalid value")
        };
    }


}
