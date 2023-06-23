using Kiss.Generator;
using System.Runtime.Versioning;

namespace Kiss.Toolset.Windows
{
    [SupportedOSPlatform("windows")]
    public class VisualStudioToolset : Toolset
    {
        public required SDK SDK { get; init; }

        public static new VisualStudioToolset? Create(GeneratorType Type)
        {
            var VSInfoList = VSWhere.LoadVisualStudioInstallationInfo();
            foreach (var VSInfo in VSInfoList)
            {
                Logs.PrintTipsLine($"Product : {VSInfo.Product}");
                Logs.PrintTipsLine($"Product name : {VSInfo.ProductName}");
                Logs.PrintTipsLine($"Product line version : {VSInfo.ProductLineVersion}");
                Logs.PrintTipsLine($"Generator : {VSInfo.GeneratorType}");
                Logs.PrintTipsLine($"Installation path : {VSInfo.InstallationPath}");
                Logs.PrintTipsLine($"Is C++ Build Tool installed : {VSInfo.IsVCBuildToolInstalled}");
                Logs.PrintTipsLine($"Default version : {VSInfo.DefaultVCToolVersion}");
                Logs.PrintTipsLine("");
            }

            var infoEnumerable = from VSInfo in VSInfoList
                                 where VSInfo.GeneratorType == Type
                                 select VSInfo;
            if (!infoEnumerable.Any())
            {
                Logs.PrintErrorLine($"No Visual studio toolset found for {Type}");
                return null;
            }

            var info = infoEnumerable.First();

            Logs.PrintTipsLine($"----------------Selected-----------------");
            Logs.PrintTipsLine($"Product : {info.Product}");
            Logs.PrintTipsLine($"Product name : {info.ProductName}");
            Logs.PrintTipsLine($"Product line version : {info.ProductLineVersion}");
            Logs.PrintTipsLine($"Generator : {info.GeneratorType}");
            Logs.PrintTipsLine($"Installation path : {info.InstallationPath}");
            Logs.PrintTipsLine($"Is C++ Build Tool installed : {info.IsVCBuildToolInstalled}");
            Logs.PrintTipsLine($"Default version : {info.DefaultVCToolVersion}");
            Logs.PrintTipsLine("");

            if (!info.IsVCBuildToolInstalled)
            {
                Logs.PrintErrorLine("The C++ Build Tool is not installed. Please install it.");
                return null;
            }

            var compilerDirectory = Path.Join(info.InstallationPath, $"VC\\Tools\\MSVC\\{info.DefaultVCToolVersion}\\bin\\Hostx64\\x64\\");
            if (!Directory.Exists(compilerDirectory))
            {
                Logs.PrintErrorLine($"Compiler directory not found : {compilerDirectory}");
                return null;
            }

            var compilerPath = Path.Join(compilerDirectory, "cl.exe");
            if (!File.Exists(compilerPath))
            {
                Logs.PrintErrorLine($"Compiler not found : {compilerPath}");
                return null;
            }

            // Select the SDK
            var sdkList = SDK.EnumerateInstalledSDK();
            if(sdkList is null || !sdkList.Any())
            {
                Logs.PrintErrorLine("No Windows SDK found. Please install Windows SDK");
                return null;
            }

            var osVersionString = Environment.OSVersion.Version;

            var sdk = sdkList.FirstOrDefault(sdk => sdk is not null ? osVersionString.ToString().StartsWith(sdk.OSVersionString) : false);

            if (sdk is null)
            {
                Logs.PrintErrorLine($"No default Windows SDK found for Windows {osVersionString}");
            }

            return new VisualStudioToolset
            {
                CCompilerPath = compilerPath,
                CXXCompilerPath = compilerPath,
                SDK = sdk!
            };
        }
    }
}
