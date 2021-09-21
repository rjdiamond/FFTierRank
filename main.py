import argparse
import requests
from lxml import html
import traceback
import os
import logging
import logging.handlers
import datetime
import sys
import csv
from threading import Timer
#import numpy as np
#from sklearn.cluster import KMeans
#import matplotlib.pyplot as plt
#from matplotlib.pyplot import cm
#from matplotlib import style
#style.use("ggplot")
from bs4 import BeautifulSoup

"""
python /home/ubuntu/projects/fftierrank/src/fp_dl.py -u https://www.fantasypros.com/nfl/rankings/half-point-ppr-flex.php?week=1\\&export=xls 
-d ~/projects/fftierrank/dat/2017/week-1-half-point-ppr-flex-raw.txt 
-c ~/projects/fftierrank/dat/2017/week-1-half-point-ppr-flex-raw.csv -n 9
infile = '/home/ubuntu/projects/fftierrank/dat/2017/week-1-half-point-ppr-flex-raw.txt'
outfile = '/home/ubuntu/fftierrank/dat/2017/week-1-half-point-ppr-flex-raw.csv'
'flex' in outfile
ncol = 9
"""

def convertTxtToCsv(infile, outfile, ncol=8):
    ncol = 8
    if 'flex' in outfile:
        ncol = 9
    file = open(infile, 'r') 
    text = file.read() 
    soup = BeautifulSoup(text)
    tables = soup.findAll("table")
    table = tables[0]
    headings = [th.get_text().strip() for th in table.find("tr").find_all("th")]    
    fout = open(outfile, 'w')
    fout.write(','.join(headings[:-1]) + '\n')
    rows = []
    count = 1
    for row in table.find_all("tr")[1:]:
        try:
            count += 1
            nextrow = [td.get_text() for td in row.find_all("td")]
            if (int(len(nextrow)) >= ncol) and (count > 1):
                line = ','.join(nextrow[:int(ncol-1)])
                line = line.replace(' \n', '')
                fout.write(line + '\n')
                rows.append(nextrow)
        except:
            pass
    fout.close()
    return

def perform_session_download(args, url, full_file_name):
    """
    creates a session that allows the user to log in to FantasyPros and use the tokens
    :param args: list of parameters can be used to get data directories
    :param url: string of the export xls url
    :param full_file_name: string of the full file path and name of file to be saved
    """
    logger = logging.getLogger()
    # get payload values from command line parameters
    username, password, token = args['username'], args['password'], args['token']
    payload = {"username": username,
               "password": password,
               "csrfmiddlewaretoken": token}
    # start session
    print "Starting download session..."
    logger.debug("Starting download session...")
    session_requests = requests.session()
    login_url = "https://secure.fantasypros.com/accounts/login/?"
    result = session_requests.get(login_url)
    # refresh token on new request
    tree = html.fromstring(result.text)
    logger.debug("Updating token...")
    authenticity_token = list(set(tree.xpath("//input[@name='csrfmiddlewaretoken']/@value")))[0]
    payload["csrfmiddlewaretoken"] = authenticity_token
    session_requests.post(login_url,
                          data=payload,
                          headers=dict(referer=login_url))
    # prepare to write data to file
    #logger.debug("Opening xls file to write data...")
    with open(full_file_name, 'wb') as handle:
        response = session_requests.get(url)
        if not response.ok:
            logger.info("Writing to xls failed...")
        for block in response.iter_content(1024):
            handle.write(block)
        logger.info("Writing to xls succeeded...")


if __name__ == "__main__":    # get all of the commandline arguments
    """
    python /Users/rjd/projects/fftierrank/src/fp_dl.py -u https://www.fantasypros.com/nfl/rankings/consensus-cheatsheets.php?export=xls -d /Users/borischen/projects/fftiers/dat/2016/week-0-all-raw.xls
    python /home/ubuntu/projects/fftierrank/src/fp_dl.py -u https://www.fantasypros.com/nfl/rankings/consensus-cheatsheets.php?export=xls -d /home/ubuntu/projects/fftiers/dat/2016/week-0-all-raw.xls
    """
    parser = argparse.ArgumentParser("FantasyPros clustering program")
    parser.add_argument('-u', dest='url', help="FantasyPros url", required=True)
    parser.add_argument('-d', dest='full_file_name', help="Destination", required=True)
    parser.add_argument('-c', dest='csv_file_name', help="CSV Destination", required=True)
    parser.add_argument('-n', dest='ncol', help="number of columns", required=True)
    userargs = {'username':'rjd105', 'password':'pw12345', 'token':'1'}
    #url = 'https://www.fantasypros.com/nfl/rankings/consensus-cheatsheets.php?export=xls'
    #full_file_name = '/Users/rjd/projects/fftierrank/dat/2016/week-0-all-raw.xls'
    args = parser.parse_args()
    url = args.url
    full_file_name = args.full_file_name
    csv_file_name = args.csv_file_name
    ncol = args.ncol
    perform_session_download(userargs, url, full_file_name)
    convertTxtToCsv(full_file_name, csv_file_name, ncol)
