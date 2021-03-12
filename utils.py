import requests
import logging

BASE_URLS = {
    'state_sites': "https://www.wfas.net/nfmd/ajax/states_map_site_xml.php?state={}",
    'site_data': "https://www.wfas.net/nfmd/public/download_site_data.php?site={}&gacc={}&state={}&grup={}"
}

def stateURL(state, **kargs):
    return BASE_URLS['state_sites'].format(state)

def siteURL(site, gacc, state, grup, **kargs):
    return BASE_URLS['site_data'].format(site,gacc,state,grup)

def getURL(url):
    page = requests.get(url)
    logging.info(page.ok) # assert if the page was OK, if not try again a number of times, and finally exit with an error if not working
    return page
