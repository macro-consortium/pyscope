import ephem

"""
Print the current Julian Day (JD) to the console
"""

print(ephem.julian_date(ephem.now()))