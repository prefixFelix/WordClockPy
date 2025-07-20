# Language presets.

lang_german = {
    # 0 column  10
    # ESKISTAFÜNF 0
    # ZEHNZWANZIG
    # DREIVIERTEL
    # VORFUNKNACH r
    # HALBAELFÜNF o
    # EINSXAMZWEI w
    # DREIPMJVIER
    # SECHSNLACHT
    # SIEBENZWÖLF
    # ZEHNEUNKUHR 9

    # (row, (column))
    'it_is': (0, (0, 1, 3, 4, 5)),
    'minute_5': (0, (7, 8, 9, 10)),
    'minute_10': (1, (0, 1, 2, 3)),
    'minute_15': (2, (4, 5, 6, 7, 8, 9, 10)),
    'minute_20': (1, (4, 5, 6, 7, 8, 9, 10)),
    'before': (3, (0, 1, 2)),
    'after': (3, (7, 8, 9, 10)),
    'half': (4, (0, 1, 2, 3)),
    'hour_1': (5, (0, 1, 2, 3)),
    'hour_2': (5, (7, 8, 9, 10)),
    'hour_3': (6, (0, 1, 2, 3)),
    'hour_4': (6, (7, 8, 9, 10)),
    'hour_5': (4, (7, 8, 9, 10)),
    'hour_6': (7, (0, 1, 2, 3, 4)),
    'hour_7': (8, (0, 1, 2, 3, 4, 5)),
    'hour_8': (7, (7, 8, 9, 10)),
    'hour_9': (9, (3, 4, 5, 6)),
    'hour_10': (9, (0, 1, 2, 3)),
    'hour_11': (4, (5, 6, 7)),
    'hour_12': (8, (6, 7, 8, 9, 10)),
    'o_clock': (9, (8, 9, 10)),
}

# --- Language dict explanation ---
#
#  Create a new dict with the name of your language and copy all the existing KEYS into it:
#      lang_your_new_language = {...}
#  A key represents a word and the value (nested tuples) represent the coordinates of the letters that make up the individual word.
#  The coordinates always refer to the front plate and are fixed (do not change depending on the LED layout).
#  The exact indices of the LEDs are later automatically derived from these coordinates depending on the layout.
#
#  This represents the coordinates of a german front plate. X:0; Y:0 is always top left.
#  0 column  10
#  ESKISTAFÜNF 0
#  ZEHNZWANZIG
#  DREIVIERTEL
#  VORFUNKNACH r
#  HALBAELFÜNF o
#  EINSXAMZWEI w
#  DREIPMJVIER
#  SECHSNLACHT
#  SIEBENZWÖLF
#  ZEHNEUNKUHR 9
#  All the letters in the word 'ES IST' are positioned at Y-coordinate of 0. 'ES' is be positioned at x-coordinates 0 and 1. 'IST' is at x-coordinates 3, 4, and 5. So the key / value pair looks like this:
#           Y   X  X  X  X  X
# 'it_is': (0, (0, 1, 3, 4, 5)),

