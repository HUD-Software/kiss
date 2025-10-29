from modules import Bin, Description

@Bin("mon_projet_toto")
@Description("C'est mon projet toto")
class MyBinProject:
    
    def prebuild(self):
        print("Préparation du build pour MyBinProject")
    def postbuild(self):
        print("Finalisation du build pour MyBinProject")