﻿using Newtonsoft.Json.Linq;
using Newtonsoft.Json;

namespace Kiss.Manifest.Json.Converters
{
    public class ProfileConverter : JsonConverter
    {
        public override bool CanConvert(Type objectType)
        {
            return objectType == typeof(Profile);
        }

        public override object? ReadJson(JsonReader reader, Type objectType, object? existingValue, JsonSerializer serializer)
        {
            try
            {
                JObject jo = JObject.Load(reader);

                bool? SanitizerEnabled = null;
                bool? CoverageEnabled = null;
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
                                        SanitizerEnabled = property.GetPropertyValue<bool>("sanitizer");
                                    }
                                    else if (property.Name.Equals("coverage", StringComparison.OrdinalIgnoreCase))
                                    {
                                        CoverageEnabled = property.GetPropertyValue<bool>("coverage");
                                    }
                                    else
                                    {
                                        throw new Exception($"{property.Name} ({(property as IJsonLineInfo).LineNumber}) is Unknown)");
                                    }
                                }
                                catch (Exception e)
                                {
                                    Console.Error.WriteLine(e.Message);
                                }
                            }
                            break;
                    }
                }
                return new Profile
                {
                    SanitizerEnabled = SanitizerEnabled,
                    CoverageEnabled = CoverageEnabled
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
            if (value is Profile profile)
            {
                writer.WriteStartObject();
                writer.WritePropertyName("sanitizer");
                serializer.Serialize(writer, profile.SanitizerEnabled);
                writer.WritePropertyName("coverage");
                serializer.Serialize(writer, profile.CoverageEnabled);
                writer.WriteEndObject();
            }
        }
    }
}
