import math

def compute_airmass(alt_degs):
    """
    Compute the airmass value using the Kasten-Young approach.
      m = 1.0 / [ cos(Z) + 0.50572 * (96.07995 - Z)^-1.6364 ]
    This is a more common modern standard, superior to sec(z) or the Hardie methods.

    Returns a value > 1 (typically 1-38).
    """

    z = 90.0 - alt_degs # Zenith angle
    if z < 1.4:
        # At elevations above 88.6, the formula returns values just slightly below 1.
        # (0.9997119 at 89.9999 degs)
        # Here we clamp it to 1
        return 1.0
    if z > 89.95:
        return 38.0

    return 1.0 / (math.cos(math.radians(z)) + 0.50572 * math.pow(96.07995 - z, -1.6364))
