import datetime as dt

from RAiDER.models.era5 import ERA5


class ERA5T(ERA5):
    _Name = 'ERA-5T'
    _dataset = 'era5t'
    _expver = '0005'

    # I took this from
    # https://www.ecmwf.int/en/forecasts/documentation-and-support/137-model-levels.
    def __init__(self) -> None:
        super().__init__()

        self._valid_range = (
            dt.datetime(1950, 1, 1).replace(tzinfo=dt.timezone(offset=dt.timedelta())),
            dt.datetime.now(dt.timezone.utc),
        )  # Tuple of min/max years where data is available.
        # Availability lag time in days; actually about 12 hours but unstable on ECMWF side
        # https://confluence.ecmwf.int/display/CKB/ERA5%3A+data+documentation
        # see data update frequency
        self._lag_time = dt.timedelta(days=1)
