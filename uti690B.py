# standard libraries #
import logging

import numpy as np

logging.basicConfig(level = logging.INFO)
import time
# pip installed libraries #
import numpy
import cv2

# wrapper libraries, which require external installation #
import pytesseract
pytesseract.pytesseract.tesseract_cmd = "C:\Program Files\Tesseract-OCR\\tesseract.exe"

separator = "*************************************************************************"

class uti690B():
    """
    Class for the thermal camera uti690B
    Uses computer vision and OCR in order to get the temperature data from the stream
    """

    # coordinates of the blocks to be further processed #
    # coordinate_format = [y0,y1,x0,x1]
    sign_block = [12,30,2,20]
    center_temp_block = [5,33,25,112]               # checked with image
    max_temp_block = [36,55,194,240]                # checked with image [36,55,194,240]
    min_temp_block = [255,274,194,240]              # checked with image [255,274,194,240]
    contrast_block = [58,253,225,235]               # checked with image
    # coordinates of blocks to remove #
    date_block = [7,18,124,195]                     # checked with image may need improving
    time_block = [23,34,144,180]                    # checked with image may need improving
    battery_block = [13,29,203,235]                 # checked with image

    metadata_block = [320,321,0,240]

    im_path = "test_images"



    def __init__(self):
        """
        Constructor:
        Does nothing, except initializing a couple variables to None
        """
        self.camera_n = 1
        self.camera = None

    def find_camera(self):
        """
        # 1. find all available cameras (take a picture with each of them, until crash)
        # 2. Check which camera has a picture size matching with the UTI690 resolution.
        # 3. if no camera with the right size is found, return no uti690b found.
        # if a camera is being used by another application, Videocapture works,
        """

        print("Finding camera number (this may take some seconds)")
        done = False
        camera_n = 0
        retval = False
        while(done == False):
            logging.debug(separator)
            # logging.debug("Camera number: " + str(camera_n))
            camera = cv2.VideoCapture(camera_n)
            # logging.debug("camera object created")
            ok , img = camera.read()
            logging.debug("return value camera read: " + str(ok))

            if(ok == True):
                logging.debug("Camera number: " + str(camera_n))
                im_size = numpy.shape(img)
                logging.debug("Picture size:" + str(im_size))
                if(im_size == (321, 240, 3)):
                    logging.debug("Picture dimensions matching UTi690")
                    print("UTi690 camera found")
                    self.camera_n = camera_n
                    retval = True

            else:
                logging.debug("camera " + str(camera_n) + " not available?")

            if(camera_n >= 100):
                done = True

            camera_n = camera_n + 1
            logging.debug(separator)

        if(retval == False):
            print("No UTI690 was found, please review your connections")

        return(retval)

    def interactive_menu(self):
        """
        Allows choosing between different options via command line interface.
        :return: True
        """
        quit = 0
        while(quit == 0):
            option = input("Please choose option (write 'help' for command list)")
            if(option == "find"):
                found = self.find_camera()
            elif(option == "preview"):
                self.preview()
            elif(option == "snap"):
                self.take_snapshot()
            elif(option == "help"):
                print("preview")
                print("snap")
                #print("split")
            elif(option == "test"):
                self.test()
            elif(option == "quit"):
                quit = 1
            else:
                print("Command not recognized")

        return(True)

    def preview(self):
        """
        Shows a video preview of the camera,
         useful for location of the camera at the right position for automation.
         pressing 'esc' quits the preview.
        :return: True
        """
        self.camera = cv2.VideoCapture(self.camera_n)  # this should be variable.
        quit = 0
        while quit == 0:
            check, frame_thermal = self.camera.read()
            # check, frame_linear = cam_linear.read()
            # check, frame_wafer = cam_wafer.read()

            cv2.imshow('video', frame_thermal)
            # cv2.imshow('video', frame_linear)
            # cv2.imshow('video', frame_wafer)

            key = cv2.waitKey(1)
            if key == 27:
                quit = 1
                self.camera.release()
                cv2.destroyAllWindows()

        return(True)

    def connect(self):
        """
        Tries to create an opencv capture object, and displays warnings if fails
        :return: success, True if worked, False if failed
        """
        success = False
        try:
            self.camera = cv2.VideoCapture(self.camera_n)
            success = True
        except:
            logging.warning("Camera not connected?")
            logging.warning("Camera already open?")
            success = False
        return(success)

    def disconnect(self):
        """
        Releases the camera
        :return: return value from camera release method
        """
        retval = self.camera.release()
        return(retval)

    def take_picture(self):
        """
        takes a single picture
        to be implemented: handling errors on takink picture failure?
        """
        check, img = self.camera.read()
        logging.debug(img.shape)
        return(img)

    def take_snapshot(self):            # stores picture to file
        """
        Connects the camera, takes a picture, saves it to file, and disconnects the camera
        """
        self.connect()
        check, img = self.camera.read()
        cv2.imwrite(self.im_path + "/test_image.png", img)
        self.disconnect()
        return(check)

    def get_block(self,image,coord):
        """
        :param image:   Image from which to get a block
        :param coord:   Array with coordinates of the block to be taken (x0,y0,x1,y1)
        :return:        block
        """

        block = image[
                coord[0]:coord[1],
                coord[2]:coord[3]
                ]
        # block = image[
        #         coord[0]+1:coord[1]-1,
        #         coord[2]+1:coord[3]-1
        #         ]
        return(block)

    def remove_block(self, image, coord):
        """
        :param image: Image from which a block will be removed
        :param coord: Coordinates of the bock to be removed
        :return: Pointer to the image with removed block?
        """
        image[
            coord[0]:coord[1],
            coord[2]:coord[3]
            ] = 0

        return(image)

    def split_image(self, image):
        """
        Splits image in different parts, required for further processing
        :return:
        """

        cv2.imwrite(self.im_path + "/original_image.png", image)


        rest_img = image.copy()
        # metadata #
        metadata_img = self.get_block(image,self.metadata_block)
        cv2.imwrite(self.im_path + "/metadata.png", metadata_img)

        # center #
        center_temp_img = self.get_block(image,self.center_temp_block)
        cv2.imwrite(self.im_path + "/center_temp.png", center_temp_img)

        # max #
        max_temp_img = self.get_block(image,self.max_temp_block)
        cv2.imwrite(self.im_path + "/max_temp.png", max_temp_img)

        # min #
        min_temp_img = self.get_block(image,self.min_temp_block)
        cv2.imwrite(self.im_path + "/min_temp.png", min_temp_img)

        # contrast bar #
        contrast_img = self.get_block(image,self.contrast_block)
        cv2.imwrite(self.im_path + "/contrast.png", contrast_img)

        # rest #
        self.remove_block(rest_img,self.sign_block)
        self.remove_block(rest_img,self.center_temp_block)
        self.remove_block(rest_img, self.max_temp_block)
        self.remove_block(rest_img,self.min_temp_block)
        self.remove_block(rest_img,self.contrast_block)
        self.remove_block(rest_img,self.date_block)
        self.remove_block(rest_img,self.time_block)
        self.remove_block(rest_img,self.battery_block)
        self.remove_block(rest_img,self.metadata_block)
        cv2.imwrite(self.im_path + "/rest.png", rest_img)



        return([center_temp_img,max_temp_img,min_temp_img,contrast_img, rest_img])

    def clean_image(self, image):
        """
        Prepares the image for OCR
        :param image: image to be prepared for OCR
        :return: image ready to be processed with OCR
        """
        image = cv2.resize(image, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)

        image_g = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        cv2.imshow("Gray", image_g)
        kernel = np.array([[0, -1, 0],
                           [-1, 5, -1],
                           [0, -1, 0]])

        image_sharp = image_g
        # image_sharp = cv2.filter2D(src=image_g, ddepth=-1, kernel=kernel)
        # cv2.imshow("Gray", image_sharp)
        # image_sharp = cv2.equalizeHist(image_g)
        # cv2.imshow("equalized", image_sharp)

        retval, image_bw = cv2.threshold(image_sharp, 210, 255,cv2.THRESH_BINARY)  # returns a fucking tuple, where the fuck is this explained?
        # image_bw = cv2.adaptiveThreshold(image_g, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 2)


        cv2.imshow("BW", image_bw)
        cv2.waitKey(50)
        return(image_bw)

    def get_val(self, image):
        image_clean = self.clean_image(image)
        full_path = self.im_path + "/image_clean.png"
        cv2.imwrite(full_path,image_clean)

        val_im_str = pytesseract.image_to_string(image_clean,config="--psm 8 --psm 6 -c tessedit_char_whitelist=0123456789.")  # read tesseract manual page, configuration for image as single word.

        try:
            val = float(val_im_str)
        except:
            logging.error("Value couldn't be converted to a float")
            val = None
        return(val)

    def get_max_temp(self):             # finds max temp
        max_temp_im = cv2.imread(self.im_path + "/max_temp.png")
        max_temp = self.get_val(max_temp_im)
        return(max_temp)

    def get_min_temp(self):             # min temp
        min_temp_im = cv2.imread(self.im_path + "/min_temp.png")
        min_temp = self.get_val(min_temp_im)
        return(min_temp)

    def contrast_to_temp(self, contrast_bar, max_temp, min_temp):
        print(contrast_bar.shape)
        bar_width = contrast_bar.shape[1]
        bar_height = contrast_bar.shape[0]
        print(bar_height)
        contrast_array = contrast_bar[:,int(bar_width/2),:]
        print(contrast_array.shape)

        contrast_array_grey = cv2.cvtColor(contrast_array, cv2.COLOR_BGR2GRAY)
        for val in contrast_array_grey:
            print(val)
        different_vals = len(np.unique(contrast_array, axis=0))
        print("Number of different values at the contrast array: " + str(different_vals))

    def image_to_temp(self, image, max_temp, min_temp, contrast_bar):
        """
        Maps image to temperature values
        :param image: Input image
        :param max_temp: maximum temperature, previously obtained with OCR (float)
        :param min_temp: minimum temperature, previously obtained with OCR (float)
        :param contrast_bar: currently unused, useful for future implementations
        :return: bidimensional array with the temperature values
        """
        temp_vals = np.zeros(image.shape)
        image_grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        cv2.imwrite(self.im_path + "/rest_grey.png", image_grey)

        # max_val = 0
        # min_val = 255

        size = image_grey.shape
        y = size[0]
        x = size[1]

        # print("Size: " + str(size))
        # print("Y: " + str(y))
        # print("X: " + str(x))


        # for val in image_grey:
        #     print(val)

        # self.contrast_to_temp(contrast_bar, max_temp, min_temp)


        for i in range(x):
            for j in range(y):
                temp_vals[j,i] = min_temp + (image_grey[j][i]/255)*(max_temp - min_temp)

        for i in range(x):
            for j in range(y):
                if(image_grey[j][i] == 0):          # 0 is reserved for masked pixels
                    temp_vals[j, i] = 0             # 0 will be reserved for unused pixels
                else:
                    temp_vals[j,i] = min_temp + (image_grey[j][i]/255)*(max_temp - min_temp)

        #
        # print(temp_vals)

        return(temp_vals)

    def get_temp_vals(self):
        """
        Performs all actions needed to get the temperature values of the current frame
        :return: the temperature values matrix
        """
        temp_vals = None
        try:
            img = self.take_picture()                                       # saves frame
            images = self.split_image(img)                                  # divides it onto different regions of interest
            max_temp = self.get_max_temp()                                  # gets maximum temperature from digits via ocr
            min_temp = self.get_min_temp()                                  # same for minimum temp
            rest = cv2.imread(self.im_path + "/rest.png")                   # gets the image containing only temperature pixels
            contrast_bar = cv2.imread(self.im_path + "/contrast.png")       # gets the contrast bar to calculate the temperature values

            temp_vals = self.image_to_temp(rest, max_temp, min_temp, contrast_bar)      # calculates the temperature values based on all previous

        except:
            logging.error("Failed acquiring temperature values")

        return(temp_vals)



    def test(self):
        """
        Placeholder for various tests
        :return: True
        """
        # camera_n = self.find_camera()
        # if(camera_n):
        #     print("UTI690B camera found, in n: " + str(self.camera_n))
        # else:
        #     print("No UTI cameras were found")

        # camera_found = self.find_camera()                                  # finding the camera

        if (self.camera_n != None):
            self.connect()

            for i in range(10):
                temp_vals = self.get_temp_vals()
                print(temp_vals)

            start_time = time.time()
            for i in range(1,100):
                print(i)
                img = self.take_picture()
                images = self.split_image(img)
                max_temp = self.get_max_temp()
                print("Maximum temperature value: " + str(max_temp))
                min_temp = self.get_min_temp()
                print("Minimum temperature value: " + str(min_temp))

                # rest = cv2.imread(self.im_path + "/rest.png")
                # contrast_bar = cv2.imread(self.im_path + "/contrast.png")
                #
                # try:
                #     temp_values = self.image_to_temp(rest, max_temp, min_temp, contrast_bar)
                # except:
                #     logging.error("Failed converting image to temperature")

                # image = cv2.imread(self.im_path + "/rest.png")
                # print("unique values on test picture: ")
                # unique_vals = np.unique(image.reshape(-1,3),axis=0)
                # for val in unique_vals:
                #     print(val)
                # print(len(unique_vals))

            end_time = time.time()
            dt = end_time-start_time
            print(dt)
        else:
            print("NO CAMERA AVAILABLE: Couldn't proceed with the testing")
            print("use 'find' command to find a camera, if it fails, check your connections")

        self.disconnect()

        return(True)

if __name__ == "__main__":
    thermal_cam = uti690B()
    thermal_cam.interactive_menu()

