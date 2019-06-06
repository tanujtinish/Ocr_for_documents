from PIL import Image
import pytesseract
import argparse
import cv2
import os
import re
import io
import json
import ftfy


def voter_ocr(path,thresh,rescale,average):
	image = cv2.imread(path)
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


	if thresh == "thresh":
	    gray = cv2.threshold(gray, 0, 255,cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
	elif thresh == "adaptive":
	    gray = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 2)


	if rescale == "linear":
	    gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)
	elif rescale == "cubic":
	    gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)


	if average == "blur":
	    gray = cv2.medianBlur(gray, 3)
	elif average == "bilateral":
	    gray = cv2.bilateralFilter(gray, 9, 75, 75)
	elif average == "gauss":
	    gray = cv2.GaussianBlur(gray, (5,5), 0)

	cv2.imwrite("."+path.split('.')[1]+"_gray"+"."+path.split('.')[2],gray)
	text = pytesseract.image_to_string(gray)
	print(text)

	name = None
	fname = None
	dob = None
	pan = None
	nameline = []
	dobline = []
	panline = []
	text0 = []
	text1 = []


	lines = text.split('\n')
	for lin in lines:
		lin = lin.encode('ascii', 'ignore')
		s = lin.strip()
		s = lin.replace('\n','')
		s = s.rstrip()
		s = s.lstrip()
		print("index",s.find(" !\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"))
		s = s[re.search("[^A-Za-z0-9]", s).end():]
		text1.append(s)

	text1 = list(filter(None, text1))
	print("text1",text1)

	lineno = -1

	for wordline in text1:
		xx = wordline.split(' ')
		if ([w for w in xx if re.search('(IDENTITY|CARD|CAPD|CAPO|IOENTITY|TITY|TITT)', w)]):
			text1 = list(text1)
			lineno = text1.index(wordline)
			break

	text0 = text1[lineno+1:]
	print(text0)

	data=pre_cleaning(text0)
	print("hey",data,text0)

	return data

def pre_cleaning(text0):
	try:
		# Cleaning first names, better accuracy
		name = text0[2]
		name = name.rstrip()
		name = name.lstrip()
		name = name.replace("8", "B")
		name = name.replace("0", "D")
		name = name.replace("6", "G")
		name = name.replace("1", "I")
		name = re.sub('[^a-zA-Z] +', ' ', name)
		print("name",name)

		# Cleaning Father's name
		fname = text0[4]
		fname = fname.rstrip()
		fname = fname.lstrip()
		fname = fname.replace("8", "S")
		fname = fname.replace("0", "O")
		fname = fname.replace("6", "G")
		fname = fname.replace("1", "I")
		fname = fname.replace("\"", "A")
		fname = re.sub('[^a-zA-Z] +', ' ', fname)

		# Cleaning DOB
		dob = text0[4]
		dob = dob.rstrip()
		dob = dob.lstrip()
		dob = dob.replace('l', '/')
		dob = dob.replace('L', '/')
		dob = dob.replace('I', '/')
		dob = dob.replace('i', '/')
		dob = dob.replace('|', '/')
		dob = dob.replace('\"', '/1')
		dob = dob.replace(" ", "")

		# Cleaning PAN Card details
		pan = text0[0]
		pan = pan.rstrip()
		pan = pan.lstrip()
		pan = pan.replace(" ", "")
		pan = pan.replace("\"", "")
		pan = pan.replace(";", "")
		pan = pan.replace("%", "L")

	except:
		pass

	# Making tuples of data
	data = {}
	data['Name'] = str(name)
	data['Father Name'] = str(fname)
	data['Date of Birth'] = str(dob)
	data['PAN'] = str(pan)

	return data

def findword(textlist, wordstring):
	lineno = -1
	for wordline in textlist:
		xx = wordline.split( )
		if ([w for w in xx if re.search(wordstring, w)]):
			lineno = textlist.index(wordline)
			textlist = textlist[lineno+1:]
			print(lineno)
			return textlist
	print(lineno)
	return textlist