def _args_to_config(self, args):
    if args is None or len(args) == 0:
        return ""
    string = ""
    for arg in args:
        string += str(arg) + " "
    return string[:-1]


def _kwargs_to_config(self, kwargs):
    if kwargs is None or len(kwargs) == 0:
        return ""
    string = ""
    for key, value in kwargs.items():
        string += str(key) + ":" + str(value) + " "
    return string[:-1]
