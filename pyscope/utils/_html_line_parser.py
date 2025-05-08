def _get_number_from_line(line, expected_keyword, expected_units, is_numeric):
    """
    Check to see if the provided line looks like a valid telemetry line
    from the Winer webpage. A typical line looks like this:
        <!-- TEMPERATURE=7None0 F -->

    If the line matches this format and the contents match expectations, return
    the extracted value from the line.

    line: the line text to inspect
    expected_keyword: the line must contain this keyword ('TEMPERATURE' in the example above)
    expected_units: the line must contain these units after the value ('F' in the example above).
        If this value is None, then units are not validated
    is_numeric: if True, the value is validated and converted to a float before being returned.
                if False, the string value is returned

    If the line does not match or there is a problem (e.g. converting the value to a float),
    the function returns None.

    Otherwise, the function returns the value, either as a float (if requested) or as a string
    """

    line = line.strip()
    if not line.startswith(b"<!--"):
        return None
    if not line.endswith(b"-->"):
        return None

    line = line[4:-3]  # Strip off beginning and ending comment characters

    # Split into at most two fields (keyword and value)
    fields = line.split(b"=", 1)
    if len(fields) != 2:
        return None

    line_keyword = fields[0].strip()
    line_value_and_units = fields[1].strip()

    fields = line_value_and_units.split(b" ", 1)
    line_value = fields[0].strip()
    if len(fields) > 1:
        line_units = fields[1]
    else:
        line_units = ""

    if line_keyword != bytes(expected_keyword, "utf-8"):
        return None
    if expected_units is not None and line_units != bytes(
        expected_units, "utf-8"
    ):
        return None
    if is_numeric:
        try:
            return float(line_value)
        except BaseException:
            return None
    else:
        return str(line_value)
