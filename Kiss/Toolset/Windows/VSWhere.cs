using Kiss.Generator;
using Microsoft.VisualStudio.Setup.Configuration;
using System.Runtime.InteropServices;
using System.Runtime.Versioning;

namespace Kiss.Toolset.Windows
{
    // From https://github.com/microsoft/vs-setup-samples

    [SupportedOSPlatform("windows")]
    public class VSWhere
    {
        private const int REGDB_E_CLASSNOTREG = unchecked((int)0x80040154);

        /// <summary>
        /// Enumerate all VisualStudio instances installed
        /// </summary>
        /// <returns>Enumeration of all VisualStudio instances installed</returns>
        public static IEnumerable<VisualStudio> LoadVisualStudioInstallationInfo()
        {
            var vctoolList = new List<VisualStudio>();
            try
            {
                // Gets information about product instances installed on the machine.
                var query = new SetupConfiguration();
                // Helper functions.
                var helper = (ISetupHelper)query;

                // Gets information about product instances set up on the machine.
                var query2 = (ISetupConfiguration2)query;
                // Enumerates all product instances.
                var e = query2.EnumAllInstances();

                // Loop through all instances set up on the machine
                int fetched;
                var instances = new ISetupInstance[1];

                do
                {
                    e.Next(1, instances, out fetched);
                    if (fetched > 0)
                    {
                        // Get information about an instance of a product.
                        ISetupInstance instance = instances[0];
                        var instance2 = (ISetupInstance2)instance;

                        // Gets the state of the instance.
                        var state = instance2.GetState();

                        // An installation path must exists
                        if ((state & InstanceState.Local) != InstanceState.Local) continue;
                        var installationPath = instance2.GetInstallationPath();

                        // The product need to be registered to the instance
                        if ((state & InstanceState.Registered) != InstanceState.Registered) continue;
                        var product = instance2.GetProduct().GetId();

                        var isCPPBuildToolInstalled = product switch
                        {
                            "Microsoft.VisualStudio.Product.BuildTools" => IsWorkloadInstalled(instance2, "Microsoft.VisualStudio.Workload.VCTools") &&
                                                                           IsVCToolsInstalled(instance2),
                            "Microsoft.VisualStudio.Product.Community" => IsWorkloadInstalled(instance2, "Microsoft.VisualStudio.Workload.NativeDesktop") &&
                                                                          IsVCToolsInstalled(instance2),
                            _ => false
                        };

                        // Need the catalog information about the instance
                        if (instance is not ISetupInstanceCatalog catalog) continue;
                        ISetupPropertyStore store = catalog.GetCatalogInfo();

                        // Get the productLineVersion
                        var productLineVersionEnumerable = from property in store.GetNames()
                                                           where string.Equals(property, "productLineVersion", StringComparison.OrdinalIgnoreCase)
                                                           select new { Name = property, Value = store.GetValue(property) };
                        if (!productLineVersionEnumerable.Any()) continue;
                        var productLineVersion = productLineVersionEnumerable.First().Value;

                        // Get the productName
                        var productNameEnumerable = from property in store.GetNames()
                                                    where string.Equals(property, "productName", StringComparison.OrdinalIgnoreCase)
                                                    select new { Name = property, Value = store.GetValue(property) };
                        if (!productNameEnumerable.Any()) continue;
                        var productName = productNameEnumerable.First().Value;

                        // Get product display version
                        var installationVersion = instance.GetInstallationVersion();
                        var majorVersion = installationVersion.Split(".")[0];

                        GeneratorType type;
                        if (productLineVersion.Equals("2022"))
                        { 
                            switch (product!)
                            {
                                case "Microsoft.VisualStudio.Product.BuildTools":
                                    type = GeneratorType.VISUAL_STUDIO_2022_BUILDTOOLS;
                                    break;
                                case "Microsoft.VisualStudio.Product.Community":
                                    type = GeneratorType.VISUAL_STUDIO_2022_COMMUNITY;
                                    break;
                                default:
                                    continue;
                            }
                        }
                        else
                        {
                            continue;
                        }

                        // Read the default version
                        string? defaultVersion = GetVCToolsDefaultVersion(instance2);

                        vctoolList.Add(new VisualStudio
                        {
                            InstallationPath = installationPath,
                            Product = product,
                            IsVCBuildToolInstalled = isCPPBuildToolInstalled,
                            ProductLineVersion = productLineVersion,
                            MajorVersion = majorVersion,
                            ProductName = productName,
                            GeneratorType = type,
                            DefaultVCToolVersion = defaultVersion
                        });
                    }
                }
                while (fetched > 0);
            }
            catch (COMException ex) when (ex.HResult == REGDB_E_CLASSNOTREG)
            {
                Logs.PrintError("The query API is not registered. Assuming no instances are installed.");
            }
            catch (Exception ex)
            {
                Logs.PrintError($"Error 0x{ex.HResult:x8}: {ex.Message}");
            }
            return vctoolList;
        }

        /// <summary>
        /// Check if the <paramref name="workload"/> is installed with the installed <paramref name="instance2"/>
        /// </summary>
        /// <param name="instance2">The installed instance</param>
        /// <param name="workload">The workload to check</param>
        /// <returns>true if <paramref name="workload"/> is installed, false otherwise</returns>
        private static bool IsWorkloadInstalled(ISetupInstance2 instance2, string workload)
        {
            var workloads = from package in instance2.GetPackages()
                            where string.Equals(package.GetType(), "Workload", StringComparison.OrdinalIgnoreCase)
                            orderby package.GetId()
                            select package;

            var res = from workload2 in workloads
                      where string.Equals(workload2.GetId(), workload, StringComparison.OrdinalIgnoreCase)
                      select workload2;
            return res.Any();
        }

        /// <summary>
        ///  Check if the VCTools is installed with the installed <paramref name="instance2"/>
        /// </summary>
        /// <param name="instance2">The installed instance</param>
        /// <returns>true if VCTools is installed, false otherwise</returns>
        private static bool IsVCToolsInstalled(ISetupInstance2 instance2)
        {
            // From https://github.com/microsoft/vswhere/wiki/Find-VC
            var defaultVersion = Path.Join(instance2.GetInstallationPath(), "VC\\Auxiliary\\Build\\Microsoft.VCToolsVersion.default.txt");
            return File.Exists(defaultVersion);
        }

        private static string? GetVCToolsDefaultVersion(ISetupInstance2 instance2)
        {
            var defaultVersionFilePath = Path.Join(instance2.GetInstallationPath(), "VC\\Auxiliary\\Build\\Microsoft.VCToolsVersion.default.txt");
            if (File.Exists(defaultVersionFilePath))
            {
                try
                {
                    using (StreamReader reader = new StreamReader(defaultVersionFilePath))
                    {
                        string? line = reader.ReadLine();
                        return line?.Trim() ?? null;
                    }
                }
                catch (Exception e)
                {
                    Logs.PrintError(e.Message);
                }
            }
            return null;
        }
    }
}