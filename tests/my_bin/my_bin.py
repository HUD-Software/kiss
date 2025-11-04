from modules import Bin, Description

@Bin("my_bin")
@Description("This is my bin")
class MyBin:

	# List all source files in the SOURCES variable
	SOURCES=["src\main.cpp"]

	# Run python code before compilation
	def prebuild(self):
		print("Préparation du build pour my_bin")

	# Run python code after compilation
	def postbuild(self):
		print("Finalisation du build pour my_bin")
