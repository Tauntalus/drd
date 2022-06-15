CHAR_MAP = [
    'A',
    'B',
    'C',
    'D',
    'E',
    'F',
    'G',
    'H',
    'I',
    'J',
    'K',
    'L',
    'M',
    'N',
    'O',
    'P',
    'Q',
    'R',
    'S',
    'T',
    'U',
    'V',
    'W',
    'X',
    'Y',
    'Z'
]

MAP_LEN = len(CHAR_MAP)


# stoid - String to ID conversion
# strings are processed using CHAR_MAP to retrieve a decimal conversion of an alphadecimal number
def stoid(s):
    s = s.upper()
    str_len = len(s)
    num = 0

    i = 0
    while i < str_len:
        char = s[i]
        place_val = CHAR_MAP.index(char)

        # Take the exact place value, then multiply it by it's positional value.
        # The positional value ranges from str_len - 1 to 0
        num += place_val * pow(MAP_LEN, str_len - i - 1)
        i += 1

    return num


# idtos - ID to String conversion
# Translate
def idtos(num):
    num_temp = num
    s = ""

    # Build the string by repeated modulo and division of the base number
    while num_temp >= MAP_LEN:
        s = CHAR_MAP[num_temp % MAP_LEN] + s
        num_temp -= num_temp % MAP_LEN
        num_temp = int(num_temp / MAP_LEN)

    # Final character is guaranteed to be between 0-25,
    # So we can just add it to the string
    s = CHAR_MAP[num_temp % MAP_LEN] + s
    return s
