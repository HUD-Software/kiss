from modules import Lib, Description, ProjectType

LIB_NAME = "ma_lib_jiji"

@Lib(LIB_NAME)
@Description("C'est ma library Jiji")
class JijiProject:
    def prebuild(self):
        print(f"Préparation du build pour {LIB_NAME}")
