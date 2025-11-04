from modules import Bin, Description

@Bin("new_project")
@Description("This is the new_project")
class NewProject:
	src=["src/main.cpp"]
	def prebuild(self):
		print("Préparation du build pour new_project")

	def postbuild(self):
		print("Finalisation du build pour new_project")
