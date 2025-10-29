from modules import Bin, Description

@Bin("my_project")
@Description("This is my project")
class MyProject:
	src=["src/main.cpp"]
	def prebuild(self):
		print("Préparation du build pour my_project")

	def postbuild(self):
		print("Finalisation du build pour my_project")
