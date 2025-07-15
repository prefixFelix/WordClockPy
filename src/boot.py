import network
import time
import git_fetch
import dev_config as config
import gc


def connect_wifi():
    # Disable AP - why???
    ap_if = network.WLAN(network.AP_IF)
    ap_if.active(False)
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect(config.wifi_ssid, config.wifi_passwd)
    print(f'\n\n\n[>] Connecting to {config.wifi_ssid}', end='')
    while not sta_if.isconnected():
        print('.', end='')
        time.sleep(0.2)
    print(f'connected with the IP http://{sta_if.ifconfig()[0]}')


connect_wifi()
# Pull files if version changed
if not git_fetch.status():
    git_fetch.pull()
gc.collect()