from modules import Bin, Description

@Bin("coucou")
@Description("Ceci est mon projet coucou")
class Coucou:
	src=["src/main.cpp"]
	def prebuild(self):
		print("Préparation du build pour coucou")

	def postbuild(self):
		print("Finalisation du build pour coucou")
