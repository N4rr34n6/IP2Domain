import requests
import ipaddress
import sqlite3
from datetime import datetime
from bs4 import BeautifulSoup
import concurrent.futures
import gc
import colorama
import os
from colorama import Fore, Style
from random import choice
import multiprocessing
import json
import time
import subprocess
import socket
import socks
from fake_useragent import UserAgent
import argparse
import random
import itertools

parser = argparse.ArgumentParser(description="Opens IP files and a database.")
parser.add_argument('directory', type=str, help='The directory containing IP files.')
parser.add_argument('db_name', type=str, help='The name of the database to open.')
args = parser.parse_args()

directory = args.directory
files = os.listdir(directory)
file = random.choice(files)
file_path = os.path.join(directory, file)

user_agent_list = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (X11; Linux x86_64; rv:93.0) Gecko/20100101 Firefox/93.0",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko"
]

user_agent_cycle = itertools.cycle(user_agent_list)

delay_range = (0, 0.5)

colorama.init()

def check_tor_service():
    try:
        # Try to connect to Tor's SOCKS5 port
        sock = socket.create_connection(("127.0.0.1", 9050), timeout=5)
        sock.close()
        return True
    except (socket.error, socket.timeout):
        return False

# Check if Tor is active
if not check_tor_service():
    print("Tor service is not active. Make sure Tor is running.")
    exit(1)

# Configure SOCKS5 proxy
socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 9050)
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = 'ALL:@SECLEVEL=0'

# Create a requests session and apply the proxy
session = requests.Session()
session.proxies = {
    'http': 'socks5h://127.0.0.1:9050',
    'https': 'socks5h://127.0.0.1:9050'
}

def ip_generator(cidr_ip):
    ip_network = ipaddress.ip_network(cidr_ip) 
    prefixlen = ip_network._prefixlen 
    for ip in range(int(ip_network.network_address), int(ip_network.broadcast_address) + 1): 
        ip = ipaddress.ip_address(ip) 
        if ip in ip_network: 
            yield f"{ip}" 

def process_ip_pair(ip):
    delay_range = (0, 0.1)
    process_ip(f"http://{ip}") 
    process_ip(f"https://{ip}") 

def get_location_info(ip):
    city_output = subprocess.run(['./mmdbinspect', '-db', 'GeoLite2-City.mmdb', ip], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True).stdout

    isp_output = os.popen(f'./mmdbinspect -db dbip-asn-lite.mmdb {ip}').read()

    city_data = json.loads(city_output)
    isp_data = json.loads(isp_output)

    for record in city_data[0]["Records"]:
        record.setdefault("Record", {})
        record["Record"].setdefault("city", {})
        record["Record"]["city"].setdefault("names", {})
        city = record["Record"]["city"]["names"].get("en", "N/A")
        record["Record"].setdefault("subdivisions", [])
        province = "N/A"
        autonomous_region = "N/A"
        if len(record["Record"]["subdivisions"]) > 0:
            record["Record"]["subdivisions"][0].setdefault("names", {})
            province = record["Record"]["subdivisions"][0]["names"].get("en", "N/A")
        if len(record["Record"]["subdivisions"]) > 1:
            record["Record"]["subdivisions"][1].setdefault("names", {})
            autonomous_region = record["Record"]["subdivisions"][1]["names"].get("en", "N/A")

    if isp_data[0]["Records"] is not None and len(isp_data[0]["Records"]) > 0:
        isp = isp_data[0]["Records"][0]["Record"]["autonomous_system_organization"].replace(",", "")
    else:
        isp = "Unknown"

    return city, province, autonomous_region, isp

