import cv2
import cv2.aruco as aruco
import keyboard
from time import sleep,time

class frame_converter(object):

	def __init__(self,width=0,height=0,Xpercentage=0,Ypercentage=0):
		self.width = width
		self.height = height
		self.Xpercentage = Xpercentage
		self.Ypercentage = Ypercentage
		self.coordinate = []

	def convert(self):
		
		pointXY1 = (round(self.Xpercentage*self.width/100),round(self.Ypercentage*self.height/100))
		
		self.coordinate.append((pointXY1[0],0))
		self.coordinate.append((self.width-pointXY1[0],0))
		self.coordinate.append((self.width,pointXY1[1]))
		self.coordinate.append((self.width,self.height-pointXY1[1]))
		self.coordinate.append((self.width-pointXY1[0],self.height))
		self.coordinate.append((pointXY1[0],self.height))
		self.coordinate.append((0,self.height-pointXY1[1]))
		self.coordinate.append((0,pointXY1[1]))
		return self.coordinate


video_width = 640
video_height = 480

directional_percentage_area = 45
action_percentage_area = 45
fc = frame_converter(video_width,video_height,directional_percentage_area,action_percentage_area)
loc = fc.convert()
print(loc)
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT,video_height)
cap.set(cv2.CAP_PROP_FRAME_WIDTH,video_width)
control_left = False
control_right = False
control_jump = False
control_sleding = False

debug=""
lastkey = 'p'

aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_250)
parameters =  aruco.DetectorParameters_create()
	
thres_x_left = loc[0][0]
thres_x_right = loc[1][0]
thres_y_up = loc[2][1]
thres_y_down = loc[3][1]

while(True):

	# Capture frame-by-frame
	ret, frame = cap.read()
	center_x = -1
	center_y = -1

	# Our operations on the frame come here
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

 
	'''	   detectMarkers(...)
		detectMarkers(image, dictionary[, corners[, ids[, parameters[, rejectedI
		mgPoints]]]]) -> corners, ids, rejectedImgPoints
		'''
		#lists of ids and the corners beloning to each id
	corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)
	if ids is not None:
		if ids[0][0] == 203:
			for corner in corners[0][0]:
				center_x += corner[0]
				center_y += corner[1]
			center_x/=4
			center_y/=4			
			print(center_x,center_y)
	
	cv2.line(frame,loc[0],loc[5],(255,255,0),2) #limiter kiri
	cv2.line(frame,loc[1],loc[4],(255,0,0),2) #limiter kanan
	cv2.line(frame,loc[2],loc[7],(255,255,255),2) #limiter atas
	cv2.line(frame,loc[3],loc[6],(0,255,0),2) #limiter bawah
	
	if center_x < thres_x_left and center_x >0 :
		debug = "Left"
		if lastkey != 'd':
			keyboard.release(lastkey)
			lastkey = 'd'
			keyboard.press(lastkey)
	elif center_x > thres_x_right and center_x >0:
		debug = "Right"
		if lastkey != 'a':
			keyboard.release(lastkey)
			lastkey = 'a'
			keyboard.press(lastkey)
	elif center_y < thres_y_up and center_y > 0:
		debug = "Jump"
		if lastkey != 'w':
			keyboard.release(lastkey)
			lastkey = 'w'
			keyboard.press(lastkey)  	
	elif center_y > thres_y_down and center_y > 0:
		debug = "Slide"
		if lastkey != 's':
			keyboard.release(lastkey)
			lastkey = 's'
			keyboard.press(lastkey)	
	else:
		keyboard.release(lastkey)
		lastkey = 'p'
		
	cv2.putText(frame,debug,(10,20), cv2.FONT_HERSHEY_SIMPLEX, 1,(255,255,255),2,cv2.LINE_AA)
	frame = aruco.drawDetectedMarkers(frame, corners)

	# Display the resulting frame
	cv2.imshow('frame',frame)
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break


# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
