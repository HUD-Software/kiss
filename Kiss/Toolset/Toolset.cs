using Kiss.Generator;
using Kiss.Toolset.Windows;
using System.Runtime.Versioning;

namespace Kiss.Toolset
{
    public class Toolset
    {
        public required string CCompilerPath { get; init; }
        public required string CXXCompilerPath { get; init; }
        public static Toolset? Create(GeneratorType Type)
        {
            switch (Type)
            {
                case GeneratorType.VISUAL_STUDIO_2022_BUILDTOOLS:
                case GeneratorType.VISUAL_STUDIO_2022_COMMUNITY:
                    {
                        if (OperatingSystem.IsWindows())
                        {
                            return VisualStudioToolset.Create(Type);
                        }
                        else
                        {
                            Logs.PrintErrorLine($"Visual Studio toolset is not supported on current platform");
                        }
                    }
                    break;
                default:
                    throw new NotImplementedException();
            }
            return null;
        }
    }
}
