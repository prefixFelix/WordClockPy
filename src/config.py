version = "1.2"
import language as language_file

wifi_ssid = 'SET_HERE'
wifi_passwd = 'SET_HERE'

static_ip = False               # Set to False to use DHCP, if false other values will be ignored
ip = '192.168.0.111'            # Static IP of the FenoPy device
subnet_mask = '255.255.255.0'   # Usually this for home networks
gateway = '192.168.0.1'         # Your router's IP
dns = '9.9.9.9'                 # DNS server (Quad9)

ota = False                      # Fetch updates from github automatically
data_pin = 22                   # GPIO of the LED data pin
time_zone = 1                   # Timezone hour offset from UTC
dst = 0                         # 1 if daylight-saving-time is active

color = (0, 0, 0, 255)                      # 3 tuple for RGB or WWA, 4 tuple for RGBW
brightness = 1.0                            # 0.0-1.0100%
gamma_correction = True                     # Dimming: False = linear, True = with gamma correction table
transition = 'concurrent_fade'              # Fade mode: None, concurrent_fade, successive_fade
# Smooth / CPU heavy: S=0.001, D=0.005; Tradeoff: S=0.002, D=0.01; Light CPU: S=0.004, D=0.02
transition_duration = 0.01                  # Time between each fade step
transition_smoothness = 0.002               # Dimming rate between each fade step

orientation = 'vertical'                  # vertical, horizontal
first_led = 'top_left'                      # top_left, top_right, bottom_left, bottom_right
x_max = 11                                  # LED count x-axis
y_max = 10                                  # LED count y-axis
led_type = 'RGBW'                           # Strip type: RGB, RGBW, WWA
language = language_file.lang_german        # Language from language.py
show_it_is = True
show_minutes = True
show_oclock = True
minute_clockwise = True

sleep = True                                # Enable display off time window
sleep_time = (1, 6)                         # Display off time window: form / til (0-23, 0-23)
on = True                                   # Power state of the clock
power = True                                # Power switch witch of the clock
