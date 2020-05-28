# Manage HDR Image with EXR import from Mitsuba

import OpenEXR, Imath, array
import numpy as np
from PIL import Image, ImageQt
import math

verbose = False


# Load EXR file
# Return size of the image and [R,G,B], Depth and AO PIL image 
def loadEXR(filename):
	# Load EXR file
	file = OpenEXR.InputFile(filename)
	pt = Imath.PixelType(Imath.PixelType.FLOAT)

	if verbose:
		print("Channels : " + str(file.header()['channels']))

	# Get Header
	dw = file.header()['dataWindow']
	size = (dw.max.x - dw.min.x + 1, dw.max.y - dw.min.y + 1)
	
	# Get RGB Layers, Distance Layer and AO Layer
	rgbf = [Image.frombytes("F", size, file.channel(c, pt)) for c in ["color.R","color.G","color.B"]]
	df = Image.frombytes("F", size, file.channel("distance.Y", pt))
	aof = Image.frombytes("F", size, file.channel("ao.Y", pt))

	return size, rgbf, df, aof


# Return a RGB PIL Image [0;255]
def getRGB8Image(rgbf, dark, light):

	scale = 255 / (light - dark)
		
	def normalize_0_255(v):
		return (v  * scale) + dark * 255
	
	rgb8 = [im.point(normalize_0_255).convert("L") for im in rgbf]

	return Image.merge("RGB", rgb8) 


# Return a depth PIL Image [0;255]
def getD8Image(df, state, distMin, distMax):

	if not(state) :
		# Automatic computation
		extrema = df.getextrema()
		distMax = max(extrema)
		distMin = min(extrema)

	np_df = np.array(df)
	np_df = np.clip(np_df, distMin, distMax)

	np_df = np_df / distMax
	
	np_df = - np.power( np_df , 1.5)
	np_df = 1.0 - np.exp( np_df )

	np_df = np_df * 255.

	return Image.fromarray(np_df).convert("L")


# Return an AO PIL Image [0;255]
def getAO8Image(aof, state, scl):

	maxAO = max(aof.getextrema())
	minAO = min(aof.getextrema())
	
	scaleLocal = 1.
	if state:
		scaleLocal = scl

	scaleAO = 255 * scaleLocal / (maxAO - minAO)

	def normalize_ao(v):
		return (v * scaleAO)  + minAO

	return aof.point(normalize_ao).convert("L")


def getFinalImage(rgbf, stateD, df, distMin, distMax, stateAO, aof, aoScl):
	
	# Get layers
	np_R = np.array(rgbf[0])
	np_G = np.array(rgbf[1])
	np_B = np.array(rgbf[2])

	# Add Ambient Occlusion
	if stateAO :
		np_AO = np.array(aof)
		np_R = np_R - ( 1. - np_AO)*aoScl
		np_G = np_G - ( 1. - np_AO)*aoScl
		np_B = np_B - ( 1. - np_AO)*aoScl
		
	# Add Fog
	if stateD :
		np_D = np.array(df)
		np_D = np.clip(np_D, distMin, distMax)
		
		np_D = np_D / distMax
				
		np_D = np.power( np_D, 1.5)
		np_D = 1.0 - np.exp( - np_D )

		np_ColorR = np.copy(np_D)
		np_ColorG = np.copy(np_D)
		np_ColorB = np.copy(np_D)
		
		np_ColorR.fill(0.4) 
		np_ColorG.fill(0.65)
		np_ColorB.fill(1.0) 

		np_ColorR = np_ColorR * 0.65 
		np_ColorG = np_ColorG * 0.65 
		np_ColorB = np_ColorB * 0.65 

		np_R = np_ColorR * np_D + (1. - np_D) * np_R
		np_G = np_ColorG * np_D + (1. - np_D) * np_G
		np_B = np_ColorB * np_D + (1. - np_D) * np_B

	final = [Image.fromarray(np_R),Image.fromarray(np_G),Image.fromarray(np_B)]

	return final


def exrtojpg_all(exrfile, rgbfile, distfile, aofile, finalfile):
	# Load EXR file
	size, rgbf, df, aof = loadEXR(exrfile)

	# Get RGB Layers
	colMin = 0.2
	colMax = 0.8
	image_rgb8 = getRGB8Image(rgbf,colMin, colMax)
	image_rgb8.save(rgbfile)
	
	# Get Distance Layer
	distMin = 0.
	distMax = 3000.
	image_d8 = getD8Image(df, True, distMin, distMax)
	image_d8.save(distfile)
	
	# Get AO Layer
	aoScale = 0.2
	image_ao8 = getAO8Image(aof, True, 1.0)
	image_ao8.save(aofile)
	
	# Get Composition
	image_finalf = getFinalImage(rgbf, True, df, distMin, distMax, True, aof, aoScale)
	image_final8 = getRGB8Image(image_finalf, colMin, colMax)
	image_final8.save(finalfile)

	#pixdata_rgb8 = image_rgb8.load()	
	#pixdata_d8   = image_d8.load()
	#pixdata_ao8  = image_ao8.load()
	#
	## HSV color
	#image_hsv8 = image_rgb8.convert("HSV")
	#pixdata_hsv8 = image_hsv8.load()
	#for y in range(image_rgb8.size[1]):
	#	for x in range(image_rgb8.size[0]):
	#		colDist = pixdata_d8[x,y]
	#		H = pixdata_hsv8[x,y][0]
	#		S = int( pixdata_hsv8[x,y][1] + colDist)
	#		V = pixdata_hsv8[x,y][2]
	#		pixdata_hsv8[x,y] = (H,S,V)
	#
	#image_rgb8 = image_hsv8.convert("RGB")
	#image_rgb8.save("../data/plop.jpg")
	#
	#for y in range(image_rgb8.size[1]):
	#	for x in range(image_rgb8.size[0]):
	#		colAO = int((255-pixdata_ao8[x,y])/8.)
	#		R = pixdata_rgb8[x, y][0] #+ colDist #- colAO
	#		G = pixdata_rgb8[x, y][1] #+ colDist #- colAO
	#		B = pixdata_rgb8[x, y][2] #+ colDist #- colAO
	#		pixdata_rgb8[x, y] = (R,G,B)
	#
	#image_rgb8.save(compfile)
	#image_rgb8.show()

	
def exrtojpg(exrfile, finalfile, colMin, colMax, distMin, distMax, aoScale):

	# Load EXR file
	size, rgbf, df, aof = loadEXR(exrfile)
	
	# Get Composition
	image_finalf = getFinalImage(rgbf, True, df, distMin, distMax, True, aof, aoScale)
	image_final8 = getRGB8Image(image_finalf, colMin, colMax)
	image_final8.save(finalfile)

def exrtojpg_default(exrfile, finalfile):
	
	# Parameters
	colMin = 0.2
	colMax = 0.8
	distMin = 0.
	distMax = 3000.
	aoScale = 0.2

	exrtojpg(exrfile, finalfile, colMin, colMax, distMin, distMax, aoScale)

def exrtojpg_tonemap(exrfile, finalfile):
	subprocess.run(["mtsutil", 'tonemap','-o',finalfile,exrfile])
	
# Example

# exrtojpg_all("../data/output_rgb_ao_dist.exr", "../data/resultat-color.jpg", "../data/resultat-dist.jpg", "../data/resultat-ao.jpg", "../data/resultat-comp.jpg")
# exrtojpg_default("../data/output_rgb_ao_dist.exr", "../data/resultat-comp.jpg")
# exrtojpg("../data/output_rgb_ao_dist.exr", "../data/resultat-comp.jpg", 0.2, 0.8, 0., 3000., 0.2)