import sys
import machine
import ntptime
import time
import asyncio
import json
import config
import wordclock
from nanoweb import Nanoweb, send_file

# import os; os.remove('boot.py')


def set_time():
    """ Sync NTP """
    for attempt in range(3):
        try:
            ntptime.settime()
            print(f'[+] Current UTC time: {time.localtime()[3]}:{time.localtime()[4]}')
            break
        except OSError as e:
            print(f'[!] NTP sync attempt {attempt + 1} failed: {e}')
            if attempt == 2:
                print(f'[!] NTP sync failed after 3 attempts, using current time')
                break
            time.sleep(1)
    
    dst_status = eu_dst_active(time.localtime())
    if dst_status:
        update_config_file({"dst": 1})
    else:
        update_config_file({"dst": 0})
    print(f'[+] DST: {dst_status}')
    print(f'[+] Local time: {local_hour()}:{time.localtime()[4]}')


def eu_dst_active(td):
    """ Check if dst is currently active """
    # April - September
    if 3 < td[1] < 10:
        return True
    # After last Sunday in March
    if td[1] == 3 and td[2] >= (31 - ((td[6] - td[2]) % 7)):
        return True
    # Before last Sunday in October
    if td[1] == 10 and td[2] < (31 - ((td[6] - td[2]) % 7)):
        return True
    return False


def local_hour():
    """ Return real local hour"""
    return (time.localtime()[3] + config.time_zone + config.dst) % 24


def update_config_file(updates, filename="config.py"):
    """ Update the config file at runtime """
    # Read the current file
    with open(filename, 'r') as file:
        lines = file.readlines()

        # Update existing values
        for i, line in enumerate(lines):
            original_line = line
            line = line.strip()
            if line and not line.startswith('#'):
                try:
                    var_name, value = line.split('=', 1)
                    var_name = var_name.strip()

                    if var_name in updates:
                        # Update the line with new value
                        new_value = updates[var_name]

                        # Format the value properly
                        if isinstance(new_value, str):
                            formatted_value = f"'{new_value}'"
                        elif isinstance(new_value, bool):
                            formatted_value = 'True' if new_value else 'False'
                        elif isinstance(new_value, (list, tuple)):
                            formatted_value = str(new_value)
                        else:
                            formatted_value = str(new_value)

                        # Preserve any inline comments
                        comment_idx = value.find('#')
                        if comment_idx != -1:
                            comment = value[comment_idx:]
                            lines[i] = f"{var_name} = {formatted_value} {comment}\n"
                        else:
                            lines[i] = f"{var_name} = {formatted_value}\n"
                except ValueError:
                    # Skip lines that don't follow the format
                    pass

        # Write back to file
        with open(filename, 'w') as file:
            for line in lines:
                file.write(line)
    # print(f'[~] Saved changes: {updates}')
    reload_config()


def reload_config():
    """ Reimport config.py """
    sys.modules.pop("config")
    global config
    import config


async def run_clock():
    """ Trigger a clock change every 1 min """
    ntp_miss = 0
    while True:
        # Update clock
        wc.update_display(local_hour(), time.localtime()[4])

        # Resync time every hour
        if time.localtime()[4] == 0:
            for attempt in range(3):
                try:
                    ntptime.settime()
                    ntp_miss = 0
                    break
                except OSError as e:
                    if attempt == 2:
                        ntp_miss += 1
                        print(f'[!] NTP miss: {ntp_miss}')
                    else:
                        time.sleep(1)

        # Check every day at 2:00 if dst is active (summer -> winter wrong for 1h!)
        if local_hour() == 2 and time.localtime()[4] == 0:
            if eu_dst_active(time.localtime()):
                update_config_file({"dst": 1})
            else:
                update_config_file({"dst": 0})

        # Check for scheduled sleeping time
        if config.power and config.sleep:
            # Turn off at sleep time
            if local_hour() == config.sleep_time[0] and config.on:
                config.on = False
                print(f'[+] Sleep mode activated.')
            # Turn on at wake time
            elif local_hour() == config.sleep_time[1] and not config.on:
                config.on = True
                print(f'[+] Sleep mode deactivated.')

        # Sleep at second 0 for 1 minute
        time_delta = (60 - time.localtime()[5]) + 1  # +1 ensures that we are still in the same minute
        await asyncio.sleep(time_delta)


