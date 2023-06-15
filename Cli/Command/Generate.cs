﻿using Kiss.Generator;
using System.CommandLine;

//generate cmake proj "Visual Studio 2022 BuildTool"

namespace Command
{
    public record Generate(string Name)
    {
        public static System.CommandLine.Command Create(Action<Generate> action)
        {
            var command = new System.CommandLine.Command("generate", "Genereate build scripts of a project");
            command.AddCommand(CMakeGenerate.Create((command) =>
            {
                action.Invoke(command);
            }));
            return command;
        }
    }

    internal record CMakeGenerate(string Name, GeneratorType Type, bool EnableCoverage, bool EnableSanitizer)
        : Generate(Name: Name)
    {
        public static System.CommandLine.Command Create(Action<CMakeGenerate> action)
        {
            var projectNameArgument = new Argument<string>(
                name: "name",
                description: "name of the project where to generate build scripts"
            );

            var generatorArgument = new Argument<string>(
                name: "generator",
                description: "Generator type to use"
            ).FromAmong(GeneratorTypeExtensions.ToList());

            var enableCoverageOption = new Option<bool>(
                name: "--cov",
                description: "enable code coverage",
                getDefaultValue: () => false
            );

            var enableSanitizerOption = new Option<bool>(
                name: "--san",
                description: "enable code sanitizer",
                getDefaultValue: () => false
            );

            var command = new System.CommandLine.Command("cmake", "Genereate build scripts of a project using CMake");
            command.AddArgument(projectNameArgument);
            command.AddArgument(generatorArgument);
            command.AddOption(enableCoverageOption);
            command.AddOption(enableSanitizerOption);

            command.SetHandler((name, generator, enableCoverage, enableSanitizer) =>
            {
                action.Invoke(new CMakeGenerate(
                    Name: name,
                    Type: GeneratorTypeExtensions.FromString(generator),
                    EnableCoverage: enableCoverage,
                    EnableSanitizer: enableSanitizer));
            }, projectNameArgument, generatorArgument, enableCoverageOption, enableSanitizerOption);

            return command;
        }
    }
}