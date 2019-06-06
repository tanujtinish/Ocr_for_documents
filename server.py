from flask import Flask, request, Response, abort
import os
import calendar;
import time;
import cv2

import process_image_1
import process_image_2
import process_image_3
import pan
import passport
import aadhaar
import voter

app = Flask(__name__)


@app.route('/api/test', methods=['POST'])
def test():
	ts = calendar.timegm(time.gmtime())
	image_type= request.form["type"]
	image= request.files['image']
	file_name= str(image_type)+"_"+str(ts)+"."+image.filename.split('.')[1]
	image.save(os.path.join("./images", file_name))
	path1="./images/"+file_name
	process_image_1.process_image_1(path1)
	path2="./images/"+file_name.split('.')[0]+"_crop."+file_name.split('.')[1]
	process_image_2.process_image_2(path2)
	path3="./images/"+file_name.split('.')[0]+"_crop_rotated."+file_name.split('.')[1]
	
	if(image_type=="pan"):
		json_object=pan.pan_ocr(path3,"thresh","linear","gauss")
	elif(image_type=="passport"):
		json_object=passport.passport_ocr(path3,"thresh","linear","gauss")
	elif(image_type=="aadhaar"):
		json_object=aadhaar.aadhaar_ocr(path3,"thresh","linear","gauss")
	elif(image_type=="voter"):
		json_object=voter.voter_ocr(path3,"thresh","linear","gauss")

	return image_type


# start flask app
if __name__ == "__main__":
	app.run(port=8010)