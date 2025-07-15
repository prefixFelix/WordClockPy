import sys
import ntptime
import time
import asyncio
import json
import dev_config as config
import wordclock


def set_time():
    """ Sync NTP """
    ntptime.settime()  # todo can fail (OSError: [Errno 116] ETIMEDOUT)
    print(f'[>] Current UTC time: {time.localtime()[3]}:{time.localtime()[4]}')
    dst_status = eu_dst_active(time.localtime())
    if dst_status:
        update_config_file({"dst": 1})
    else:
        update_config_file({"dst": 0})
    print(f'[>] DST: {dst_status}')
    print(f'[>] Local time: {local_hour()}:{time.localtime()[4]}')


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
            line = line.strip()
            if line and not line.startswith('#'):
                try:
                    var_name, value = line.split('=', 1)
                    var_name = var_name.strip()

                    if var_name in updates:
                        # Update the line with new value
                        new_value = updates[var_name]
                        lines[i] = f"{var_name} = {new_value}\n"
                except ValueError:
                    # Skip lines that don't follow the format
                    pass

        # Write back to file
        with open(filename, 'w') as file:
            for line in lines:
                file.write(line)
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
        print('A', end='')
        wc.update_display(time.localtime()[3], time.localtime()[4])

        # Resync time every hour
        if time.localtime()[4] == 0:
            print('X')
            try:
                ntptime.settime()
                ntp_miss = 0
            except:
                ntp_miss += 1
                print(f'[!] NTP miss: {ntp_miss}')

        # Check every day at 2:00 if dst is active (summer -> winter wrong for 1h!)
        if time.localtime()[3] == 2 and time.localtime()[4] == 0:
            if eu_dst_active(time.localtime()):
                update_config_file({"dst": 1})
            else:
                update_config_file({"dst": 0})

        # Check for scheduled sleeping time
        if config.power:
            if config.sleep and time.localtime()[3] == config.sleep_time[0]:
                config.on = False
            if config.sleep and time.localtime()[3] == config.sleep_time[1]:
                config.on = True

        # Sleep at second 0 for 1 minute
        time_delta = (60 - time.localtime()[5]) + 1  # +1 ensures that we are still in the same minute
        await asyncio.sleep(time_delta)


async def main():
    """ Create tasks """
    run_clock_task = asyncio.create_task(run_clock())
    await asyncio.gather(run_clock_task)


if __name__ == '__main__':
    wc = wordclock.WordClock()
    set_time()
    asyncio.run(main())

    """
      Traceback (most recent call last):
      File "main.py", line 173, in <module>
      File "main.py", line 28, in connect
      File "ntptime.py", line 1, in settime
      File "ntptime.py", line 1, in time
      OSError: [Errno 116] ETIMEDOUT
    """
