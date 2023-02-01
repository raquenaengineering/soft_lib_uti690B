# standard libraries #
import logging
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



    def __init__(self):
        self.camera_n = None


    def find_camera(self):

        # 1. find all available cameras (take a picture with each of them, until crash)
        # 2. Check which camera has a picture size matching with the UTI690 resolution.
        # 3. if no camera with the right size is found, return no uti690b found.
        # if a camera is being used by another application, Videocapture works,


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

    def preview(self):
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

    def take_snapshot(self):            # stores picture to file
        try:
            self.camera = cv2.VideoCapture(self.camera_n)
        except:
            logging.warning("Camera not connected?")
            logging.warning("Camera already open?")
        check, img = self.camera.read()
        cv2.imwrite("test_images/test_image.png", img)
        logging.debug(img.shape)
        # cleanup #
        self.camera.release()
        cv2.destroyAllWindows()
        return(img)

    def split_image(self, image):
        """
        Splits image in different parts, required for further processing
        :return:
        """
        center_temp_img = image[0:40,0:120]
        cv2.imwrite("test_images/center_temp.png", center_temp_img)
        max_temp_img = image[35:55,196:250]
        cv2.imwrite("test_images/max_temp.png", max_temp_img)
        min_temp_img = image[254:274,196:250]
        cv2.imwrite("test_images/min_temp.png", min_temp_img)
        contrast_img = image[58:253,226:234]
        cv2.imwrite("test_images/contrast.png", contrast_img)

        return([center_temp_img,max_temp_img,min_temp_img,contrast_img])

    def clean_images(self, image_list):
        clean_image_list = []
        for image in image_list:
            image_g = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            aaa, image_bw = cv2.threshold(image_g, 180, 255, cv2.THRESH_BINARY)      # returns a fucking tuple, where the fuck is this explained?
            clean_image_list.append(image_bw)
        return(clean_image_list)

    def calculate_temp_grey_levels(self, max_val,min_val, contrast_img):
        logging.debug("calculate_temp_grey_levels()")
        logging.debug("max_val = " + str(max_val))
        logging.debug("min_val = " + str(min_val))

        # 1. map the min_val to the lower value
        # 2. map the max_val to the higher value

    def save_images(self, image_list):
        for i in range(len(image_list)):
            im_name = "test_images/im" + str(i) + ".png"
            cv2.imwrite(im_name,image_list[i])

    def get_values_from_images(self, image_list):
        values = []
        for image in image_list:
            #logging.debug("Showing image to be processed")
            #cv2.imshow('Image',image)
            #cv2.waitKey()
            text = pytesseract.image_to_string(image, config="--psm 8")             # read tesseract manual page, configuration for image as single word.
            print('"' + text + '"')
            #val = float(text)
            values.append(text)
        logging.debug(values)
        return(values)

    def get_max_temp(self):             # finds max temp
        retval = False
        max_temp_im = cv2.imread("test_images/max_temp.png")
        max_temp = pytesseract.image_to_string(max_temp_im,config="--psm 8")  # read tesseract manual page, configuration for image as single word.
        return(max_temp)

    def get_min_temp(self):             # min temp
        retval = False
        min_temp_im = cv2.imread("test_images/min_temp.png")
        min_temp = pytesseract.image_to_string(min_temp_im,config="--psm 8")  # read tesseract manual page, configuration for image as single word.
        return(min_temp)

    def test(self):

        # camera_n = self.find_camera()
        # if(camera_n):
        #     print("UTI690B camera found, in n: " + str(self.camera_n))
        # else:
        #     print("No UTI cameras were found")

        camera_found = self.find_camera()                                  # finding the camera

        if (camera_found):
            img = self.take_snapshot()
            images = self.split_image(img)
            images_clean = self.clean_images(images)
            self.save_images(images_clean)
            # vals = self.get_values_from_images(images_clean)
            max_temp = self.get_max_temp()
            print("Maximum temperature value: " + str(max_temp))
            min_temp = self.get_min_temp()
            print("Minimum temperature value: " + str(min_temp))
        else:
            print("NO CAMERA FOUND: Couldn't proceed with the testing")

if __name__ == "__main__":
    thermal_cam = uti690B()
    thermal_cam.interactive_menu()

