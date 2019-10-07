import requests
import urllib
import re
from bs4 import BeautifulSoup
import csv
import threading
from time import sleep
import sys
import time


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


def get_part_info(part):
    full_url = "https://s36.a2zinc.net/clients/sme/Fabtech2019/Public/" + part
    response = requests.get(full_url)
    data = response.text
    parsed_html = BeautifulSoup(data, features="html.parser")
    site = parsed_html.body.find('div', attrs={'class': 'panel-body'}).find("h1").get_text().strip()
    try:
        url = (parsed_html.find(id="BoothContactUrl").get_text())
    except AttributeError:
        url = "No website data provided"

    return [site,url]


def write_csv(results):
    header = ['company', 'url']

    with open('fab-leads.csv', 'wt') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(header)
        for result in results:
            csv_writer.writerow(result)
    print("\nOutput file: 'fab-leads.csv'")


def write_benchmark_file(results):
    x = 0
    with open('benchmark-results.txt', 'wt') as f:
        for result in results:
            x+=1
            f.write(str("%s. " % x + result[0]) + ": " + (result[1] + "\n"))
    print("\nOutput file: 'benchmark-results.txt'")


def wrapper(func, args, res):
        res.append(func(*args))


print("Fetching links to participant pages...")
participant_urls = get_part_list()
print("Complete.\n")
print("Entries to scrape: " + str(len(participant_urls)))

print("1. Full Scrape")
print("2. Benchmark (scrape 100)\n")
full_or_benchmark = input("Please select\n> ")

print("\nNow scraping...")

# initialize results list, which will be a list of lists[site,url]
res = []

if full_or_benchmark == "1": 
    threads = [threading.Thread(target=wrapper, args=(get_part_info, (url,), res)) for url in participant_urls]
elif full_or_benchmark == "2":
    threads = [threading.Thread(target=wrapper, args=(get_part_info, (url,), res)) for url in participant_urls[:100]]

# start scraping
t0 = time.time()

for thread in threads:
    thread.start()

for thread in threads:
    thread.join()
    sys.stdout.write("\r# Scraped: " + str(len(res)))
    sys.stdout.flush()

t1 = time.time()
total = t1-t0

print("\n\nScraped %s items in %s seconds" % (len(res), str(round(total,2))))

if full_or_benchmark == "1":
    write_csv(res)
if full_or_benchmark == "2":
    write_benchmark_file(res)
