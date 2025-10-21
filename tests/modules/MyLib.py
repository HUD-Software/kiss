from modules import KissProject, Description

LIB_NAME = "ma_lib_jiji"

@KissProject(LIB_NAME)
@Description("C'est ma library Jiji")
class JijiProject:
    def prebuild(self):
        print(f"Préparation du build pour {LIB_NAME}")
    def postbuild(self):
        print(f"Finalisation du build pour {LIB_NAME}")