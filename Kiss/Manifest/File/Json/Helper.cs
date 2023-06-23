using Newtonsoft.Json.Linq;
using Newtonsoft.Json;

namespace Kiss.Manifest.File.Json
{
    public static class Helper
    {
        public static T? GetPropertyValue<T>(this JProperty property, string name)
        {
            try
            {
                return (T?)Convert.ChangeType(property.Value, typeof(T));
            }
            catch (FormatException)
            {
                throw new Exception($"'{name}' ({(property as IJsonLineInfo).LineNumber}) key must contains {typeof(T)} value");
            }
        }
    }
}
