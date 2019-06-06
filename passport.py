from PIL import Image
import pytesseract
import argparse
import cv2
import os
import re
import io
import json
import ftfy



def passport_ocr(path,thresh,rescale,average):
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
	text = pytesseract.image_to_string(gray, lang = 'eng')


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
		s = lin.strip()
		s = lin.replace('\n','')
		s = s.rstrip()
		s = s.lstrip()
		text1.append(s)

	text1 = list(filter(None, text1))


	lineno = -1

	for wordline in text1:
		xx = wordline.split(' ')
		if ([w for w in xx if re.search('(INCOMETAXDEPARWENT @|mcommx|INCOME|TAX|GOW|GOVT|GOVERNMENT|OVERNMENT|VERNMENT|DEPARTMENT|EPARTMENT|PARTMENT|ARTMENT|INDIA|NDIA)$', w)]):
			text1 = list(text1)
			lineno = text1.index(wordline)
			break

	text0 = text1[lineno+1:]

	for wordline in text0:
		wordline=str(wordline)
		xx = wordline.split(' ')
		for w in xx:
			print("ii",w)
			if re.search('(Pormanam|Number|umber|Account|ccount|count|Permanent|ermanent|manent|wumm)', w):
				lineno = text0.index(wordline)
				break
	if(lineno==0):
		pat=0
	else:
		pat=1
	data=pre_cleaning(text0,pat)
	print("hey",data,text0,pat,lineno)

	return data

def pre_cleaning(text0,pat):
	try:
		# Cleaning first names, better accuracy
		if(pat==0):
			name = text0[3]
			name = name.rstrip()
			name = name.lstrip()
			name = name.replace("8", "B")
			name = name.replace("0", "D")
			name = name.replace("6", "G")
			name = name.replace("1", "I")
			name = re.sub('[^a-zA-Z] +', ' ', name)
			print("name",name)
		else:
			name = text0[0]
			name = name.rstrip()
			name = name.lstrip()
			name = name.replace("8", "B")
			name = name.replace("0", "D")
			name = name.replace("6", "G")
			name = name.replace("1", "I")
			name = re.sub('[^a-zA-Z] +', ' ', name)
			print("name",name)

		# Cleaning Father's name
		if(pat==0):
			fname = text0[5]
			fname = fname.rstrip()
			fname = fname.lstrip()
			fname = fname.replace("8", "S")
			fname = fname.replace("0", "O")
			fname = fname.replace("6", "G")
			fname = fname.replace("1", "I")
			fname = fname.replace("\"", "A")
			fname = re.sub('[^a-zA-Z] +', ' ', fname)
		else:
			fname = text0[1]
			fname = fname.rstrip()
			fname = fname.lstrip()
			fname = fname.replace("8", "S")
			fname = fname.replace("0", "O")
			fname = fname.replace("6", "G")
			fname = fname.replace("1", "I")
			fname = fname.replace("\"", "A")
			fname = re.sub('[^a-zA-Z] +', ' ', fname)

		# Cleaning DOB
		if(pat==0):
			dob = text0[7]
			dob = dob.rstrip()
			dob = dob.lstrip()
			dob = dob.replace('l', '/')
			dob = dob.replace('L', '/')
			dob = dob.replace('I', '/')
			dob = dob.replace('i', '/')
			dob = dob.replace('|', '/')
			dob = dob.replace('\"', '/1')
			dob = dob.replace(" ", "")
		else:
			dob = text0[2]
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
		text0 = findword(text0, '(Pormanam|Number|umber|Account|ccount|count|Permanent|ermanent|manent|wumm)')
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