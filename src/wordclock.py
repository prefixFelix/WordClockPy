import time
import machine
import neopixel
import config

correction = [
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2,
    2, 3, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 5, 5, 5,
    5, 6, 6, 6, 6, 7, 7, 7, 7, 8, 8, 8, 9, 9, 9, 10,
    10, 10, 11, 11, 11, 12, 12, 13, 13, 13, 14, 14, 15, 15, 16, 16,
    17, 17, 18, 18, 19, 19, 20, 20, 21, 21, 22, 22, 23, 24, 24, 25,
    25, 26, 27, 27, 28, 29, 29, 30, 31, 32, 32, 33, 34, 35, 35, 36,
    37, 38, 39, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 50,
    51, 52, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 66, 67, 68,
    69, 70, 72, 73, 74, 75, 77, 78, 79, 81, 82, 83, 85, 86, 87, 89,
    90, 92, 93, 95, 96, 98, 99, 101, 102, 104, 105, 107, 109, 110, 112, 114,
    115, 117, 119, 120, 122, 124, 126, 127, 129, 131, 133, 135, 137, 138, 140, 142,
    144, 146, 148, 150, 152, 154, 156, 158, 160, 162, 164, 167, 169, 171, 173, 175,
    177, 180, 182, 184, 186, 189, 191, 193, 196, 198, 200, 203, 205, 208, 210, 213,
    215, 218, 220, 223, 225, 228, 231, 233, 236, 239, 241, 244, 247, 249, 252, 255]


