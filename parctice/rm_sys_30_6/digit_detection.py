import conv_deploy
import cv2
import time
import numpy as np

WHITE = (255,255,255)
BLACK = (0,0,0)

image_width = 640
image_height = 480

kernel2 = np.ones((2,2),np.uint8)
kernel3 = np.ones((3,3),np.uint8)

def get_digits(image):


	leftRect = []
	rightRect = []
	left_rect = []
	right_rect = []
	row_left_rect = []
	row_right_rect = []

	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	#blur = cv2.GaussianBlur(gray,(3,3),0)
	#blur = cv2.GaussianBlur(gray,(3,3),0)
	blurred = cv2.bilateralFilter(gray, 3, 119, 109)
	_,th3 = cv2.threshold(blurred,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
	edged = cv2.Canny(blurred, 180, 240)

	#cv2.imshow('',image)

	#cv2.waitKey(1)
	_, contours, hierarchy = cv2.findContours(edged.copy(),cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

	for contour in contours:
		peri = cv2.arcLength(contour,True)
		contour = cv2.approxPolyDP(contour, 0.0001 * peri, True)
		if cv2.contourArea(contour)<70 or cv2.contourArea(contour)>800:
			continue

		x,y,w,h = cv2.boundingRect(contour)

		if (w / h) < 0.9 or (w / h) > 2.5:
			continue
		#print cv2.contourArea(contour)
		cv2.drawContours(edged, [contour], -1, (255, 255, 255), 3)

		if x < (image_width//2):
			leftRect.append([x,y,w,h])
		else:
			rightRect.append([x,y,w,h])

	cv2.imshow('abc',edged)
	cv2.waitKey(1)
	for i in range(len(leftRect)):
		find_left = False
		xi,_,_,_ = leftRect[i]
		for j in range(len(leftRect)-i-1):
			j1=i+j+1
			xj1,_,_,_ = leftRect[j1]
			if abs(xi - xj1) < 10 :
				find_left = True
#				if (len(leftRect)-i-j-2) == 0 :
#					find_left = True 
#				for k in range(len(leftRect)-i-j-2):
#					k1=2+i+j+k
#					xk1,_,_,_ = leftRect[k1]
#					if abs(xk1 - xj1) < 15 :


		if find_left == True:
			left_rect.append(leftRect[i])


	for i in range(len(left_rect)):
		x1,y1,w1,h1 = left_rect[i]
		row_left_rect.append(y1)

	for i in range(len(rightRect)):
		find_right = False
		xi,_,_,_ = rightRect[i]
		for j in range(len(rightRect)-i-1):
			j1=i+j+1
			xj1,_,_,_ = rightRect[j1]
			if abs(xi - xj1) < 10:
				find_right = True
#				if (len(rightRect)-i-j-2) == 0 :
#					find_right = True 
#				for k in range(len(rightRect)-i-j-2):
#					k1=2+i+j+k
#					xk1,_,_,_ = rightRect[k1]
#					if abs(xk1 - xj1) < 15 :


		if find_right == True:
			right_rect.append(rightRect[i])

	for i in range(len(right_rect)):
		x2,y2,w2,h2 = right_rect[i]
		row_right_rect.append(y2)

	if len(row_left_rect) == 0 or len(row_right_rect) == 0:
		return [-1],[-1],[-1],[-1]

	tl_index = np.argmin(row_left_rect)
	bl_index = np.argmax(row_left_rect)
	tr_index = np.argmin(row_right_rect)
	br_index = np.argmax(row_right_rect)

	x1,y1,w1,h1=left_rect[tl_index]
	x2,y2,w2,h2=left_rect[bl_index]
	x3,y3,w3,h3=right_rect[tr_index]
	x4,y4,w4,h4=right_rect[br_index]

	sr_tl = [x1,y1]
	sr_bl = [x2,y2+h2]
	sr_tr = [x3+w3,y3]
	sr_br = [x4+w4,y4+h4]

	coord = [[x1,y1,w1,h1],[x2,y2,w2,h2],[x3,y3,w3,h3],[x4,y4,w4,h4]]

	pts1 = np.float32([sr_tl,sr_tr,sr_bl,sr_br])
	pts2 = np.float32([[0, 50],[300, 50],[0, 200],[300, 200]])
	M = cv2.getPerspectiveTransform(pts1,pts2)

	dst = cv2.warpPerspective(image,M,(300,200))
	cv2.imshow('aaa',dst)
	cv2.waitKey(1)

	""" 
	Handwritten
	"""
	digits_rect = [(51,54),(125,54),(200,54),(51,109),(125,109),(200,109),(51,163),(125,163),(200,163)]
	digit_imgs = []
	abc = 0
	for x,y in digits_rect:
		#cv2.rectangle(dst,(x,y),(x+50,y+34),(0,0,255),1)
		buf =  dst[y:y+32,x:x+50]
		buf = cv2.cvtColor(buf,cv2.COLOR_BGR2GRAY)
		_,buf = cv2.threshold(buf,20,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
		buf = cv2.erode(buf,kernel2,iterations = 1)
		buf = cv2.resize(buf,(24,24))
		buf = cv2.copyMakeBorder(buf, 2, 2, 2, 2, cv2.BORDER_CONSTANT, value=WHITE)
		#cv2.imshow('cv',buf)
		#cv2.waitKey(0)
		buf = 255 - buf
		buf = np.float32(buf) / 255.

		buf = buf.reshape([-1])
		digit_imgs.append(buf)

	handwritten_num_raw = conv_deploy.get_pred(digit_imgs)
	#print(handwritten_num_raw)

	handwritten_dict = {}

	# filter handwritten_num
	for i in range(len(handwritten_num_raw)):
		handwritten_dict[handwritten_num_raw[i]] = np.count_nonzero(handwritten_num_raw[i])

	if len(handwritten_dict) >= 9 :
		handwritten_num= handwritten_num_raw
		#print handwritten_num
	else:
		handwritten_num = [-1]
		pass
	#print handwritten_num


	""" 
	7segment
	"""

	digits_7seg_rect = [(100, 0), (121, 0), (142, 0), (162, 0), (183, 0)]

	digit_7seg_imgs = []

	for x,y in digits_7seg_rect:
		#cv2.rectangle(dst,(x,y),(x+19,y+33),(255,0,0),1)
		img_sevseg = dst[y:y+32,x:x+19]

		img_sevseg=cv2.cvtColor(img_sevseg, cv2.COLOR_BGR2HSV)
		img_sevseg_red = img_sevseg[:,:,2].copy()
		img_sevseg_red = cv2.morphologyEx(img_sevseg_red, cv2.MORPH_OPEN, kernel2)
		_,buf = cv2.threshold(img_sevseg_red,150,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
		buf = cv2.bitwise_not(buf)
		buf=cv2.dilate(buf,kernel2,iterations = 1)

		buf = cv2.resize(buf,(24,24))
		buf = cv2.copyMakeBorder(buf, 2, 2, 2, 2, cv2.BORDER_CONSTANT, value=WHITE)
		#cv2.imshow('bb',buf)
		#cv2.waitKey(0)
		buf = buf.reshape([-1])
		buf = 255 - buf
		buf = np.float32(buf) / 255.
		buf = buf.reshape([-1])
		digit_7seg_imgs.append(buf)

	scr_7seg_raw = conv_deploy.get_pred_7seg(digit_7seg_imgs)
	#print (scr_7seg_raw)

	""" 
	Flaming Digits
	"""

	flamingdigits_rect = [(61,54),(135,54),(210,54),(61,109),(135,109),(210,109),(61,163),(135,163),(210,163)]
	digit_imgs = []
	abc = 0
	for x,y in flamingdigits_rect:
		#cv2.rectangle(dst,(x,y),(x+30,y+32),(0,0,255),1)
		buf =  dst[y:y+32,x:x+30]
		img_FD = cv2.cvtColor(buf,cv2.COLOR_BGR2GRAY)
		_,buf = cv2.threshold(img_FD,200,255,cv2.THRESH_TOZERO+cv2.THRESH_OTSU)
		edged = cv2.Canny(buf, 255, 255)
		_, contours, hierarchy = cv2.findContours(edged.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
		cv2.drawContours(buf, contours, -1, 255,-1)
		buf = cv2.bitwise_not(buf)
		buf = cv2.resize(buf,(24,24))
		buf = cv2.copyMakeBorder(buf, 2, 2, 2, 2, cv2.BORDER_CONSTANT, value=WHITE)
		#cv2.imshow('cv',buf)
		#cv2.waitKey(0)
		buf = 255 - buf
		buf = np.float32(buf) / 255.
		buf = buf.reshape([-1])
		digit_imgs.append(buf)


	scr_FD_raw = conv_deploy.get_pred_flaming(digit_imgs)
	#print (scr_FD_raw)

	#filter flaming digit
	num_FD_dict = {}
	for i in range(len(scr_FD_raw)):
		num_FD_dict[scr_FD_raw[i]] = np.count_nonzero(scr_FD_raw[i])

	if len(num_FD_dict) >= 9 :
		Flaming_digit= scr_FD_raw
		#print scr_7seg
	else:
		Flaming_digit = [-1]
		pass
	#print(scr_FD)

	return coord, scr_7seg_raw, handwritten_num, Flaming_digit