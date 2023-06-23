namespace Kiss.Manifest
{
    public class ManifestProfile : ICloneable
    {
        public required bool? SanitizerEnabled { get; set; }
        public required bool? CoverageEnabled { get; set; }

        public object Clone()
        {
            return new ManifestProfile
            {
                SanitizerEnabled = SanitizerEnabled,
                CoverageEnabled = CoverageEnabled
            };
        }

        public void Sync(ManifestProfile otherProfile)
        {
            SanitizerEnabled = otherProfile.SanitizerEnabled;
            CoverageEnabled = otherProfile.CoverageEnabled;
        }

        public void DefaultNullValues()
        {
            SanitizerEnabled = SanitizerEnabled ?? false;
            CoverageEnabled = CoverageEnabled ?? false;
        }
    }


}
