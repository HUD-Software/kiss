using NuGet.Versioning;

namespace Kiss.Manifest
{
    public class ManifestPackage
    {
        public required string[] Authors { get; set; }
        public required string Name { get; set; }
        public required SemanticVersion Version { get; set; }

        public static ManifestPackage Default(string projectName)
        {
            return new ManifestPackage
            {
                Authors = new string[] { "me", "I", "myself" },
                Name = projectName,
                Version = new SemanticVersion(0, 0, 1),
            };
        }
    }
}
