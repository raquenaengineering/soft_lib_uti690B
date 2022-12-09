# standard libraries #
import logging
logging.basicConfig(level = logging.DEBUG)
import time
# pip installed libraries #
import cv2

# wrapper libraries, which require external installation #
# import opencv
import pytesseract
pytesseract.pytesseract.tesseract_cmd = "C:\Program Files\Tesseract-OCR\\tesseract.exe"


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
            if(option == "help"):
                print("preview")
                print("snap")
                #print("split")
            if(option == "test"):
                self.test()
            if(option == "quit"):
                quit = 1
            else:
                print("Command not recognized")

    def test(self):
        img = self.take_snapshot()
        images = self.split_image(img)
        images_clean = self.clean_images(images)
        self.save_images(images_clean)
        vals = self.get_values_from_images(images_clean)


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
                self.camera.release()
                cv2.destroyAllWindows()

    def take_snapshot(self):            # stores picture to file
        try:
            self.camera = cv2.VideoCapture(1)
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

    def save_images(self, image_list):
        for i in range(len(image_list)):
            im_name = "test_images/im" + str(i) + ".png"
            cv2.imwrite(im_name,image_list[i])

    def get_values_from_images(self, image_list):
        for image in image_list:
            logging.debug("Showing image to be processed")
            cv2.imshow('Image',image)
            cv2.waitKey()
            text = pytesseract.image_to_string(image, config="--psm 8")             # read tesseract manual page, configuration for image as single word.
            print('"' + text + '"')

        return(image_list)

    def get_max_temp(self):             # finds max temp
        pass

    def get_min_temp(self):             # min temp
        pass