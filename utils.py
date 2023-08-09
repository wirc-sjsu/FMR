import requests
import logging
import numpy as np

# Base URLs from NFMD website
BASE_URLS = {
    'gacc_sites': "https://www.wfas.net/nfmd/ajax/gacc_map_site_xml.php?gacc={}",
    'state_sites': "https://www.wfas.net/nfmd/ajax/states_map_site_xml.php?state={}",
    'site_data': "https://www.wfas.net/nfmd/public/download_site_data.php?site={}&gacc={}&state={}&grup={}"
}

# All available GACCs in NFMD website
_GACCS = ['AICC', 'EACC', 'EGBC', 'NICC', 'NOCC', 'NRCC', 'NRCC', 
        'NWCC', 'RMCC', 'SACC', 'SOCC', 'SWCC', 'WGBC']

# All available States in the NFMD website
_STATES = [
    'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME',
    'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA',
    'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY']

# Construct GACCs URL
#
# @ Param gacc - gacc to construct the URL for
#
def gaccURL(gacc, **kargs):
    return BASE_URLS['gacc_sites'].format(gacc)

# Construct State URL
#
# @ Param state - state to construct the URL for
#
def stateURL(state, **kargs):
    return BASE_URLS['state_sites'].format(state)

# Construct Site URL
#
# @ Param site - site to construct the URL for
# @ Param gacc - gacc to construct the URL for
# @ Param state - state to construct the URL for
# @ Param grup - grup to construct the URL for
#
def siteURL(site, gacc, state, grup, **kargs):
    return BASE_URLS['site_data'].format(site,gacc,state,grup)

# Request page with retrying using requests package
#
# @ Param url - URL to get the page from
# @ Param max_retries - maximum number of retries
#
def getURL(url, max_retries=10):
    while max_retries:
        try:
            page = requests.get(url)
            if page.ok:
                return page
            else:
                logging.warning('NFMD is returning status {}'.format(page.status_code))
        except Exception as e:
            logging.error('NFMD is not responding')
        max_retries -= 1
        logging.warning('Reconnecting, {} retries'.format(max_retries))

# Split fuel column into type and variation
#
# @ Param df - dataframe with fuel column to be splitted
#
def split_fuel(df):
    split = df['fuel'].str.split(',', n=1, expand=True)
    if len(split.columns) == 1:
        split.columns = ['fuel_type']
        split['fuel_variation'] = None
        split['fuel_type'] = split['fuel_type'].str.strip()
    elif len(split.columns) == 2:
        split.columns = ['fuel_type', 'fuel_variation']
        split['fuel_type'] = split['fuel_type'].str.strip()
        split['fuel_variation'] = split['fuel_variation'].str.strip()
    else:
        logging.error('Error in number of splitted columns: {}'.format(split))
    return split

# Check coordinates and return properly coordinates
#
# @ Param latitude1,latitude2,longitude1,longitude2 - geographical coordinates in WGS84 degrees
#
def check_coords(latitude1, latitude2, longitude1, longitude2):
    valid_coords = lambda y1,y2,x1,x2: -90 < y1 < 90 and -90 < y2 < 90 and -180 < x1 < 180 and -180 < x2 < 180
    if any([latitude1 is None, latitude2 is None, longitude1 is None, longitude2 is None]) or not valid_coords(latitude1,latitude2,longitude1,longitude2):
        return None,None,None,None
    if latitude1 < latitude2:
        lat1 = latitude1
        lat2 = latitude2
    else:
        lat1 = latitude2
        lat2 = latitude1
    if longitude1 < longitude2:
        lon1 = longitude1
        lon2 = longitude2
    else:
        lon1 = longitude2
        lon2 = longitude1
    return lat1,lat2,lon1,lon2

# Filter outliers in pandas dataframe in terms of fuel moisture
#
# @ Param df - dataframe with percent column to be cleaned of outliers
#
def filter_outliers(df):
    conditions = np.logical_or(df['percent'] > 400, df['percent'] < 0).astype(bool)
    df.loc[conditions, 'percent'] = np.nan
    return df
