

# stoid - String to ID conversion
def stoid(s, charset):
    s = s.upper()
    base = len(charset)
    str_len = len(s)
    num = 0

    i = 0
    while i < str_len:
        char = s[i]
        place_val = charset.index(char)

        # Take the exact place value, then multiply it by it's positional value.
        # The positional value ranges from str_len - 1 to 0
        num += place_val * pow(base, str_len - i - 1)
        i += 1

    return num


# idtos - ID to String conversion
def idtos(num, charset, ret_size):
    num_temp = num
    base = len(charset)
    s = ""

    # Build the string by repeated modulo and division of the base number
    while num_temp >= base:
        s = charset[num_temp % base] + s
        num_temp -= num_temp % base
        num_temp = int(num_temp / base)

    # Final character is guaranteed to be between 0-25,
    # So we can just add it to the string
    s = charset[num_temp % base] + s

    # Increase size of string if too short
    while len(s) < ret_size:
        s = charset[0] + s
    return s