with sqlite3.connect("args.db_name") as conn:
    cur = conn.cursor() 

    table_name = "ip_info" 
    columns = [ 
        "protocol", "ip", "status_code", "Date", "Server", "Location", "Content_Type",
        "Keep_Alive", "Connection", "X_Content_Type_Options", "X_Frame_Options",
        "Content_Security_Policy", "X_XSS_Protection", "Strict_Transport_Security", "eTag",
        "Set_Cookie", "Transfer_Encoding", "Content_Length", "Accept_Ranges", "SSL_Errors",
        "Title", "Description", "Content", "Last_Modified", "city", "province", "autonomous_region", "isp"
    ]
    columns_str = ", ".join(columns) 
    create_table_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_str})" 
    cur.execute(create_table_sql) 

    with open(file_path, "r") as file: 
        cidr_list = [line.strip() for line in file] 
    
    random.shuffle(cidr_list) 

    for cidr_ip in cidr_list: 
        ip_list = list(ip_generator(cidr_ip)) 
        random.shuffle(ip_list) 
        for ip in ip_list: 
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S") 
            http_ip = f"http://{ip}" 
            https_ip = f"https://{ip}" 
            print(Fore.GREEN + f"[{timestamp}] Processing IP: {http_ip}" + Style.RESET_ALL) 

            user_agent = next(user_agent_cycle)

            delay = random.uniform(*delay_range)

            try:
                print(f"[{timestamp}] Switching to browser {user_agent}")
                response = requests.head(http_ip, headers={"User-Agent": user_agent, "Connection": "close"}, timeout=(5, 30), stream=True) 
                protocol = "http"  
                status_code = response.status_code 
                headers = response.headers 

                if "text/html" in headers.get("Content-Type", ""): 
                    print(f"[{timestamp}] HTML response detected. Retrieving additional information...") 
                    print(f"[{timestamp}] Waiting {delay} seconds")
                    time.sleep(delay)

                    user_agent = next(user_agent_cycle)

                    delay = random.uniform(*delay_range)
                    print(f"[{timestamp}] Switching to browser {user_agent}")
                    response = requests.get(http_ip, headers={"User-Agent": user_agent, "Connection": "close"}, timeout=(5, 30), stream=True) 
                    soup = BeautifulSoup(response.content, "html.parser") 
                    title = soup.title.string.strip() if soup.title and soup.title.string else "N/A" 
                    description = soup.find("meta", attrs={"name": "description"}) 
                    description = description["content"].strip() if description else "N/A" 
                    content = response.content.decode("utf-8", errors="ignore") 

                    city, province, autonomous_region, isp = get_location_info(ip)

                else: 
                    print(f"[{timestamp}] The response is not HTML. Skipping additional information retrieval.") 
                    title = "N/A" 
                    description = "N/A" 
                    content = "N/A" 

                    city, province, autonomous_region, isp = get_location_info(ip)

                values = [
                    protocol, http_ip, status_code, headers.get("Date", "N/A"), headers.get("Server", "N/A"),
                    headers.get("Location", "N/A"), headers.get("Content-Type", "N/A"),
                    headers.get("Keep-Alive", "N/A"), headers.get("Connection", "N/A"),
                    headers.get("X-Content-Type-Options", "N/A"), headers.get("X-Frame-Options", "N/A"),
                    headers.get("Content-Security-Policy", "N/A"), headers.get("X-XSS-Protection", "N/A"),
                    headers.get("Strict-Transport-Security", "N/A"), headers.get("ETag", "N/A"),
                    headers.get("Set-Cookie", "N/A"), headers.get("Transfer-Encoding", "N/A"),
                    headers.get("Content-Length", "N/A"), headers.get("Accept-Ranges", "N/A"),
                    headers.get("SSL_Errors", "N/A"), title, description, content,
                    headers.get("Last-Modified", "N/A"), city, province, autonomous_region, isp 
                ]

                placeholders = ", ".join(["?" for _ in values]) 
                insert_data_sql = f"INSERT INTO {table_name} VALUES ({placeholders})" 
                cur.execute(insert_data_sql, values) 
                conn.commit() 
                print(Fore.RED + f"[{timestamp}] Data inserted into the database successfully for IP {http_ip}." + Style.RESET_ALL) 

            except requests.exceptions.SSLError as e: 
                ssl_error = str(e).replace('"', '')
                city, province, autonomous_region, isp = get_location_info(ip)
                values = [ 
                    protocol, http_ip, status_code, headers.get("Date", "N/A"), headers.get("Server", "N/A"),
                    headers.get("Location", "N/A"), headers.get("Content-Type", "N/A"),
                    headers.get("Keep-Alive", "N/A"), headers.get("Connection", "N/A"),
                    headers.get("X-Content-Type-Options", "N/A"), headers.get("X-Frame-Options", "N/A"),
                    headers.get("Content-Security-Policy", "N/A"), headers.get("X-XSS-Protection", "N/A"),
                    headers.get("Strict-Transport-Security", "N/A"), headers.get("ETag", "N/A"),
                    headers.get("Set-Cookie", "N/A"), headers.get("Transfer-Encoding", "N/A"),
                    headers.get("Content-Length", "N/A"), headers.get("Accept-Ranges", "N/A"),
                    ssl_error, "N/A", "N/A", "N/A",
                    headers.get("Last-Modified", "N/A"), city, province, autonomous_region, isp 
                ]

                placeholders = ", ".join(["?" for _ in values]) 
                insert_data_sql = f"INSERT INTO {table_name} VALUES ({placeholders})" 
                cur.execute(insert_data_sql, values) 
                conn.commit() 
                print(Fore.RED + f"[{timestamp}] An SSL error occurred. Data inserted into the database with SSL error for IP {http_ip}." + Style.RESET_ALL) 

            except requests.exceptions.ConnectionError as e: 
                print(f"[{timestamp}] The connection with IP {http_ip} has been rejected.") 

            except ConnectionResetError as e: 
                print(f"[{timestamp}] The connection with IP {http_ip} has been interrupted by the server.") 

            except requests.exceptions.Timeout as e:
                print(Fore.RED + f"[{timestamp}] The request with IP {http_ip} has exceeded the time limit", Style.RESET_ALL)

            print(f"[{timestamp}] Waiting {delay} seconds")
            time.sleep(delay)

            user_agent = next(user_agent_cycle)

            delay = random.uniform(*delay_range)

            print(Fore.GREEN + f"[{timestamp}] Processing IP: {https_ip}" + Style.RESET_ALL) 
            try:
                print(f"[{timestamp}] Switching to browser {user_agent}")
                response = requests.head(https_ip, headers={"User-Agent": user_agent, "Connection": "close"}, timeout=(5, 30), stream=True) 
                protocol = "https"  
                status_code = response.status_code 
                headers = response.headers 

                if "text/html" in headers.get("Content-Type", ""): 
                    print(f"[{timestamp}] HTML response detected. Retrieving additional information...") 
                    print(f"[{timestamp}] Waiting {delay} seconds")
                    time.sleep(delay)

                    user_agent = next(user_agent_cycle)

                    delay = random.uniform(*delay_range)
                    print(f"[{timestamp}] Switching to browser {user_agent}")
                    response = requests.get(https_ip, headers={"User-Agent": user_agent, "Connection": "close"}, timeout=(5, 30), stream=True)
                    soup = BeautifulSoup(response.content, "html.parser") 
                    title = soup.title.string.strip() if soup.title and soup.title.string else "N/A" 
                    description = soup.find("meta", attrs={"name": "description"}) 
                    description = description["content"].strip() if description else "N/A" 
                    content = response.content.decode("utf-8", errors="ignore") 

                    city, province, autonomous_region, isp = get_location_info(ip)

                else: 
                    print(f"[{timestamp}] The response is not HTML. Skipping additional information retrieval.") 
                    title = "N/A" 
                    description = "N/A" 
                    content = "N/A" 

                    city, province, autonomous_region, isp = get_location_info(ip)

                values = [
                    protocol, https_ip, status_code, headers.get("Date", "N/A"), headers.get("Server", "N/A"),
                    headers.get("Location", "N/A"), headers.get("Content-Type", "N/A"),
                    headers.get("Keep-Alive", "N/A"), headers.get("Connection", "N/A"),
                    headers.get("X-Content-Type-Options", "N/A"), headers.get("X-Frame-Options", "N/A"),
                    headers.get("Content-Security-Policy", "N/A"), headers.get("X-XSS-Protection", "N/A"),
                    headers.get("Strict-Transport-Security", "N/A"), headers.get("ETag", "N/A"),
                    headers.get("Set-Cookie", "N/A"), headers.get("Transfer-Encoding", "N/A"),
                    headers.get("Content-Length", "N/A"), headers.get("Accept-Ranges", "N/A"),
                    headers.get("SSL_Errors", "N/A"), title, description, content,
                    headers.get("Last-Modified", "N/A"), city, province, autonomous_region, isp 
                ]

                placeholders = ", ".join(["?" for _ in values]) 
                insert_data_sql = f"INSERT INTO {table_name} VALUES ({placeholders})" 
                cur.execute(insert_data_sql, values) 
                conn.commit() 
                print(Fore.RED + f"[{timestamp}] Data inserted into the database successfully for IP {https_ip}." + Style.RESET_ALL) 

            except requests.exceptions.SSLError as e: 
                ssl_error = str(e).replace('"', '')
                city, province, autonomous_region, isp = get_location_info(ip)
                try:
                    values = [ 
                        protocol, https_ip, status_code, headers.get("Date", "N/A"), headers.get("Server", "N/A"),
                        headers.get("Location", "N/A"), headers.get("Content-Type", "N/A"),
                        headers.get("Keep-Alive", "N/A"), headers.get("Connection", "N/A"),
                        headers.get("X-Content-Type-Options", "N/A"), headers.get("X-Frame-Options", "N/A"),
                        headers.get("Content-Security-Policy", "N/A"), headers.get("X-XSS-Protection", "N/A"),
                        headers.get("Strict-Transport-Security", "N/A"), headers.get("ETag", "N/A"),
                        headers.get("Set-Cookie", "N/A"), headers.get("Transfer-Encoding", "N/A"),
                        headers.get("Content-Length", "N/A"), headers.get("Accept-Ranges", "N/A"),
                        ssl_error, "N/A", "N/A", "N/A",
                        headers.get("Last-Modified", "N/A"), city, province, autonomous_region, isp 
                    ]
                except NameError:
                    protocol = "https"
                    status_code = "495/525"
                    headers = {}
                    values = [ 
                        protocol, https_ip, status_code, headers.get("Date", "N/A"), headers.get("Server", "N/A"),
                        headers.get("Location", "N/A"), headers.get("Content-Type", "N/A"),
                        headers.get("Keep-Alive", "N/A"), headers.get("Connection", "N/A"),
                        headers.get("X-Content-Type-Options", "N/A"), headers.get("X-Frame-Options", "N/A"),
                        headers.get("Content-Security-Policy", "N/A"), headers.get("X-XSS-Protection", "N/A"),
                        headers.get("Strict-Transport-Security", "N/A"), headers.get("ETag", "N/A"),
                        headers.get("Set-Cookie", "N/A"), headers.get("Transfer-Encoding", "N/A"),
                        headers.get("Content-Length", "N/A"), headers.get("Accept-Ranges", "N/A"),
                        ssl_error, "N/A", "N/A", "N/A",
                        headers.get("Last-Modified", "N/A"), city, province, autonomous_region, isp 
                    ]

                placeholders = ", ".join(["?" for _ in values]) 
                insert_data_sql = f"INSERT INTO {table_name} VALUES ({placeholders})" 
                cur.execute(insert_data_sql, values) 
                conn.commit() 
                print(Fore.RED + f"[{timestamp}] An SSL error occurred. Data inserted into the database with SSL error for IP {https_ip}." + Style.RESET_ALL) 

            except requests.exceptions.ConnectionError as e: 
                print(f"[{timestamp}] The connection with IP {https_ip} has been rejected.") 

            except ConnectionResetError as e: 
                print(f"[{timestamp}] The connection with IP {https_ip} has been interrupted by the server.") 

            except requests.exceptions.Timeout as e:
                print(Fore.RED + f"[{timestamp}] The request with IP {https_ip} has exceeded the time limit", Style.RESET_ALL)

            print(f"[{timestamp}] Waiting {delay} seconds")
            time.sleep(delay)

            user_agent = next(user_agent_cycle)

            delay = random.uniform(*delay_range)

num_cores = os.cpu_count() 

if num_cores is None: 
    num_cores = 4

num_processes = num_cores * 4 
num_threads = num_cores * 5 

with concurrent.futures.ProcessPoolExecutor(max_workers=num_processes) as executor: 
    ip_generator_list = [ip_generator(cidr_ip) for cidr_ip in cidr_list] 
    while ip_generator_list: 
        ip_generator = choice(ip_generator_list) 
        try:
            ip = next(ip_generator) 
            with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as thread_executor: 
                thread_executor.map(process_ip_pair, ip) 
        except StopIteration: 
            ip_generator_list.remove(ip_generator) 

conn.close()                        
