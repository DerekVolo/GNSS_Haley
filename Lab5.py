import numpy as np
import pandas as pd
import glob
import scipy.optimize

def my_line(x, a, b):
    return a + b*x

def fit_timeseries(tlist, ylist):
    m, mcov = scipy.optimize.curve_fit(my_line, tlist, ylist, p0=[0, 0])
    velocity = m[1]
    sigma = np.std(residuals, ddof=2)
    return velocity, sigma

def fit_tide_gauge(filename):
    t, sea_level = pd.read_csv(filename, sep=";", header=None, skiprows=1, usecols=[0, 1]).values.T
    return fit_timeseries(t, sea_level)
    
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

    return pd.DataFrame(results)