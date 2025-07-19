import network
import time
import git_fetch
import config
import gc


def connect_wifi():
    # Disable AP - why???
    ap_if = network.WLAN(network.AP_IF)
    ap_if.active(False)
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)

    # Configure static IP if specified in config
    if config.static_ip:
        sta_if.ifconfig((
            config.ip,
            config.subnet_mask,
            config.gateway,
            config.dns
        ))
    sta_if.connect(config.wifi_ssid, config.wifi_passwd)
    print(f'\n\n\n[>] Connecting to {config.wifi_ssid}', end='')
    while not sta_if.isconnected():
        print('.', end='')
        time.sleep(0.2)
    print(f'connected with the IP http://{sta_if.ifconfig()[0]}')

# Check for updates in repo
try:
    print("[>] Checking for updates...")
    if config.ota and not git_fetch.status():
        print("[>] Pulling files form git. This can take a while...")
        git_fetch.pull()
except Exception as e:
    print(f'[!] {e}')
connect_wifi()
gc.collect()
