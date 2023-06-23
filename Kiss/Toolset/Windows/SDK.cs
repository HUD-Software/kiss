using Microsoft.Win32;
using System;
using System.Runtime.Versioning;

namespace Kiss.Toolset.Windows
{
    [SupportedOSPlatform("windows")]
    public class SDK
    {
        public required string InstallationPath { get; init; }
        public required string OSVersionString { get; init; }
        public required string ProductVersion { get; init; }

        public static IEnumerable<SDK> EnumerateInstalledSDK()
        {
            var sdkList = new List<SDK>();
            var registryKey = Registry.LocalMachine.OpenSubKey("SOFTWARE\\WOW6432Node\\Microsoft\\Microsoft SDKs\\Windows");
            if (registryKey is not null)
            {
                foreach (string OSVersionString in registryKey!.GetSubKeyNames())
                {
                    RegistryKey? productKey = registryKey.OpenSubKey(OSVersionString);
                    if (productKey is null) continue;

                    // version looks like "v10.0" or "v8.1"
                    // We remove the first "v" to keep only the numbers
                    if (OSVersionString[0] != 'v') 
                    { 
                        Logs.PrintErrorLine("SDK version is not formatted correctly");
                        continue;
                    }
                    string OSVersionStringOnly = OSVersionString.Remove(0, 1);

                    string? installationPath;
                    string? productVersion;

                    productVersion = productKey.GetValue("ProductVersion") as string;
                    installationPath = productKey.GetValue("InstallationFolder") as string;
                    if (installationPath is null)
                    {
                        Logs.PrintErrorLine($"Cannot retrieves SDK {OSVersionString} \"InstallationFolder\" in registry {registryKey}");
                        continue;
                    }
                    if (productVersion is null)
                    {
                        Logs.PrintErrorLine($"Cannot retrieves SDK {OSVersionString} \"ProductVersion\" in registry {registryKey}");
                        continue;
                    }

                    sdkList.Add(new SDK
                    {
                        InstallationPath = installationPath,
                        ProductVersion = productVersion,
                        OSVersionString = OSVersionStringOnly
                    });
                }
            }
            return sdkList;
        }
    }
}
