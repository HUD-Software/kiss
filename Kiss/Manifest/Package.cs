using NuGet.Versioning;

namespace Kiss.Manifest
{
    public class Package
    {
        public required string[] Authors { get; init; }

        public required string Name { get; init; }

        public required SemanticVersion Version { get; init; }
    }
}
