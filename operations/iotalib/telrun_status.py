previous_scan = None
current_scan = None
next_scan = None

log_lines = []

# This gets replaced with a reference to a function that
# will return the current sun elevation at the observatory
sun_elevation_func = None

# This gets replaced with a reference to a function that
# will return the latest weather reading
get_weather_func = None

mount_state = "unknown"
camera_state = "unknown"
autofocus_state = "unknown"
current_scan_number = 0
total_scan_count = 0
skipped_scan_count = 0
next_autofocus_time = 0

