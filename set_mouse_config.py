#!/home/ozone/mouseenv/bin/python3

import usb.core
import usb.util
import argparse

class MouseDriver:
    def __init__(self):
        self.x9_vendorid = 0x18f8  # vendorid
        self.x9_productid = 0x0fc0  # productid
        self.bmRequestType = 0x21  # bmRequestType
        self.bRequest = 0x09  # bRequest
        self.wValue = 0x0307  # wValue
        self.wIndex = 0x0001  # wIndex
        self.mouse = None
        self.conquered = False
        self.device_busy = bool()
        self.current_active_profile = 1
        self.profile_states = [1, 1, 1, 1, 1, 1]
        self.supported_dpis = [200, 400, 600, 800, 1000, 1200, 1600, 2000, 2400, 3200, 4000, 4800]
        self.cyclic_colors = {"Yellow": 1, "Blue": 1, "Violet": 1, "Green": 1, "Red": 1, "Cyan": 1, "White": 1}
        self.supported_colors = {
            "red": (255, 0, 0),
            "green": (0, 255, 0),
            "blue": (0, 0, 255),
            "yellow": (255, 255, 0),
            "cyan": (0, 255, 255),
            "violet": (255, 0, 255),
            "white": (255, 255, 255)
        }

    def find_device(self):
        print("Trying to find device...")
        self.mouse = usb.core.find(idVendor=self.x9_vendorid, idProduct=self.x9_productid)

    def device_state(self):
        try:
            self.device_busy = self.mouse.is_kernel_driver_active(self.wIndex)
        except usb.core.USBError as exception:
            print(exception.strerror)
            if exception.errno == 13:
                print("Permission denied. Try running with sudo or add a udev rule for your mouse")
            return -1
        except AttributeError:
            print("Device not found. Try replugging")
            return -2
        print("Device is ready to be configured")
        return 1

    def conquer(self):
        if self.device_busy and not self.conquered:
            self.mouse.detach_kernel_driver(self.wIndex)
            usb.util.claim_interface(self.mouse, self.wIndex)
            self.conquered = True

    def liberate(self):
        if self.conquered:
            try:
                usb.util.release_interface(self.mouse, self.wIndex)
                self.mouse.attach_kernel_driver(self.wIndex)
                self.conquered = False
            except:
                print("Failed to release device back to kernel")

    def init_payload(self, instruction_code):
        payload = [0x07]
        payload.append(instruction_code)
        return payload

    def add_zero_bytes(self, list, number_of_bytes):
        for i in range(number_of_bytes):
            list.append(0x00)

    def set_cyclic_colors(self):
        colorname = list(self.cyclic_colors.keys())
        colors = 0
        for i in range(len(self.cyclic_colors)):
            colors += self.cyclic_colors[colorname[i]] * (2**i)
        return colors

    def create_rgb_lights_config(self, changing_scheme, time_duration=1):
        payload = self.init_payload(0x13)
        payload.append(self.set_cyclic_colors())

        if changing_scheme == "Fixed":
            payload.append(0x86 - time_duration)
        elif changing_scheme == "Cyclic":
            payload.append(0x96 - time_duration)
        elif changing_scheme == "Static":
            payload.append(0x86)
        elif changing_scheme == "Off":
            payload.append(0x87)

        self.add_zero_bytes(payload, 4)
        return payload

    def create_color_profile_config(self, profile, red, green, blue):
        payload = self.init_payload(0x14)
        internal_profile = (profile - 1) * 2
        internal_red = int((255 - red) / 16)
        internal_green = int((255 - green) / 16)
        internal_blue = int((255 - blue) / 16)

        byte = internal_profile * 16 + internal_green
        payload.append(byte)
        byte = internal_red * 16 + internal_blue
        payload.append(byte)

        payload.append(self.set_active_profiles())
        self.add_zero_bytes(payload, 3)
        return payload

    def find_closest_dpi(self, DPI):
        if DPI in self.supported_dpis:
            return DPI

        difference = 4800
        best_match = int()
        for supported in self.supported_dpis:
            temp_diff = DPI - supported
            if (difference >= (temp_diff if temp_diff > 0 else temp_diff * -1)):
                best_match = supported
                difference = temp_diff
        return best_match

    def set_active_profiles(self):
        byte = 0
        for i in range(6):
            byte += self.profile_states[i] * 2**i
        return byte

    def set_dpi_this_profile(self, DPI, profile_to_modify):
        '''DPI is set to the value that is closest to one of the mouse's supported values'''
        internal_dpi = 0
        best_match_dpi = self.find_closest_dpi(DPI)
        if best_match_dpi >= 200 and best_match_dpi <= 1200:
            internal_dpi = int(best_match_dpi / 200)
        elif best_match_dpi == 1600:
            internal_dpi = 0x7
        elif best_match_dpi == 2000:
            internal_dpi = 0x9
        elif best_match_dpi == 2400:
            internal_dpi = 0xb
        elif best_match_dpi == 3200:
            internal_dpi = 0xd
        elif best_match_dpi == 4000:
            internal_dpi = 0xe
        elif best_match_dpi == 4800:
            internal_dpi = 0xf
        else:
            print("DPI out of supported range (200-4800).")

        internal_profile = profile_to_modify + 7
        byte = (internal_dpi * 16) + internal_profile

        return byte

    def create_dpi_profile_config(self, DPI, profile_to_modify):
        payload = self.init_payload(0x09)
        payload.append(0x40 - 1 + self.current_active_profile)
        payload.append(self.set_dpi_this_profile(DPI, profile_to_modify))
        payload.append(self.set_active_profiles())
        self.add_zero_bytes(payload, 3)
        return payload

