using Kiss.Generator;
using Microsoft.VisualStudio.Setup.Configuration;
using System.Runtime.InteropServices;
using System.Runtime.Versioning;

// From https://github.com/microsoft/vs-setup-samples

// Il faut que le Workload suivant soit présent:
// Visual studio :  Microsoft.VisualStudio.Workload.NativeDesktop
// Build Tools : Microsoft.VisualStudio.Workload.VCTools

// Si Microsoft.VCToolsVersion.default.txt n'est pas présent, il manque l'installation du Build Tool C++
namespace Kiss.Toolset.Windows
{
    // MSVC Community 2022 ou BuildTool 2022
    /// <summary>
    /// Visual Studio installation informations
    /// </summary>
    /// <param name="InstallationPath">The installation path</param>
    /// <param name="Product">The product ID</param>
    /// <param name="IsCPPBuildToolInstalled">true if C++ Build Tools is installed, false otherwise</param>
    /// <param name="ProductLineVersion">Product line version (2022,...)</param>
    /// <param name="ProductName">Product Name (Visual Studio,...) </param>
    [SupportedOSPlatform("windows")]
    public class VisualStudio
    {
        public required string InstallationPath { get; init; }
        public required string Product { get; init; }
        public required string ProductLineVersion { get; init; }
        public required string MajorVersion { get; init; }
        public required string ProductName { get; init; }
        public required GeneratorType GeneratorType { get; init; }
        public required bool IsVCBuildToolInstalled { get; init; }
        public required string? DefaultVCToolVersion { get; init; }
    }

}