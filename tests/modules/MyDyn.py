from modules import Dyn, Description

@Dyn("ma_dyn_tata")
@Description("C'est mon projet tata")
class MyDynProject:
    
    def prebuild(self):
        print("Préparation du build pour MyDynProject")
    def postbuild(self):
        print("Finalisation du build pour MyDynProject")