async def main():
    """ Create tasks """
    run_clock_task = asyncio.create_task(run_clock())
    naw_task = asyncio.create_task(naw.run())
    await asyncio.gather(run_clock_task, naw_task)

naw = Nanoweb()
@naw.route("/")
async def index(request):
    await request.write("HTTP/1.1 200 Ok\r\n")
    await send_file(request, '/assets/index.html')

@naw.route('/get_config')
async def get_config(request):
    response_data = {
        "version": config.version,
        "power": config.power,
        "brightness": config.brightness,
        "color": config.color,
        "led_type": config.led_type,
        "show_it_is": config.show_it_is,
        "show_minutes": config.show_minutes,
        "show_oclock": config.show_oclock,
        "minute_clockwise": config.minute_clockwise,
        "transition": config.transition,
        "transition_duration": config.transition_duration,
        "transition_smoothness": config.transition_smoothness,
        "sleep": config.sleep,
        "sleep_time": config.sleep_time,
        "ota": config.ota,
        "gamma_correction": config.gamma_correction,
        "wifi_ssid": config.wifi_ssid,
        "static_ip": config.static_ip,
        "ip": config.ip,
        "subnet_mask": config.subnet_mask,
        "gateway": config.gateway,
        "dns": config.dns
    }
    await request.write("HTTP/1.1 200 OK\r\n")
    await request.write("Content-Type: application/json\r\n\r\n")
    await request.write(json.dumps(response_data))
    print('[+] Get config.')


@naw.route('/set_config')
async def set_config(request):
    try:
        print('[+] Set config...', end='')
        # Read the exact number of bytes specified by Content-Length
        content_length = int(request.headers.get('Content-Length', 0))
        if content_length > 0:
            body = await request.read(content_length)
        else:
            body = b''
        data = json.loads(body.decode('utf-8'))
        
        # Send response first, then update config
        await request.write("HTTP/1.1 200 OK\r\n")
        await request.write("Content-Type: application/json\r\n\r\n")
        await request.write(json.dumps({"status": "success"}))
        
        # Update config after response is sent
        update_config_file(data)
        print('updated config...', end='')
        
        # Reload config in wordclock module
        wc.reload_config()
        print('reloaded config...', end='')
        
        # Update display with new settings
        wc.update_display(local_hour(), time.localtime()[4])
        print('updated display...', end='')
        
        # If color or brightness changed, refresh existing LEDs
        if 'color' in data or 'brightness' in data:
            wc.refresh_color_brightness()
        print('DONE!')
    except Exception as e:
        print("Error in set_config:", e)
        await request.write("HTTP/1.1 500 Internal Server Error\r\n")
        await request.write("Content-Type: application/json\r\n\r\n")
        await request.write(json.dumps({"error": "Internal server error"}))


@naw.route('/restart')
async def restart(request):
    await request.write("HTTP/1.1 200 OK\r\n")
    await request.write("Content-Type: application/json\r\n\r\n")
    await request.write(json.dumps({"status": "restarting"}))

    print('[!] Restarting!')
    await asyncio.sleep(2)  # Give time for response to be sent
    machine.reset()


if __name__ == '__main__':
    # Init clock, webserver and sync to ntp
    wc = wordclock.WordClock()
    # Turn off all LEDs on startup
    all_leds = set(range((config.x_max * config.y_max) + 4))
    off_color = (0, 0, 0, 0) if len(config.led_type) == 4 else (0, 0, 0)
    wc.refresh_color_brightness(all_leds, off_color)
    set_time()

    asyncio.run(main())
