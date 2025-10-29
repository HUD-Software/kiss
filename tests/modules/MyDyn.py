from modules import Dyn, Description

@Dyn("ma_dyn_tata")
@Description("C'est mon projet tata")
class DynProject:
    
    def prebuild(self):
        print("Préparation du build pour DynProject")
    def postbuild(self):
        print("Finalisation du build pour DynProject")