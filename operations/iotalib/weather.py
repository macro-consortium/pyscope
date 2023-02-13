import ephem

class WeatherReading:
    def __init__(self):
        self.wind_speed_kph = None
        self.wind_direction_degs_east_of_north = None
        self.temperature_celsius = None
        self.pressure_millibars = None
        self.humidity_percent = None
        self.timestamp_jd = None

    def age_seconds(self):
        if self.timestamp_jd is None:
            return None

        jd_now = ephem.julian_date(ephem.now())
        return (jd_now - self.timestamp_jd) * 86400.0


    def __str__(self):
        result = "wind_speed_kph: %s\n" % self.wind_speed_kph
        result += "wind_direction_degs_east_of_north: %s\n" % self.wind_direction_degs_east_of_north
        result += "temperature_celsius: %s\n" % self.temperature_celsius
        result += "pressure_millibars: %s\n" % self.pressure_millibars
        result += "humidity_percent: %s\n" % self.humidity_percent
        result += "age_seconds(): %s\n" % self.age_seconds()

        return result