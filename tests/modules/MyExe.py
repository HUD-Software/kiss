from modules import Bin, Description

@Bin("mon_projet_toto")
@Description("C'est mon projet toto")
class BinProject:
    
    def prebuild(self):
        print("Préparation du build pour BinProject")
    def postbuild(self):
        print("Finalisation du build pour BinProject")