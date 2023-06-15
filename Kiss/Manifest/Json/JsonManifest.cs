using Kiss.Manifest.Json.Converters;
using Newtonsoft.Json;
using NuGet.Versioning;

namespace Kiss.Manifest.Json
{
    public class JsonManifest : ManifestFile
    {
        public static readonly string FILENAME = "kiss.json";
        static readonly JsonSerializerSettings JSON_SETTINGS = new JsonSerializerSettings
        {
            Formatting = Formatting.Indented,
            Converters = new JsonConverter[] { new JsonManifestConverter(),
                                               new PackageConverter(),
                                               new ProfilesConverter(),
                                               new ProfileConverter()
                                             }
        };

        public static JsonManifest? Load(string projectRootPath)
        {
            using StreamReader sr = new(Path.Combine(projectRootPath, FILENAME));
            return JsonConvert.DeserializeObject<JsonManifest>(sr.ReadToEnd(), JSON_SETTINGS);
        }

        public static JsonManifest Default(string projectName)
        {
            return new JsonManifest
            {
                Package = new Package
                {
                    Authors = new string[] { "me", "I", "myself" },
                    Name = projectName,
                    Version = new SemanticVersion(0, 0, 1),
                },
                Profiles = null
            };
        }

        public override void SaveToFile(string Filepath)
        {
            using StreamWriter sw = new(Filepath);
            string json = JsonConvert.SerializeObject(this, JSON_SETTINGS);
            sw.Write(json);
        }
    }
}
