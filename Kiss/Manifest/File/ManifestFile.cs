namespace Kiss.Manifest.File
{
    public abstract class ManifestFile
    {
        public required ManifestPackage Package { get; init; }
        public required ManifestProfiles? Profiles { get; init; }

        public abstract void SaveToFile(string projectRootPath);

        public abstract string Filepath(string projectRootPath);
    }
}
