namespace Kiss.Manifest
{
    public class Profiles
    {
        public required Profile Default { get; init; }

        public Profile? this[string key]
        {
            get
            {
                try
                {
                    return AllProfiles[key];
                }
                catch (KeyNotFoundException)
                {
                    return null;
                }
            }
        }
        public IEnumerable<string> Keys => AllProfiles.Keys;

        public required Dictionary<string, Profile> AllProfiles { get; init; }

    }
}
