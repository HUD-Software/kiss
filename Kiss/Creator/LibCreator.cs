/*
 * ProjectName
 *   -> interface
 *     -> proj_1_lib
 *       -> .h
 *   -> src
 *     -> .h, .cpp
 *   -> test
       -> .cpp
 *   -> benchmark
       -> .cpp
 *   -> target
 *     -> kiss.cache
 *     -> obj
 *   -> kiss.toml
 */
using Kiss.Project;
using Kiss.Manifest;

namespace Kiss.Creator
{
    public record LibCreator(string ProjectPath, string ProjectName, bool IsSanitizerEnabled, bool IsCoverageEnabled)
        : Creator(ProjectPath, ProjectName, Project.ProjectType.lib, IsSanitizerEnabled, IsCoverageEnabled)
    {
        protected override ProjectDescriptor Create(string projectRootPath)
        {
            try
            {
                var defaultManifest = Manifest.Manifest.Default(projectRootPath, ProjectName, Manifest.FileType.Json);
                defaultManifest.SaveToFile();

                ProjectDescriptor projectDescriptor = new ProjectDescriptor(projectRootPath, ProjectName, defaultManifest);
                Directory.CreateDirectory(projectDescriptor.Interface.Path);
                Directory.CreateDirectory(projectDescriptor.Source.Path);
                Directory.CreateDirectory(projectDescriptor.Test.Path);
                return projectDescriptor;
            }
            catch (Exception)
            {
                Console.Error.WriteLine("Error creating Json Manifest");
                throw;
            }            
        }

        protected override void Populate(ProjectDescriptor projectDescriptor)
        {
            // Add the interface header of the lib
            using (StreamWriter writer = new StreamWriter(projectDescriptor.Interface.AddNewFile("fibonacci.h")))
            {
                writer.Write("int fibonacci(int n);");
            }
            foreach (var file in projectDescriptor.Interface.Files)
            {
                Console.WriteLine(file);
            }
            // Add the source implementation of the lib
            using (StreamWriter writer = new StreamWriter(projectDescriptor.Source.AddNewFile("fibonacci.cpp")))
            {
                writer.Write(@"int fibonacci(int n)
{
    int a = 0, b = 1, c, i;
    if (n == 0)
    {
        return a;
    }
    for (i = 2; i <= n; i++)
    {
        c = a + b;
        a = b;
        b = c;
    }
    return b;
}");
            }

            // Add the GoogleTest tests
            using (StreamWriter writer = new StreamWriter(projectDescriptor.Test.AddNewFile("main.cpp")))
            {
                writer.Write(@"int main(int argc, char *argv[])
{
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}");
            }
            using (StreamWriter writer = new StreamWriter(projectDescriptor.Test.AddNewFile("test_fibonacci.cpp")))
            {
                writer.WriteLine($"#include <{projectDescriptor.ProjectName}/fibonacci.h>");
                writer.WriteLine($"TEST({projectDescriptor.ProjectName}, fibonacci)");
                writer.Write(@"{
    ASSERT_EQ(fibonacci(10), 55);
}");
            }
        }
    }
}
