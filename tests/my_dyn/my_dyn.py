from modules import Dyn, Description

@Dyn("my_dyn")
@Description("This is my dyn")
class MyDyn:

	# List all interface directories in the INTERFACES variable
	INTERFACES=["interface"]

	# List all source files in the SOURCES variable
	SOURCES=["src\dyn.cpp"]

	# Run python code before compilation
	def prebuild(self):
		print("Préparation du build pour my_dyn")

	# Run python code after compilation
	def postbuild(self):
		print("Finalisation du build pour my_dyn")
