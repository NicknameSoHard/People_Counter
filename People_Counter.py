## author HydroslidE
import numpy as np
import cv2
from time import time
from datetime import datetime.now
import Person

###############
## Function ##
##############
# Write log for 1C.
def Save_log(direction, date_now):
    try:
        if direction == "up": # Direction
            direct = ["1","2"]
        else:
            direct = ["1","1"]
#        date_now = datetime.now()
        ms_now = str(int(time.time() / 1000)) # time in ms
        log_file = open(date_now.strftime("%d%m%y%H") + ".txt", "a") # Filename
        log_file.write( date_now.strftime("%d.%m.%Y") + "|" + ms_now + "|" + direct[0] + "|" + direct[1] + "|PCCapture|"+"0" + "|\n")
        log_file.close();
        return True
    except:
        return False

def nothing(x): # Trackpad function
    pass # nothing to do

##########
## Main ##
##########
# Exit counters
cnt_up   = 0
cnt_down = 0

# Catch video
cap = cv2.VideoCapture("http://192.168.1.35//video.cgi")
if not cap.isOpened():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print( "Video Capture error: Can't find camera.")

# Load setting
setting = []
try:
    setting_file = open("Setting", "r")
    for line in setting_file:
        setting.append(int(line))
    setting_file.close()
    if(len(setting) != 5 or min(setting) <= 0): # Raise exeption
        raise
    print("Load setting from file")
except:
    setting = [30, 215, 252, 288, 192]
    print("Load default setting")

"""
Memo for settings:
setting[0] - min threshold
setting[1] - min object
setting[2] - max object
setting[3] - down line
setting[4] - top line
setting[5] - visible_frame # In this version of program is off
"""
# take frame width and height
frame_width = cap.get(3)
frame_height = cap.get(4)
res = (frame_height * frame_width)
# Calculate the min and max size of the object
min_areaTH = res / 40
print ('Min area Threshold', min_areaTH)
max_areaTH = res / 3
print ('Max area Threshold', max_areaTH)

# Calculate program setting
# Build line on 3\5 screen
line_down = int(3 * (frame_height / 5))
print ("Red line coord y:", str(line_down))
# Calculate coordinate extreme points
pt1 =  [0, line_down];
pt2 =  [frame_width, line_down];
# Build and transform matrix
pts_L1 = np.array([pt1, pt2], np.int32)
pts_L1 = pts_L1.reshape((-1, 1, 2))
line_down_color = (255, 0, 0)

# Build line on 2\5 screen
line_up = int(2*(frame_height / 5))
print ("Blue line coord y:", str(line_up))
pt3 =  [0, line_up];
pt4 =  [frame_width, line_up];
pts_L2 = np.array([pt3, pt4], np.int32)
pts_L2 = pts_L2.reshape((-1, 1, 2))
line_up_color = (0, 0, 255)

# Create new array with 8-bit unsigned integer for morphological filters
kernelOp = np.ones((3,3),np.uint8)
kernelOp2 = np.ones((5,5),np.uint8)
kernelCl = np.ones((11,11),np.uint8)

# Make Hershey Fonts
font = cv2.FONT_HERSHEY_SIMPLEX
# Create panel and trackpads
Panel = np.zeros([1,256], np.uint8)
cv2.namedWindow("Panel")

cv2.createTrackbar("THRSH_MIN", "Panel", setting[0], 255, nothing)
cv2.createTrackbar("MIN OBJ", "Panel", setting[1], 255, nothing)
cv2.createTrackbar("MAX OBJ", "Panel", setting[2], 255, nothing)
cv2.createTrackbar("DWN_LINE", "Panel", setting[3], int(frame_height), nothing)
cv2.createTrackbar("TOP_LINE", "Panel", setting[4], int(frame_height), nothing)
#cv2.createTrackbar("VISIBLE_FRAME", "Panel", setting[5], 1, nothing)
#cv2.resizeWindow("Panel", int(frame_height)+15, -5)
# Makes array for detector
persons = []
iteration_counter = 0
now_setting = [1,1,1,1,1]

# Get mask
ret, mask_frame = cap.read()
while(cap.isOpened()):
    # Get frame
    ret, frame = cap.read()
    # Calculates the absolute difference between mask and frame frames(arrays).
    frame_ABS =  cv2.absdiff(frame, mask_frame)
#    cv2.imshow('ADS',frame_ABS)
    # Converts an image to gray color space.
    gray_frame = cv2.cvtColor(frame_ABS, cv2.COLOR_BGR2GRAY)

    cv2.imshow("Panel", Panel)

    now_setting[0] = cv2.getTrackbarPos("THRSH_MIN", "Panel")
    now_setting[1] = cv2.getTrackbarPos("MIN OBJ", "Panel")
    now_setting[2] = cv2.getTrackbarPos("MAX OBJ", "Panel")
    now_setting[3] = cv2.getTrackbarPos("DWN_LINE", "Panel")
    now_setting[4] = cv2.getTrackbarPos("TOP_LINE", "Panel")