def main():
    parser = argparse.ArgumentParser(description='Configure Fantech X9 Thor mouse settings')
    parser.add_argument('-d', '--dpi', type=int, help='Set DPI (200-4800)')
    parser.add_argument('-c', '--color', type=str, help='Set LED color (red, green, blue, yellow, cyan, violet, white, off)')
    
    try:
        args = parser.parse_args()
        
        # If no arguments provided, use defaults
        if args.dpi is None and args.color is None:
            args.dpi = 2000
            args.color = 'off'
        
        # Initialize the driver
        driver = MouseDriver()
        
        # Find and initialize the device
        driver.find_device()
        
        # Check device state and conquer if needed
        status = driver.device_state()
        if status == 1:
            driver.conquer()
            
            try:
                # Set DPI if specified
                if args.dpi is not None:
                    if args.dpi < 200 or args.dpi > 4800:
                        print(f"Error: DPI must be between 200 and 4800")
                        parser.print_help()
                        return
                        
                    dpi_payload = driver.create_dpi_profile_config(args.dpi, 1)
                    driver.mouse.ctrl_transfer(
                        bmRequestType=driver.bmRequestType,
                        bRequest=driver.bRequest,
                        wValue=driver.wValue,
                        wIndex=driver.wIndex,
                        data_or_wLength=dpi_payload
                    )
                    print(f"DPI set to: {args.dpi}")
                
                # Set LED color if specified
                if args.color is not None:
                    if args.color.lower() == 'off':
                        led_payload = driver.create_rgb_lights_config("Off")
                        driver.mouse.ctrl_transfer(
                            bmRequestType=driver.bmRequestType,
                            bRequest=driver.bRequest,
                            wValue=driver.wValue,
                            wIndex=driver.wIndex,
                            data_or_wLength=led_payload
                        )
                        print("LED turned off")
                    else:
                        color = args.color.lower()
                        if color in driver.supported_colors:
                            r, g, b = driver.supported_colors[color]
                            # First set the color profile
                            color_payload = driver.create_color_profile_config(1, r, g, b)
                            driver.mouse.ctrl_transfer(
                                bmRequestType=driver.bmRequestType,
                                bRequest=driver.bRequest,
                                wValue=driver.wValue,
                                wIndex=driver.wIndex,
                                data_or_wLength=color_payload
                            )
                            # Then set it to static mode (no blinking)
                            led_payload = driver.create_rgb_lights_config("Static")
                            driver.mouse.ctrl_transfer(
                                bmRequestType=driver.bmRequestType,
                                bRequest=driver.bRequest,
                                wValue=driver.wValue,
                                wIndex=driver.wIndex,
                                data_or_wLength=led_payload
                            )
                            print(f"LED color set to: {color}")
                        else:
                            print(f"Error: Unsupported color: {color}")
                            print("Supported colors: red, green, blue, yellow, cyan, violet, white, off")
                            parser.print_help()
                            return
                
            except Exception as e:
                print(f"Error configuring mouse: {str(e)}")
            finally:
                # Release the device back to the kernel
                driver.liberate()
        else:
            print("Failed to initialize device. Make sure the mouse is connected and you have proper permissions.")
    
    except Exception as e:
        print(f"Error: {str(e)}")
        parser.print_help()

if __name__ == "__main__":
    main()
