using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using NuGet.Versioning;
using System.Text.Json.Nodes;

namespace Kiss.Project
{
//    public class ManifestAlreadyExistException : Exception
//    {
//        public ManifestAlreadyExistException(string directory)
//        : base($"The manifest file {Manifest.Filename} already exist in directory {directory}")
//        { }
//    }

//    public class ManifestFileNotFound : Exception
//    {
//        public ManifestFileNotFound(string directory)
//        : base($"The manifest file {Manifest.Filename} not found in directory {directory}")
//        { }
//    }

//    public class ManifestBadVersionStringException : Exception
//    {
//        public ManifestBadVersionStringException(string tomlString)
//        : base("The version in the Manifest must be \"MAJOR.MINOR.PATCH\" where MAJOR, MINOR and PATCH are 32 bits integers.\n" +
//               $"Current: \"{tomlString}\"" +
//               $"Expect \"MAJOR.MINOR.PATCH\"")
//        { }

//        public ManifestBadVersionStringException(string tomlString, Exception innerException)
//        : base("The version in the Manifest must be \"MAJOR.MINOR.PATCH\" where MAJOR, MINOR and PATCH are 32 bits integers.\n" +
//               $"Current: \"{tomlString}\"" +
//               $"Expect \"MAJOR.MINOR.PATCH\"", innerException)
//        { }
//    }
 
//    public record Package
//    {
//        public Package() { }

//        public string[] Authors { get; init; }

//        public string Name { get; init; }

//        public SemanticVersion Version { get; init; }
//    }

//    public class Profile 
//    {
//        public bool SanitizerEnabled { get; init; }
//        public bool CoverageEnabled { get; init; }
//    }

//    public class Profiles
//    {
//        public Profile Default { get; } = new Profile
//        {
//            SanitizerEnabled = false,
//            CoverageEnabled = false,
//        };

//        public Profile this[string key] => _profiles[key];
//        public IEnumerable<string> Keys => _profiles.Keys;

//        private Dictionary<string, Profile> _profiles = new Dictionary<string, Profile>();

//    }

//    public class Manifest
//    {
//        public static readonly string Filename = "kiss.json";

//        public Manifest() { }

//        public Package Package { get; init; }

//        public Profiles Profiles { get; init; }

//        public string Filepath { get; init; }

//        public static bool CreateManifestFileIfNotExist(Manifest manifest)
//        {
//            if (File.Exists(manifest.Filepath))
//            {
//                Console.Error.WriteLine("Manifest file already exists.");
//                return false;
//            }

//            return Save(manifest);
//        }

//        public static Manifest Load(string directory)
//        {
//            if (!File.Exists(Path.Combine(directory, Filename)))
//            {
//                return null;
//            }
//            return new Manifest();
//            //RegisterTomlMappers();
//            //TomlDocument document = TomlParser.ParseFile(Path.Combine(directory, Filename));
//            //return TomletMain.To<Manifest>(document);
//        }

//        public static bool Save(Manifest manifest)
//        {
//            try
//            {
//                using StreamWriter stream = new(manifest.Filepath);
//                using JsonTextWriter writer = new(stream)
//                {
//                    Indentation = 4,
//                    Formatting = Formatting.Indented,
                    
//                };
////                manifest.WriteTo(writer);
//                //var manifest_file = File.OpenWrite(manifest.Filepath);
//                //RegisterTomlMappers();

//                //string tomlString = TomletMain.TomlStringFrom(manifest);
//                //using (StreamWriter writer = new StreamWriter(manifest_file))
//                //{
//                //    writer.Write(tomlString);
//                //    Console.Write(tomlString);
//                //}
//                return true;
//            }
//            catch (Exception e)
//            {
//                Console.Error.WriteLine(e.Message);
//            }
//            return false;
//        }

//        private class ManifestJsonConverter : JsonConverter
//        {
//            public override bool CanConvert(Type objectType)
//            {
//                return typeof(Manifest) == objectType;
//            }

//            public override object ReadJson(JsonReader reader, Type objectType, object existingValue, JsonSerializer serializer)
//            {
//                throw new NotImplementedException();
//            }

//            public override void WriteJson(JsonWriter writer, object value, JsonSerializer serializer)
//            {
//                if (value is Manifest manifest)
//                {
//                    JObject root = new JObject();
//                    root.Add("package");
//                }
//            }
//        }
//    }

    
}
