from generator import GeneratorRegistry
from kiss_parser import KissParser
from platform_target import SupportedTarget

@GeneratorRegistry.register("cmake", "Generate cmake CMakeLists.txt")
class GeneratorCMake:
     
    @classmethod
    def add_cli_argument_to_parser(cls, parser: KissParser):
        parser.add_argument("-p", "--project", help="name of the project.py to generate", dest="project_name", required=False)
        parser.add_argument("-t", "--target", help="specify the target platform", dest="platform_target", default=SupportedTarget.default_target(), required=False)
        parser.add_argument("-cov", "--coverage", help="enable code coverage", action='store_const', const=True)
        parser.add_argument("-san", "--sanitizer", help="enable sanitizer", action='store_const', const=True)


