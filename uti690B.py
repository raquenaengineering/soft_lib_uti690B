import logging
logging.basicConfig(level = logging.DEBUG)
import time

import numpy
import cv2
#import opencv
class uti690B():



    def __init__(self):
        pass

    def interactive_menu(self):
        quit = 0
        while(quit == 0):
            option = input("Please choose option (write 'help' for command list)")
            if(option == "preview"):
                self.preview()
            if(option == "snap"):
                self.take_snapshot()
            if(option == "quit"):
                quit = 1
            else:
                print("Command not recognized")


    def preview(self):
        self.camera = cv2.VideoCapture(1)  # this should be variable.
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
                cv2.destroyAllWindows()

    def take_snapshot(self):            # stores picture to file
        self.camera = cv2.VideoCapture(1)
        check, frame_thermal = self.camera.read()
        cv2.imwrite("test_images/test_image.png", frame_thermal)
        logging.debug(frame_thermal.shape)
        # cv2.imshow("video",frame_thermal)
        self.split_image(frame_thermal)
        cv2.destroyAllWindows()

    def split_image(self, image):
        """
        Splits image in different parts, required for further processing
        :return:
        """
        centerpoint_block = image[0:40,0:120]
        cv2.imwrite("test_images/centerpoint_block.png", centerpoint_block)
        max_temp_block = image[35:55,196:250]
        cv2.imwrite("test_images/max_temp_block.png", max_temp_block)
        min_temp_block = image[254:274,196:250]
        cv2.imwrite("test_images/min_temp_block.png", min_temp_block)
        # contrast_block = image[57:254,225:235]
        contrast_block = image[58:253,226:234]
        cv2.imwrite("test_images/contrast_block.png", contrast_block)



    def get_max_temp(self):             # finds max temp
        pass

    def get_min_temp(self):             # min temp
        pass