
namespace Kiss.Project
{
    public class BuildDirectory
    {
        public BuildDirectory(string directory)
        {
            Path = System.IO.Path.Join(directory, "target");
        }

        public string Path { get; init; }
    }
}
