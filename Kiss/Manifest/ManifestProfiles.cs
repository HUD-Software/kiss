namespace Kiss.Manifest
{
    public class ManifestProfiles : ICloneable
    {
        public static readonly ManifestProfiles BUILT_IN = new ManifestProfiles
        {
            AllProfiles = new Dictionary<string, ManifestProfile>
                {
                    {
                        "debug",
                        new ManifestProfile
                        {
                            CoverageEnabled = true,
                            SanitizerEnabled = true,
                        }
                    },
                    {
                        "debug-opt",
                        new ManifestProfile
                        {
                            CoverageEnabled = true,
                            SanitizerEnabled = true,
                        }
                    },
                    {
                        "release",
                        new ManifestProfile
                        {
                            CoverageEnabled = false,
                            SanitizerEnabled = false,
                        }
                    }
                }
        };

        public required Dictionary<string, ManifestProfile> AllProfiles { get; init; }

        public ManifestProfile? this[string key]
        {
            get
            {
                ManifestProfile profile;
                return AllProfiles.TryGetValue(key, out profile!) ? profile : null;
            }
        }

        public ManifestProfile DefaultProfile() => AllProfiles["debug"];
        
        public IEnumerable<string> Keys => AllProfiles.Keys;

        public void Sync(ManifestProfiles otherProfiles)
        {
            foreach (var otherProfile in otherProfiles.AllProfiles)
            {
                // If we have the same profile, synchronize it
                if (AllProfiles.ContainsKey(otherProfile.Key))
                {
                    AllProfiles[otherProfile.Key].Sync(otherProfile.Value);
                }
                // If the profile is not present, add it
                else
                {
                    // Clone the value and set default value for values that is not in the manifest file
                    var manifestProfile = (ManifestProfile)otherProfile.Value.Clone();
                    manifestProfile.DefaultNullValues();
                    AllProfiles.Add(otherProfile.Key, manifestProfile);
                }
            }
        }

        public static ManifestProfiles Default()
        {
            return new ManifestProfiles
            {
                AllProfiles = new Dictionary<string, ManifestProfile>()
            };
        }

        public object Clone()
        {
            return new ManifestProfiles
            {
                AllProfiles = AllProfiles.ToDictionary(entry => (string)entry.Key.Clone(),
                                                       entry => (ManifestProfile)entry.Value.Clone())
            };
        }
    }
}
