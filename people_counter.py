import datetime

import cv2
import numpy


from base_camera import Camera
from person import MyPerson
from settingsdict import SettingsDict


class PeopleCounter:
    def __init__(self):
        self.cnt_up = 0
        self.cnt_down = 0

        cam_string = 0  # "http://192.168.1.35//video.cgi"
        # Catch video
        self.cap = Camera(cam_string)
        # Load settings
        self.setting = SettingsDict()

        # take frame width and height
        self.cam_characteristic = self.cap.get_camera_settings()
        self.res = self.cam_characteristic['frame_height'] * self.cam_characteristic['frame_width']
        # Calculate the min and max size of the object
        self.min_areaTH = self.res / 40
        self.max_areaTH = self.res / 3

        cv2.namedWindow("Panel")

        cv2.createTrackbar("THRSH_MIN", "Panel", self.setting['THRSH_MIN'], 255, self.nothing)
        cv2.createTrackbar("MIN_OBJ", "Panel", self.setting['MIN_OBJ'], 255, self.nothing)
        cv2.createTrackbar("MAX_OBJ", "Panel", self.setting['MAX_OBJ'], 255, self.nothing)
        cv2.createTrackbar("DWN_LINE", "Panel", self.setting['DWN_LINE'], self.cam_characteristic['frame_height'], self.nothing)
        cv2.createTrackbar("TOP_LINE", "Panel", self.setting['TOP_LINE'], self.cam_characteristic['frame_height'], self.nothing)
        # Makes array for detector
        self.persons = []

    def save_log(self, direction):
        """
        Write log for 1C.
        """
        try:
            if direction == "up":  # Direction
                direction_mark = "2"
            else:
                direction_mark = "1"
            now = datetime.datetime.now()
#            ms_now = str(int(time.time() / 1000))
            with open(now.strftime("%d%m%y%H") + ".txt", "a") as log_file:
                log_file.write(f"{now.strftime('%d.%m.%Y')}|{now.microsecond}|1|{direction_mark[1]}|PCCapture|0|")
#            log_file.close()
            return True
        except Exception:
            return False

    def nothing(x):
        """
         Trackpad function. nothing to do
        """
        pass

    def run(self):
        iteration_counter = 0

        # Create new array with 8-bit unsigned integer for morphological filters
        self.kernelOp = numpy.ones((3, 3), numpy.uint8)
        self.kernelCl = numpy.ones((11, 11), numpy.uint8)

        # Make Hershey Fonts
        self.font = cv2.FONT_HERSHEY_SIMPLEX

        # Create panel and trackpads
        panel = numpy.zeros([1, 256], numpy.uint8)

        # Get mask
        mask_frame = self.cap.get_frame()
        while True:
            # Get frame
            frame = self.cap.get_frame()
            # Calculates the absolute difference between mask and frame frames(arrays).
            frame_ABS = cv2.absdiff(frame, mask_frame)
#            cv2.imshow('ADS',frame_ABS)
            # Converts an image to gray color space.
            gray_frame = cv2.cvtColor(frame_ABS, cv2.COLOR_BGR2GRAY)

            cv2.imshow("Panel", panel)

            settings_change = False
            # if position trackbars not equal settings
            for key in self.setting.get_settings_names():
                trackbar_position = cv2.getTrackbarPos(key, "Panel")
                if self.setting[key] != trackbar_position:
                    self.setting[key] = trackbar_position
                    settings_change = True

            if settings_change:
                # Recalculate setting
                self.min_areaTH = self.res / (255-self.setting['MIN_OBJ']+1)
                self.max_areaTH = self.res / (255-self.setting['MAX_OBJ']+1)

                # If setting line position change, recalculate and her
                line_down = int(self.setting[3])
#                print("Red line y:", str(line_down))
                pt1 = [0, line_down]
                pt2 = [self.cam_characteristic['frame_width'], line_down]
                pts_L1 = numpy.array([pt1, pt2], numpy.int32)
                pts_L1 = pts_L1.reshape((-1, 1, 2))

                line_up = int(self.setting[4])
