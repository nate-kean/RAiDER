import datetime
from pathlib import Path

import numpy as np
import pytest

from RAiDER.checkArgs import makeDelayFileNames
from RAiDER.cli.raider import calcDelays
from RAiDER.losreader import Zenith
from RAiDER.utilFcns import rio_open, write_yaml
from test import TEST_DIR


SCENARIO_DIR = TEST_DIR / 'scenario_1'
WM_LOC = SCENARIO_DIR / 'weather_files'
_RTOL = 1e-2


@pytest.mark.long
@pytest.mark.parametrize('model_name', ['GMAO', 'NCMR', 'MERRA2', 'ERA5T', 'ERA5'])
def test_tropo_delay(tmp_path: Path, model_name) -> None:
    """
    Scenario:
    1: Small area, Zenith delay.
    """
    if model_name == 'NCMR':
        time = datetime.datetime(2018, 7, 1, 0, 0)
    else:
        time = datetime.datetime(2020, 1, 3, 23, 0)

    WM_LOC.mkdir(exist_ok=True)

    args = {
        'weather_model': model_name,
        'date_group': {
            'date_start': time.strftime('%Y%m%d'),
        },
        'time_group': {
            'time': time.strftime('%H:%M:%S'),
        },
        'aoi_group': {
            'lat_file': str(SCENARIO_DIR / 'geom/lat.dat'),
            'lon_file': str(SCENARIO_DIR / 'geom/lon.dat'),
        },
        'los_group': {
            'zref': 20_000.0,
        },
        'runtime_group': {
            'verbose': True,
            'output_directory': str(tmp_path),
            'weather_model_directory': str(WM_LOC),
            'download_only': False,
        },
    }
    # args['ll_bounds'] = (15.75, 18.25, -103.24, -99.75)
    # args['heights'] = ('dem', str(TEST_DIR / 'test_geom/warpedDEM.dem'))
    # args['pnts_file'] = 'lat_query_points.h5'
    # args['flag'] = 'files'

    config_path = tmp_path / 'run_config.yaml'
    write_yaml(args, config_path)
    calcDelays([str(config_path)])

    # get the results
    wet_filename, hydro_filename = makeDelayFileNames(time, Zenith(), 'envi', model_name, tmp_path)
    wet, _ = rio_open(wet_filename)
    hydro, _ = rio_open(hydro_filename)
    true_wet, _ = rio_open(SCENARIO_DIR / f'{model_name}/wet.envi', userNDV=0.0)
    true_hydro, _ = rio_open(SCENARIO_DIR / f'{model_name}/hydro.envi', userNDV=0.0)

    # get the true delay from the weather model
    assert np.nanmax(np.abs((wet - true_wet) / true_wet)) < _RTOL
    assert np.nanmax(np.abs((hydro - true_hydro) / true_hydro)) < _RTOL