#    now_setting[5] = cv2.getTrackbarPos("VISIBLE_FRAME", "Panel")

    # if position trackbars not equal setting change and save setting
    if not np.array_equal(now_setting, setting):
        for i in range(0,5):
            setting[i] = now_setting[i]

        # Recalculate setting
        min_areaTH = res / (255-setting[1]+1)
        max_areaTH = res / (255-setting[2]+1)

        # If setting line position change, recalculate and her
        if (line_down != int(setting[3])):
            line_down = int(setting[3])
            print("Red line y:", str(line_down))
            pt1 = [0, line_down];
            pt2 = [frame_width, line_down];
            pts_L1 = np.array([pt1, pt2], np.int32)
            pts_L1 = pts_L1.reshape((-1, 1, 2))
            line_down_color = (255, 0, 0)

        if (line_up != int(setting[4])):
            line_up = int(setting[4])
            print("Blue line y:", str(line_up))
            pt3 = [0, line_up];
            pt4 = [frame_width, line_up];
            pts_L2 = np.array([pt3, pt4], np.int32)
            pts_L2 = pts_L2.reshape((-1, 1, 2))
            line_up_color = (0, 0, 255)

        # Save setting on file
        setting_file = open("Setting", "w")
        setting_file.write(str(setting[0]) +  "\n" + str(setting[1]) + "\n" + str(setting[2]) + "\n" + str(setting[3]) + "\n" + str(setting[4]))
        setting_file.close();
        print("Saved in file")

    try:
        # Binarize the difference frame (Change color space to black and white)
        ret,imBin= cv2.threshold(gray_frame, setting[0], 255, cv2.THRESH_BINARY)
#        cv2.imshow('threshold',imBin)
        # Morphology transformation (open and close). Just filter the noise in the image.
        morphology_mask = cv2.morphologyEx(imBin, cv2.MORPH_OPEN, kernelOp)
        morphology_mask =  cv2.morphologyEx(morphology_mask , cv2.MORPH_CLOSE, kernelCl)
        cv2.imshow('morphologyEx', morphology_mask )
    except:
        # All exceptions end the program.
        print('Error threshold or morphology. End of programm.')
        print ('UP:',cnt_up)
        print ('DOWN:',cnt_down )
        break

        # Find countours on image
    ___, contours0, ___ = cv2.findContours(morphology_mask,
        cv2.RETR_EXTERNAL, # Retrieves only the extreme outer contours
        cv2.CHAIN_APPROX_SIMPLE # Extracts only edge points of contours
    )

    # For all countours
    for cnt in contours0:
        # Calculate size of countour
        area = cv2.contourArea(cnt)
        # Сheck cameras on noise
        print(area, (frame_width * frame_height))
        if area > (frame_width * frame_height) * 0.90:
            iteration_counter = 1000
        if area > min_areaTH and area < max_areaTH:
            # Image moments help you to calculate some features like center of mass of the object. We calculate it.
            M = cv2.moments(cnt)
            # Get coordinates of the edges
            cx = int(M['m10']/M['m00'])
            cy = int(M['m01']/M['m00'])
            # Get the coordinates of the scope
            x,y,w,h = cv2.boundingRect(cnt)
            # Check for a new object
            new = True
            for i in persons:
                # If the object is close to already detected
                if abs(cx-i.getX()) <= w and abs(cy-i.getY()) <= h:
                    #print("Not new obj")
                    new = False
                    # Update coordinates for better tracking
                    i.updateCoords(cx,cy)

                    date_now = datetime.now()
                    # Check cross the line
                    if i.going_UP(line_down, line_up) == True:
                        cnt_up += 1;
                        # Write log to console and file
                        print ("Person crossed going up at", str(date_now.strftime("%d.%m.%Y")) )
                        if not Save_log("up", date_now):
                            print("Logfile save error")
                        break

                    elif i.going_DOWN(line_down, line_up) == True:
                        cnt_down += 1;
                        print ("Person crossed going down at", str(date_now.strftime("%d.%m.%Y")) )
                        if not Save_log("down", date_now):
                            print("Logfile save error")
                        break
                else:
                    print("New obj")
                # delete object if work done
                if i.timedOut():
                    index = persons.index(i)
                    persons.pop(index)
                    del i

            # Create new object
            if new == True:
                p = Person.MyPerson(cx, cy)
                persons.append(p)

            # Draw red dot in a middle object, and make scope.
            cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)
            cv2.rectangle(frame, (x, y),(x + w, y + h), (0, 255, 0), 2)
            # cv2.drawContours(frame, cnt, -1, (0, 255, 0), 3) # And we can draw all object countours
            iteration_counter = 0
        else:
            # Count frames without tracking objects
            iteration_counter +=1;
            #print("Strange object!" + str(iteration_counter))
            # If we had a lot of frames without tracking object, we update mask and tracking array
            if iteration_counter > 1000:
                ret, mask_frame = cap.read()
                iteration_counter = 0
                persons = []
            print(iteration_counter)
    # Draw lines and text on frames
    str_up = 'UP: '+ str(cnt_up)
    str_down = 'DOWN: '+ str(cnt_down)
    frame = cv2.polylines(frame,[pts_L1], False, line_down_color, thickness = 2)
    frame = cv2.polylines(frame,[pts_L2], False, line_up_color,thickness = 2)

    cv2.putText(frame, str_up, (10, 40), font, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(frame, str_up, (10, 40),font, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
    cv2.putText(frame, str_down, (10, 90), font, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(frame, str_down, (10, 90), font, 0.5, (255, 0, 0), 1, cv2.LINE_AA)

    # Show final frame
    #cv2.imshow('Frame',frame)
    cv2.imshow('Frame',frame)

    # Checking the key press
    k = cv2.waitKey(30) & 0xff
    # if ESC - end program
    if k == 27:
        break
    # If SPACE, we update mask and reset exit counters
    elif k == 32:
        ret, mask_frame = cap.read()
        cnt_up = 0
        cnt_down = 0

# Close camera and all windows
cap.release()
cv2.destroyAllWindows()
