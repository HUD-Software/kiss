using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using NuGet.Versioning;

namespace Kiss.Manifest.Json.Converters
{
    public class PackageConverter : JsonConverter
    {
        public override bool CanConvert(Type objectType)
        {
            return objectType == typeof(Package);
        }

        public override object? ReadJson(JsonReader reader, Type objectType, object? existingValue, JsonSerializer serializer)
        {
            try
            {
                JObject jo = JObject.Load(reader);
                var packageName = (jo["name"]?.ToString()) ?? throw new ArgumentException("Missing package.name");
                var authors = (jo["authors"]?.ToObject<string[]>()) ?? throw new ArgumentException("Missing package.authors");
                var version = (jo["version"]?.ToObject<SemanticVersion>()) ?? throw new ArgumentException("Missing package.version");
                return new Package
                {
                    Name = packageName,
                    Authors = authors,
                    Version = version
                };
            }
            catch (JsonReaderException e)
            {
                Console.Error.Write(e.Message);
                return null;
            }
        }

        public override void WriteJson(JsonWriter writer, object? value, JsonSerializer serializer)
        {
            if (value is Package package)
            {
                writer.WriteStartObject();
                writer.WritePropertyName("name");
                serializer.Serialize(writer, package.Name);
                writer.WritePropertyName("authors");
                serializer.Serialize(writer, package.Authors);
                writer.WritePropertyName("version");
                serializer.Serialize(writer, package.Version);
                writer.WriteEndObject();
            }
        }
    }
}
