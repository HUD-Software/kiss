using Kiss.Manifest.File;

namespace Kiss.Manifest
{
    public class Manifest
    {
        public ManifestPackage Package { get; init; }
        public ManifestProfiles Profiles { get; init; }
        public ManifestFile? ManifestFile { get; init; }

        public Manifest(ManifestFile manifestFile)
        {
            ManifestFile = manifestFile;
            Package = ManifestPackage.Default(manifestFile.Package.Name);
            Profiles = (ManifestProfiles)ManifestProfiles.BUILT_IN.Clone();

            // Sync the manifest file with build-in profiles
            if(manifestFile.Profiles is not null)
            {
                Profiles.Sync(manifestFile.Profiles);
            }
        }
    }
}