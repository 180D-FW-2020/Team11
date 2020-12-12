'''
Developed code using:
    https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_colorspaces/py_colorspaces.html
    https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_canny/py_canny.html#canny
'''

import numpy as np
import cv2

cap = cv2.VideoCapture(0)

while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()
    arrow = cv2.imread('arrow.jpeg',0)

    # Our operations on the frame come here
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray,100,200)
    
    bound = int((gray.shape[1] - gray.shape[0])/2)
    scale_percent = 60 # percent of original size
    gray = gray[:, bound:gray.shape[1] - bound]
    width = int(400)
    height = int(400)
    dim = (width, height)

    # Display the resulting frame
    resized = cv2.resize(gray, dim, interpolation = cv2.INTER_AREA)
    cv2.imshow('frame', resized)
    cv2.imshow('edges', edges)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
