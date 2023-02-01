
import usb

from uti690B import uti690B

if __name__ == "__main__":
    print("Pene")
    #
    # import usb.core
    # import usb.backend.libusb1
    # import usb.util
    #
    # busses = usb.busses()
    # for bus in busses:
    #     devices = bus.devices
    #     for dev in devices:
    #         if dev != None:
    #             try:
    #                 xdev = usb.core.find(idVendor=dev.idVendor, idProduct=dev.idProduct)
    #                 if xdev._manufacturer is None:
    #                     xdev._manufacturer = usb.util.get_string(xdev, xdev.iManufacturer)
    #                 if xdev._product is None:
    #                     xdev._product = usb.util.get_string(xdev, xdev.iProduct)
    #                 stx = '%6d %6d: ' + str(xdev._manufacturer).strip() + ' = ' + str(xdev._product).strip()
    #                 print(stx % (dev.idVendor, dev.idProduct))
    #             except:
    #                 pass

