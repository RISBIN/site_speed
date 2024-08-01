import requests
import time
import socket
from datetime import datetime
from prettytable import PrettyTable

# Get URL from user
MONITORED_URL = input("Enter the URL of the website to monitor: ")
CHECK_INTERVAL = 60  # Check every 60 seconds

# State tracking
website_down_since = None
website_up_since = None

def get_website_info(url):
    try:
        # Measure the time taken to get a response
        start_time = time.time()
        response = requests.get(url)
        end_time = time.time()
        response_time = end_time - start_time

        # Extract server information
        server = response.headers.get('Server', 'Unknown')

        # Resolve all IP addresses
        domain = url.split('//')[-1].split('/')[0]
        ip_addresses = socket.gethostbyname_ex(domain)[2]
        
        return response_time, server, ip_addresses

    except requests.RequestException as e:
        return None, None, None

def get_speed_status(response_time):
    if response_time is None:
        return "Unknown"
    elif response_time < 1:
        return "Fast"
    elif response_time < 2:
        return "Medium"
    else:
        return "Slow"

def display_status(response_time, server, ip_addresses, status, downtime_duration=None):
    table = PrettyTable()
    if status == "Down":
        table.field_names = ["Metric", "Value"]
        table.add_row(["Status", "Down"])
    else:
        speed_status = get_speed_status(response_time)
        table.field_names = ["Metric", "Value"]
        table.add_row(["Status", "Up"])
        table.add_row(["Response Time", f"{response_time:.2f} seconds"])
        table.add_row(["Speed Status", speed_status])
        table.add_row(["Server", server])
        table.add_row(["IP Addresses", ", ".join(ip_addresses)])
        if downtime_duration:
            table.add_row(["Downtime Duration", f"{downtime_duration}"])

    # Print the table
    print("Website Monitoring Status")
    print(table.get_string(border=True))

def check_website():
    global website_down_since, website_up_since
    try:
        response_time, server, ip_addresses = get_website_info(MONITORED_URL)
        if response_time is None:
            if website_up_since is not None:
                downtime_duration = datetime.now() - website_up_since
                display_status(None, None, None, "Down", downtime_duration)
                website_down_since = datetime.now()
                website_up_since = None
            else:
                if website_down_since is None:
                    website_down_since = datetime.now()
                display_status(None, None, None, "Down")
        else:
            if website_down_since is not None:
                downtime_duration = datetime.now() - website_down_since
                display_status(response_time, server, ip_addresses, "Up", downtime_duration)
                website_down_since = None
                website_up_since = datetime.now()
            else:
                display_status(response_time, server, ip_addresses, "Up")
    except requests.RequestException as e:
        if website_up_since is not None:
            downtime_duration = datetime.now() - website_up_since
            display_status(None, None, None, "Down", downtime_duration)
            website_down_since = datetime.now()
            website_up_since = None
        else:
            if website_down_since is None:
                website_down_since = datetime.now()
            display_status(None, None, None, "Down")

if __name__ == '__main__':
    while True:
        check_website()
        time.sleep(CHECK_INTERVAL)