from clean import CleanContext
from cleaner import BaseCleaner
from cli import KissParser
from cmake.cmake_context import CMakeContext
import console



class CleanerCMake(BaseCleaner):
    @classmethod
    def add_cli_argument_to_parser(cls, parser: KissParser):
        pass

    def __init__(self, parser: KissParser = None):
        super().__init__("cmake", "Clean cmake CMakeLists.txt")

    def clean_project(self, clean_context: CleanContext):

        if not clean_context.project is None:
            # Clean the project
            context = CMakeContext(current_directory=clean_context.directory, 
                                platform_target=clean_context.platform_target, 
                                project=clean_context.project)
            
            # Delete build directory
            if context.build_directory.exists():
                console.print_step(f"Removing build directory: {str(context.build_directory)}")
                import shutil
                shutil.rmtree(context.build_directory)

            # Delete output directory
            if context.output_directory(clean_context.config).exists():
                console.print_step(f"Removing output directory: {str(context.output_directory(clean_context.config))}")
                import shutil
                shutil.rmtree(context.output_directory(clean_context.config))

            # Delete CMakeLists.txt file
            if context.cmakefile.exists():
                console.print_step(f"Removing CMakeLists.txt: {str(context.cmakefile)}")
                context.cmakefile.unlink()

            # If the directory is empty, remove it
            if context.build_directory.parent.exists() and len(list(context.build_directory.parent.iterdir())) == 0:
                console.print_step(f"Removing empty build parent directory: {str(context.build_directory.parent)}")
                context.build_directory.parent.rmdir()

        else:
            if CMakeContext.resolveRootBuildDirectory(current_directory=clean_context.directory).exists():
                console.print_step(f"Removing build directory: {str(CMakeContext.resolveRootBuildDirectory(clean_context.directory))}")
                import shutil
                shutil.rmtree(CMakeContext.resolveRootBuildDirectory(clean_context.directory))
            
            
    def clean(self, clean_context: CleanContext):
        self.clean_project(clean_context=clean_context)