class WordClock:
    def __init__(self):
        self.data_pin = machine.Pin(config.data_pin, machine.Pin.OUT)
        self.strip = neopixel.NeoPixel(self.data_pin, config.x_max * config.y_max, bpp=len(config.led_type))

        self.minute_indices = self.get_minute_indices()
        self.display = set()

    def get_minute_indices(self):
        if config.orientation == 'vertical':
            corners = [0, config.y_max + 1, (config.y_max * (config.x_max - 1)) + 2, (config.y_max * config.x_max) + 3]

            # If size is not 11x10 - swap last colum/row
            if not config.x_max % 2:
                tmp = corners[3]
                corners[3] = corners[2]
                corners[2] = tmp

            # Reorient the corner indices
            if config.first_led == 'bottom_left':
                return [corners[1], corners[3], corners[0], corners[2]]
            if config.first_led == 'bottom_right':
                return [corners[3], corners[1], corners[2], corners[0]]
            if config.first_led == 'top_left':
                return [corners[0], corners[2], corners[1], corners[3]]
            if config.first_led == 'top_right':
                return [corners[2], corners[0], corners[3], corners[1]]
        # Horizontal
        else:
            corners = [0, config.x_max + 1, (config.x_max * (config.y_max - 1)) + 2, (config.y_max * config.x_max) + 3]

            # If size is not 11x10 - swap last colum/row
            if config.y_max % 2:
                tmp = corners[3]
                corners[3] = corners[2]
                corners[2] = tmp

            if config.first_led == 'bottom_left':
                return [corners[3], corners[2], corners[0], corners[1]]
            if config.first_led == 'bottom_right':
                return [corners[2], corners[3], corners[1], corners[0]]
            if config.first_led == 'top_left':
                return [corners[0], corners[1], corners[3], corners[2]]
            if config.first_led == 'top_right':
                return [corners[1], corners[0], corners[2], corners[3]]

    def time_to_word_cords(self, hour, minute):
        """ Convert the actual time to coordinates of the actual letters on the clock face"""
        cords = []
        minute_indi_l = set()

        # Set hour
        if hour > 12:
            hour = hour - 12
        if hour == 0:
            hour = 12

        if minute >= 30:
            hour += 1
        if hour > 12:
            hour = 1
        cords.append(config.language[f'hour_{hour}'])

        # O clock & it is
        if config.show_it_is:
            cords.append(config.language['it_is'])
        if 0 <= minute < 5:
            cords.append(config.language['o_clock'])

        # Set minute (direct indices, not cords!) todo
        if config.show_minutes:
            minute_digit = minute % 10
            if minute_digit in (0, 5):  # 0, 5
                pass
            if minute_digit in (1, 6):  # 1
                minute_indi_l = set([self.minute_indices[0]])
            if minute_digit in (2, 7):  # 2
                minute_indi_l = set(self.minute_indices[0:2])
            if minute_digit in (3, 8):  # 3
                minute_indi_l = set(self.minute_indices[0:3])
            if minute_digit in (4, 9):  # 4
                minute_indi_l = set(self.minute_indices[0:4])

        # Set preposition
        if 0 <= minute < 5:  # 0
            pass
        if 30 <= minute < 35:  # 30
            cords.append(config.language['half'])
        if 5 <= minute < 25:  # 5-20
            cords.append(config.language['after'])
        if 35 <= minute < 40:  # 35
            cords.extend([config.language['after'], config.language['half']])
        if 35 <= minute < 60:  # 40-55
            cords.append(config.language['before'])
        if 25 <= minute < 30:  # 25
            cords.extend([config.language['before'], config.language['half']])

        # Set 5 minutes
        if 0 <= minute < 5 or 30 <= minute < 35:  # 0, 30
            pass
        if 5 <= minute < 10 or 25 <= minute < 30 or 35 <= minute < 40 or 55 <= minute < 60:  # 5, 25, 35, 55
            cords.append(config.language['minute_5'])
        if 10 <= minute < 15 or 50 <= minute < 55:  # 10, 50
            cords.append(config.language['minute_10'])
        if 15 <= minute < 20 or 45 <= minute < 50:  # 15, 45
            cords.append(config.language['minute_15'])
        if 20 <= minute < 25 or 40 <= minute < 45:  # 20, 40
            cords.append(config.language['minute_20'])

        return cords, minute_indi_l

    def cord_indices_helper(self, row, columns, start_index, alignment, modulo):
        """
        Iterates over each letter of a single "word" and calculate the appropriate index.
        Returns a list of indices corresponding to the letters in the word.
        Could be simplified!
        """

        indices = set()
        # Iterate over each letter (column)
        for column in columns:
            # Set the value at which the index calculation should start & how the calculation is executed
            if start_index.upper() == 'HIGH':
                # Set the start index to the highest possible value
                # (including minute leds! Also sub 1 for the first led and 1 for the addressing offset)
                index = (config.x_max * config.y_max) + 2
                # If high start index: Calculate the index by using subtraction
                calc_mode = -1
            # LOW
            else:
                # Set the start index to the lowest possible value
                # (Not zero because of the first minute led)
                index = 1
                # If low start index: Calculate the index by using addition
                calc_mode = 1

            # Select calculation properties based on the alignment of the layout
            if alignment.upper() == 'VERTICAL':
                max_length_one = config.x_max
                max_length_two = config.y_max
                dimension_one = column
                dimension_two = row
            # VERTICAL
            else:
                max_length_one = config.y_max
                max_length_two = config.x_max
                dimension_one = row
                dimension_two = column

            # Calculate the offset caused by the minute leds (interruptions in sequential indexing)
            # Minute led #1
            if dimension_one > 0:
                index += 1 * calc_mode
            # Minute led #2
            if dimension_one > max_length_one - 2:
                index += 1 * calc_mode

            # Calculate the offset in a single row/column.
            # Depending on the start, the calculation must be done either from the front or from the back.
            if (dimension_one % 2 == 0 and modulo) or (dimension_one % 2 != 0 and not modulo):
                add = (max_length_two - 1) - dimension_two
            else:
                add = dimension_two

            # Calculate the final index, add/sub all rows/columns before and the current line/row
            index += ((max_length_two * dimension_one) + add) * calc_mode
            indices.add(index)
        return indices

    def word_cords_to_indices(self, word):
        """ Convert the coordinates to indices for the LED strip"""

        # Vertical
        if config.orientation == 'vertical':
            if config.first_led == 'bottom_left':
                return self.cord_indices_helper(word[0], word[1], 'LOW', 'VERTICAL', True)
            if config.first_led == 'bottom_right':
                return self.cord_indices_helper(word[0], word[1], 'HIGH', 'VERTICAL', False)
            if config.first_led == 'top_left':
                return self.cord_indices_helper(word[0], word[1], 'LOW', 'VERTICAL', False)
            if config.first_led == 'top_right':
                return self.cord_indices_helper(word[0], word[1], 'HIGH', 'VERTICAL', True)
        # Horizontal
        else:
            if config.first_led == 'bottom_left':
                return self.cord_indices_helper(word[0], word[1], 'HIGH', 'HORIZONTAL', False)
            if config.first_led == 'bottom_right':
                return self.cord_indices_helper(word[0], word[1], 'HIGH', 'HORIZONTAL', True)
            if config.first_led == 'top_left':
                return self.cord_indices_helper(word[0], word[1], 'LOW', 'HORIZONTAL', False)
            if config.first_led == 'top_right':
                return self.cord_indices_helper(word[0], word[1], 'LOW', 'HORIZONTAL', True)

    def get_color_brightness(self, color, brightness):
        if config.gamma_correction:
            # With gamma correction
            return tuple(correction[round(brightness * val)] for val in color)
        else:
            # Linear
            return tuple(round(brightness * val) for val in color)

    def update_display(self, hour, minute):
        # Convert time to word coordinates and minute indices
        word_cords, minute_indices = self.time_to_word_cords(hour, minute)
        # Iterate over words and add indices to new display list
        new_display = set()

        # Only add new words when on - else everything off
        if config.on and config.power:
            for word in word_cords:
                new_display.update(self.word_cords_to_indices(word))
            # Add minutes
            new_display.update(minute_indices)

        # Check which leds to be turned on / off
        display_on = new_display.difference(self.display)  # Also copy?
        display_off = self.display.difference(new_display)  # Also copy?
        self.display = new_display.copy()

        if config.transition:
            if config.transition == 'concurrent_fade':
                b = 0
                while b <= config.brightness:
                    # Get correct color
                    color_on = self.get_color_brightness(config.color, b)
                    color_off = self.get_color_brightness(config.color, round(config.brightness - b, 3))

                    # Set strip color
                    for index_on in display_on:
                        self.strip[index_on] = color_on
                    for index_off in display_off:
                        self.strip[index_off] = color_off
                    self.strip.write()

                    time.sleep(config.transition_duration)
                    # Increment counter (brightness)
                    b = round(b + config.transition_smoothness, 3)
            if config.transition == 'successive_fade':
                # OFF
                b = 0
                while b <= config.brightness:
                    # Get correct color
                    color_off = self.get_color_brightness(config.color, round(config.brightness - b, 3))
                    # Set strip color
                    for index_off in display_off:
                        self.strip[index_off] = color_off
                    self.strip.write()

                    time.sleep(config.transition_duration)
                    # Increment counter (brightness)
                    b = round(b + config.transition_smoothness, 3)
                # ON
                b = 0
                while b <= config.brightness:
                    # Get correct color
                    color_on = self.get_color_brightness(config.color, b)
                    # Set strip color
                    for index_on in display_on:
                        self.strip[index_on] = color_on
                    self.strip.write()

                    time.sleep(config.transition_duration)
                    # Increment counter (brightness)
                    b = round(b + config.transition_smoothness, 3)
        else:
            # Set strip color
            for index_on in display_on:
                self.strip[index_on] = config.color
            for index_off in display_off:
                self.strip[index_off] = (0, 0, 0, 0) if len(config.color) == 4 else (0, 0, 0)
            self.strip.write()

    def refresh_color_brightness(self):
        for index in self.display:
            self.strip[index] = self.get_color_brightness(config.color, config.brightness)
