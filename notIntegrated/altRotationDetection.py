# -*- coding: utf-8 -*-
"""
Created on Mon Nov 30 08:57:52 2020

@author: zefyr
"""

import cv2

cap = cv2.VideoCapture(0)

while(True):
    # Capture frame-by-frame
    _, frame = cap.read()
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    #_,img = cv2.threshold(frame, 128, 255, cv2.THRESH_BINARY)

    
    img = frame[120:360, 200:440]
    ret,thresh = cv2.threshold(img,127,255,0)
    contours,hierarchy = cv2.findContours(thresh, 1, 2)
    
    for cnt in contours:
        area = cv2.contourArea(cnt)
        
        # Find first contour of reasonable proportion to overall size of sub image
        if (area/(img.size) > 0.01) and  (area/(img.size) < 0.1):
    
            leftmost = cnt[cnt[:,:,0].argmin()][0]
            rightmost = cnt[cnt[:,:,0].argmax()][0]
            topmost = cnt[cnt[:,:,1].argmin()][0]
            bottommost = cnt[cnt[:,:,1].argmax()][0]
            
            # img = cv2.circle(img,tuple(leftmost), 10, (0,0,255), -1)
            # img = cv2.circle(img,tuple(rightmost), 10, (0,0,255), -1)
            # img = cv2.circle(img,tuple(topmost), 10, (0,0,255), -1)
            # img = cv2.circle(img,tuple(bottommost), 10, (0,0,255), -1)
            
            leftright_x = abs((rightmost - leftmost)[0])
            topbottom_y = abs((bottommost - topmost)[1])
            
            ratio = leftright_x/topbottom_y
            
            direction = 0
            # A horizontal to vertical ratio of about 0.48 corresponds with
            # a vertical arrow
            if ratio - 0.48 < 0.05: 
                # if span from bottom to arrow wings is longer than from arrow wings to
                # top, it's an up arrow
                if abs(bottommost[1] - leftmost[1]) > abs(leftmost[1] - topmost[1]):
                    direction = '^'
                else: direction = 'v'
                
            # A horizontal to vertical ratio of about 2.10 corresponds with
            # a horizontal arrow
            elif 1/ratio - 2.10 < 0.05:
                # if span from right to arrow wings is longer than from arrow wings to
                # left, it's a left arrow
                if abs(rightmost[0] - topmost[0]) > abs(topmost[0] - leftmost[0]):
                    direction = '<'
                else: direction = '>'
                
            # Any other ratio is unlikely to be a reasonable orientation of our arrow
            else:
                pass
            
            # if direction found, print stuff to screen
            if direction:
                frame = cv2.putText(frame, direction, (10,frame.shape[0]-10), cv2.FONT_HERSHEY_SIMPLEX,
                                    2, (255, 255, 255), 2)
                img = cv2.circle(img,tuple(leftmost), 10, (0,0,255), -1)
                img = cv2.circle(img,tuple(rightmost), 10, (0,0,255), -1)
                img = cv2.circle(img,tuple(topmost), 10, (0,0,255), -1)
                img = cv2.circle(img,tuple(bottommost), 10, (0,0,255), -1)
            break
    
    frame = cv2.flip(frame,1)
    # Display the resulting frame
    #cv2.imshow('img', img)
    cv2.imshow('frame', frame)
    cv2.imshow('frame', cv2.rectangle(frame,(200, 120), (440,360), (0,255,0),2))
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()