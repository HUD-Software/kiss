using Newtonsoft.Json.Linq;
using Newtonsoft.Json;

namespace Kiss.Manifest.File.Json.Converters
{
    public class JsonManifestConverter : JsonConverter
    {
        public override bool CanConvert(Type objectType)
        {
            return objectType == typeof(JsonManifest);
        }

        public override object? ReadJson(JsonReader reader, Type objectType, object? existingValue, JsonSerializer serializer)
        {
            try
            {
                JObject jo = JObject.Load(reader);

                var package = jo["package"]?.ToObject<ManifestPackage>(serializer) ?? throw new ArgumentException("Missing package");
                var profiles = jo["profiles"]?.ToObject<ManifestProfiles>(serializer)!;

                return new JsonManifest
                {
                    Package = package,
                    Profiles = profiles,
                };
            }
            catch (JsonReaderException e)
            {
                Logs.PrintError(e.Message);
                return null;
            }
        }

        public override void WriteJson(JsonWriter writer, object? value, JsonSerializer serializer)
        {
            if (writer is JsonTextWriter writer1)
            {
                writer1.Indentation = 4;
                if (value is JsonManifest manifest)
                {
                    writer.WriteStartObject();
                    writer.WritePropertyName("package");
                    serializer.Serialize(writer, manifest.Package);
                    if (manifest.Profiles is not null)
                    {
                        writer.WritePropertyName("profiles");
                        serializer.Serialize(writer, manifest.Profiles);
                    }
                    writer.WriteEndObject();
                }
            }
        }
    }
}
