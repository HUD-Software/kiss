from modules import Lib, Description

@Lib("my_lib")
@Description("This is my lib")
class MyLib:

	# List all interface directories in the INTERFACES variable
	INTERFACES=["interface"]

	# List all source files in the SOURCES variable
	SOURCES=["src\lib.cpp"]

	# Run python code before compilation
	def prebuild(self):
		print("Préparation du build pour my_lib")

	# Run python code after compilation
	def postbuild(self):
		print("Finalisation du build pour my_lib")
