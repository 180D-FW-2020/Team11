'''
Developed code using:
        https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_colorspaces/py_colorspaces.html
        https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_canny/py_canny.html#canny
	https://docs.opencv.org/3.4/d7/d1d/tutorial_hull.html
'''

import numpy as np
import cv2
import random as rng

cap = cv2.VideoCapture(0)

while(True):
	# Capture frame-by-frame
	ret, frame = cap.read()
	arrow = cv2.imread('arrow.jpeg',0)

	# Our operations on the frame come here
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	edges = cv2.Canny(gray,100,200)

	# Find contours
	contours, hierarchy = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

	# Find the convex hull object for each contour
	hull_list = []
	for i in range(len(contours)):
		hull = cv2.convexHull(contours[i])
		hull_list.append(hull)

	# Draw contours + hull results
	drawing = np.zeros((edges.shape[0], edges.shape[1], 3), dtype=np.uint8)
	for i in range(len(contours)):
		color = (rng.randint(0,256), rng.randint(0,256), rng.randint(0,256))
		cv2.drawContours(drawing, contours, i, color)
		cv2.drawContours(drawing, hull_list, i, color)


	# Display the resulting frame
	cv2.imshow('frame', gray)
	cv2.imshow('edges', edges)
	cv2.imshow('Contours', drawing)
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
