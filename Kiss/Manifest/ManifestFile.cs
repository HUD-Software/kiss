namespace Kiss.Manifest
{
    public abstract class ManifestFile
    { 
        public required Package Package { get; init; }
        public required Profiles? Profiles { get; init; }
        public abstract void SaveToFile(string Filepath);
    }
}