#                print("Blue line y:", str(line_up))
                pt3 = [0, line_up]
                pt4 = [self.cam_characteristic['frame_width'], line_up]
                pts_L2 = numpy.array([pt3, pt4], numpy.int32)
                pts_L2 = pts_L2.reshape((-1, 1, 2))

                self.setting.write_file()

            try:
                # Threshold the difference frame (Change color space to black and white)
                ret, imBin = cv2.threshold(gray_frame, self.setting[0], 255, cv2.THRESH_BINARY)
                # Morphology transformation (open and close). Just filter the noise in the image.
                morphology_mask = cv2.morphologyEx(imBin, cv2.MORPH_OPEN, self.kernelOp)
                morphology_mask = cv2.morphologyEx(morphology_mask, cv2.MORPH_CLOSE, self.kernelCl)
                cv2.imshow('morphologyEx', morphology_mask)
            except Exception:
                # All exceptions end the program.
                print('Error threshold or morphology. End of programm.')
                print(f"UP:{self.cnt_up}")
                print(f"DOWN:{self.cnt_down}")
                break

                # Find contours on image
            ___, contours0, ___ = cv2.findContours(
                                        morphology_mask,
                                        cv2.RETR_EXTERNAL,  # Retrieves only the extreme outer contours
                                        cv2.CHAIN_APPROX_SIMPLE  # Extracts only edge points of contours
                                        )

            # For all contours
            for cnt in contours0:
                # Calculate size of contours
                area = cv2.contourArea(cnt)
                # check cameras on noise
                if area > (self.cam_characteristic['frame_width'] * self.cam_characteristic['frame_height']) * 0.90:
                    iteration_counter = 1000
                if self.min_areaTH < area < self.max_areaTH:
                    M = cv2.moments(cnt)
                    # Get coordinates of the edges
                    cx = int(M['m10']/M['m00'])
                    cy = int(M['m01']/M['m00'])
                    # Get the coordinates of the scope
                    x, y, w, h = cv2.boundingRect(cnt)
                    # Check for a new object
                    new = True
                    for i in persons:
                        # If the object is close to already detected
                        if abs(cx-i.getX()) <= w and abs(cy-i.get_y()) <= h:
                            new = False
                            # Update coordinates for better tracking
                            i.update_coords(cx, cy)

                            date_now = datetime.datetime.now()
                            # Check cross the line
                            if i.going_up(line_down, line_up):
                                self.cnt_up += 1
                                # Write log to console and file
                                print(f"Person crossed going up at {date_now.strftime('%d.%m.%Y')}")
                                if not self.save_log("up", date_now):
                                    print("Logfile save error")
                                break

                            elif i.going_down(line_down, line_up):
                                self.cnt_down += 1
                                print(f"Person crossed going down at {date_now.strftime('%d.%m.%Y')}")
                                if not self.save_log("down", date_now):
                                    print("Logfile save error")
                                break
                        else:
                            print("New obj")
                        # delete object if work done
                        if i.timed_out():
                            index = persons.index(i)
                            persons.pop(index)
                            del i

                    # Create new object
                    if new:
                        p = MyPerson(cx, cy)
                        persons.append(p)

                    # Draw red dot in a middle object, and make scope.
                    cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)
                    cv2.rectangle(frame, (x, y),(x + w, y + h), (0, 255, 0), 2)
                    iteration_counter = 0
                else:
                    # Count frames without tracking objects
                    iteration_counter += 1
                    # If we had a lot of frames without tracking object, we update mask and tracking array
                    if iteration_counter > 1000:
                        ret, mask_frame = self.cap.read()
                        iteration_counter = 0
                        persons = []
                    print(iteration_counter)

            # Draw lines and text on frames
            str_up = f"UP: {self.cnt_up}"
            str_down = f"DOWN:{self.cnt_down}"
            frame = cv2.polylines(frame, [pts_L1], False, (255, 0, 0), thickness=2)
            frame = cv2.polylines(frame, [pts_L2], False, (255, 0, 0), thickness=2)

            cv2.putText(frame, str_up, (10, 40), self.font, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(frame, str_up, (10, 40), self.font, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
            cv2.putText(frame, str_down, (10, 90), self.font, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(frame, str_down, (10, 90), self.font, 0.5, (255, 0, 0), 1, cv2.LINE_AA)

            # Show final frame
            cv2.imshow('Frame', frame)

            # Checking the key press
            k = cv2.waitKey(30) & 0xff
            # if ESC - end program
            if k == 27:
                break
            # If SPACE, we update mask and reset exit counters
            elif k == 32:
                ret, mask_frame = self.cap.read()
                self.cnt_up = 0
                self.cnt_down = 0

        # Close camera and all windows
        self.cap.release()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    PeopleCounter()
