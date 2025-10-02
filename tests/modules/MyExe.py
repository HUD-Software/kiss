from modules import KissProject, Description

@KissProject("mon_projet_toto")
@Description("C'est mon projet toto")
class TotoProject:
    def prebuild(self):
        print("Préparation du build pour TotoProject")
    def postbuild(self):
        print("Finalisation du build pour TotoProject")