from modules import Lib, Description

LIB_NAME = "ma_lib_jiji"

@Lib(LIB_NAME)
@Description("C'est ma library Jiji")
class MyLibProject:
    def prebuild(self):
        print(f"Préparation du build pour {LIB_NAME}")
