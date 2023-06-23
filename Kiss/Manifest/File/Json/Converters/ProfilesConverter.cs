using Newtonsoft.Json.Linq;
using Newtonsoft.Json;
using Kiss.Manifest.File.Json;

namespace Kiss.Manifest.File.Json.Converters
{
    public class ProfilesConverter : JsonConverter
    {
        public override bool CanConvert(Type objectType)
        {
            return objectType == typeof(ManifestProfiles);
        }

        public override object? ReadJson(JsonReader reader, Type objectType, object? existingValue, JsonSerializer serializer)
        {
            try
            {
                JObject jo = JObject.Load(reader);

                bool? DefaultSanitizerEnabled = null;
                bool? DefaultCoverageEnabled = null;
                var profiles = new Dictionary<string, ManifestProfile>();

                foreach (var child in jo.Children())
                {
                    switch (child.Type)
                    {
                        case JTokenType.Property:
                            if (child is JProperty property)
                            {
                                try
                                {
                                    if (property.Name.Equals("sanitizer", StringComparison.OrdinalIgnoreCase))
                                    {
                                        DefaultSanitizerEnabled = property.GetPropertyValue<bool>("sanitizer");
                                    }
                                    else if (property.Name.Equals("coverage", StringComparison.OrdinalIgnoreCase))
                                    {
                                        DefaultCoverageEnabled = property.GetPropertyValue<bool>("coverage");
                                    }
                                    else
                                    {
                                        var profile = property.Value.ToObject<ManifestProfile>(serializer);
                                        if (profile is not null)
                                        {
                                            profiles.Add(property.Name, profile);
                                        }
                                        else
                                        {
                                            throw new Exception($"{property.Name} ({(property as IJsonLineInfo).LineNumber}) is Unknown)");
                                        }
                                    }
                                }
                                catch (Exception e)
                                {
                                    Logs.PrintError(e.Message);
                                }
                            }
                            break;
                    }
                }
                return new ManifestProfiles
                {
                    AllProfiles = profiles,
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
            if (value is ManifestProfiles profiles)
            {
                writer.WriteStartObject();
                //writer.WritePropertyName("sanitizer");
                //serializer.Serialize(writer, profiles.Default.SanitizerEnabled);
                //writer.WritePropertyName("coverage");
                //serializer.Serialize(writer, profiles.Default.CoverageEnabled);
                foreach (var profile in profiles.AllProfiles)
                {
                    writer.WritePropertyName(profile.Key);
                    serializer.Serialize(writer, profile.Value);
                }
                writer.WriteEndObject();
            }
        }
    }
}
