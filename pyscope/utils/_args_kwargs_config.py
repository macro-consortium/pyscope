def _kwargs_to_config(kwargs):
    if kwargs is None or len(kwargs) == 0:
        return ""
    string = ""
    for key, value in kwargs.items():
        string += str(key) + "=" + str(value) + ","
    return string[:-1]
