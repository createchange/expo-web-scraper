import requests
import urllib
import re
from bs4 import BeautifulSoup
import csv
import time
import sys

def get_part_list():
    part_list = "https://s36.a2zinc.net/clients/sme/Fabtech2019/Public/Exhibitors.aspx?_ga=2.260747789.1815559995.1542037203-1539468774.1539700027"
    url_content = []
    response = requests.get(part_list)
    data = response.text
    output = data.split('\n')
    for line in output:
        if "exhibitor" in line and "eBooth" in line:
                matchResult = re.search('(?<=href=")(.*)(?=")', line)
                if matchResult:
                    url_content.append(matchResult.group(1))

    updated_urls = []
    for url in url_content:
        updated_urls.append(url.replace("&amp;", "&"))
    
    return updated_urls


def get_part_info(part_list):
    site_list = []
    for part in part_list[:100]:
        full_url = "https://s36.a2zinc.net/clients/sme/Fabtech2019/Public/" + part
        response = requests.get(full_url)
        data = response.text
        parsed_html = BeautifulSoup(data, features="html.parser")
        site = parsed_html.body.find('div', attrs={'class': 'panel-body'}).find("h1").get_text().strip()
        try:
            url = (parsed_html.find(id="BoothContactUrl").get_text())
        except AttributeError:
            url = "No website data provided"
        site_list.append([site,url])
        sys.stdout.write("\r# Scraped: " + str(len(site_list)))
        sys.stdout.flush()
    return site_list


def write_csv(site_list):
    header = ['company', 'url']

    with open('fab-leads.csv', 'wt') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(header)
        for site in site_list:
            csv_writer.writerow(site)

part_list = get_part_list()

t0 = time.time()

site_list = get_part_info(part_list)

t1 = time.time()
total = t1-t0

print("\n\nSeconds to scrape: " + str(round(total,2)))
#write_csv(site_list)
