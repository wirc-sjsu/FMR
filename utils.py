import requests
import logging

BASE_URLS = {
    'gacc_sites': "https://www.wfas.net/nfmd/ajax/gacc_map_site_xml.php?gacc={}",
    'state_sites': "https://www.wfas.net/nfmd/ajax/states_map_site_xml.php?state={}",
    'site_data': "https://www.wfas.net/nfmd/public/download_site_data.php?site={}&gacc={}&state={}&grup={}"
}

_GACCS = ['AICC', 'EACC', 'EGBC', 'NICC', 'NOCC', 'NRCC', 'NRCC', 
        'NWCC', 'RMCC', 'SACC', 'SOCC', 'SWCC', 'WGBC']

def gaccURL(gacc, **kargs):
    return BASE_URLS['gacc_sites'].format(gacc)

def stateURL(state, **kargs):
    return BASE_URLS['state_sites'].format(state)

def siteURL(site, gacc, state, grup, **kargs):
    return BASE_URLS['site_data'].format(site,gacc,state,grup)

def getURL(url, max_retries=10):
    while max_retries:
        try:
            page = requests.get(url)
            if page.ok:
                return page
            else:
                logging.warning('NFMDB is returning status {}'.format(page.status_code))
        except Exception as e:
            logging.error('NFMDB is not responding')
        max_retries -= 1
        logging.warning('Reconnecting, {} retries'.format(max_retries))
        

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