import numpy as np
import pandas as pd
import glob
import scipy.optimize

def my_line(x, a, b):
    return a + b*x

def fit_timeseries(tlist, ylist):
    m, mcov = scipy.optimize.curve_fit(my_line, tlist, ylist, p0=[0, 0])
    velocity = m[1]
    uncertainty = np.sqrt(mcov[1][1])
    return velocity, uncertainty

def fit_tide_gauge(filename):
    t, sea_level = pd.read_csv(filename, sep=";", header=None, skiprows=1, usecols=[0, 1]).values.T
    return fit_timeseries(t, sea_level)
    

def get_coordinates(filename):
    # Column names based on the provided sample format
    columns = ['site', 'YYMMMDD', 'yyyy.yyyy', '__MJD', 'week', 'd', 'reflon', '_e0(m)', '__east(m)', 
               '____n0(m)', '_north(m)', 'u0(m)', '____up(m)', '_ant(m)', 'sig_e(m)', 'sig_n(m)', 
               'sig_u(m)', '__corr_en', '__corr_eu', '__corr_nu', '_latitude(deg)', '_longitude(deg)', '__height(m)']
    
    # Load data using specified column names
    data = pd.read_csv(filename, sep="\s+", names=columns, skiprows=1)
    
    lat = data['_latitude(deg)'].values
    lon = data['_longitude(deg)'].values
    elev = data['__height(m)'].values
    
    return np.mean(lat), np.mean(lon), np.mean(elev)

def fit_velocities(folder, pattern, dtype="GNSS"):
    files = glob.glob(folder + pattern)
    results = []

    for file in files:
        if dtype == "GNSS":
            site_name = file.split('/')[-1].split('.')[0]
            e, n, u = fit_velocities(file)
            results.append({
                'site_name': site_name,
                'e_velocity': e[0], 'e_uncertainty': e[1],
                'n_velocity': n[0], 'n_uncertainty': n[1],
                'u_velocity': u[0], 'u_uncertainty': u[1]
            })
        elif dtype == "tide":
            site_name = file.split('/')[-1].split('.')[0]
            sea_level_rate, uncertainty = fit_tide_gauge(file)
            results.append({
                'site_name': site_name,
                'sea_level_rate': sea_level_rate,
                'uncertainty': uncertainty
            })
            
def fit_all_velocities(folder, pattern):
    files = glob.glob(folder + pattern)
    results = []

    for file in files:
        site_name = file.split('/')[-1].split('.')[0]
        coords = get_coordinates(file)
        e, n, u = fit_velocities(file)
        
        results.append({
            'site_name': site_name,
            'latitude': coords[0],
            'longitude': coords[1],
            'elevation': coords[2],
            'e_velocity': e[0], 'e_uncertainty': e[1],
            'n_velocity': n[0], 'n_uncertainty': n[1],
            'u_velocity': u[0], 'u_uncertainty': u[1]
        })            
        
    return pd.DataFrame(results)
