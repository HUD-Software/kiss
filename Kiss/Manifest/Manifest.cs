using Kiss.Manifest.Json;

namespace Kiss.Manifest
{
    public enum FileType
    {
        Json
    }

    public class Manifest
    {
        public required string Filepath { get; init; }
        public Package Package => ManifestFile.Package;
        public Profiles? Profiles => ManifestFile.Profiles;
        public required ManifestFile ManifestFile { get; init; }

        public void SaveToFile() => ManifestFile.SaveToFile(Filepath);

        public static Manifest Default(string projectRootPath, string projectName, FileType type)
        {
            (ManifestFile file, string filename) manifest = type switch
            {
                FileType.Json => (JsonManifest.Default(projectName),JsonManifest.FILENAME),
                _ => throw new ArgumentException("Invalid manifest file type"),
            };
            return new Manifest
            {
                Filepath = Path.Combine(projectRootPath, manifest.filename),
                ManifestFile = manifest.file
            };
        }

        public static Manifest? Load(string projectRootPath, FileType type)
        {
            (ManifestFile? file, string filename) manifest = type switch
            {
                FileType.Json => (JsonManifest.Load(projectRootPath), JsonManifest.FILENAME),
                _ => throw new ArgumentException("Invalid manifest file type"),
            };
            if (manifest.file is null)
            {
                Console.Error.Write($"The manifest file {JsonManifest.FILENAME} not found in directory {projectRootPath}");
                return null;
            }

            return new Manifest
            {
                Filepath = Path.Combine(projectRootPath, manifest.filename),
                ManifestFile = manifest.file
            };
        }

    }
}