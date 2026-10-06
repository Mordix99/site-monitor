
import requests 
import json
import time
from datetime import datetime
import csv
import os
import signal
import logging
import sys
from dotenv import load_dotenv
from enum import Enum

load_dotenv()
running = True
class SiteStatus(Enum):
    REACHABLE = "reachable"
    UNREACHABLE = "unreachable"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
# Function to check the status of a website
def check_site(url: str) -> dict:

    site_dict = {
        "timestamp": datetime.now().isoformat(),
        "url": url,
        "status": None,
        "status_code": None,
        "response_time": None,
    }

    try:
        response = requests.get(url, timeout=5)
        if response.status_code < 400:
            site_dict["status"] = SiteStatus.REACHABLE.value
        else:
            site_dict["status"] = SiteStatus.UNREACHABLE.value
        site_dict["status_code"] = response.status_code
        site_dict["response_time"] = response.elapsed.total_seconds()
    except requests.exceptions.RequestException as e:
        site_dict["status"] = SiteStatus.UNREACHABLE.value

    return site_dict

# Function to load configuration from a JSON file
def load_config(config_file="config.json"):
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        logging.error(f"Configuration file {config_file} not found.")
        sys.exit(1)
# Function to save results to a CSV file
def save_to_csv(results,filename):
    # Check if results is empty
    if not results:
        logging.info("No results to save.")
        return
    # Check if the file already exists to determine if we need to write the header
    file_exists = os.path.isfile(filename)
    # Save results to CSV
    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=list(results[0].keys()))
        if not file_exists:
            writer.writeheader()
        writer.writerows(results)

# Function to send a notification to Discord
def send_discord_notification(webhook_url, result,event_type="DOWN"):
    # Check if the webhook URL is provided
    if not webhook_url:
        logging.error("Discord webhook URL is not configured.")
        return

    if event_type == "DOWN":
        title = "Site Down Alert"
    else:
        title = "Site Up Alert"
    # Prepare the message payload
    message = {
        "content": f"***{title}***\nURL: {result['url']}\nStatus: {result['status']}\nStatus Code: {result.get('status_code', 'N/A')}\nResponse Time: {result.get('response_time', 'N/A')} seconds\nTimestamp: {result['timestamp']}"
    }
    try:
        response = requests.post(webhook_url, json=message)
        if response.status_code == 204:
            logging.info(f"Notification sent for {result['url']}")
        else:
            logging.error(f"Failed to send notification for {result['url']}. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error sending notification for {result['url']}: {e}")

def handle_exit(signum, frame):
    logging.info("Program terminated by user.")
    global running
    running = False
    return 

    
    
def main():
    
    config = load_config()
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    
    interval = config.get("check_interval_seconds", 10)
    last_known_status = {}

    while running:
        cycle_results = []
        for url in config["sites"]:
            result = check_site(url)
            cycle_results.append(result)
            logging.info(result)
                
            previous_status = last_known_status.get(url)
            current_status = result["status"]

            
            if current_status == SiteStatus.UNREACHABLE.value and previous_status != SiteStatus.UNREACHABLE.value:
                 send_discord_notification(webhook_url, result, event_type="DOWN")

            
            elif current_status == SiteStatus.REACHABLE.value and previous_status == SiteStatus.UNREACHABLE.value:
                 send_discord_notification(webhook_url, result, event_type="RECOVERED")
            
            last_known_status[url] = current_status

        save_to_csv(cycle_results, "site_status.csv")
        
        for _ in range(interval):
            if not running:
                break
            time.sleep(1)
    
       
  
# Main execution
if __name__ == "__main__":
    signal.signal(signal.SIGTERM, handle_exit)
    signal.signal(signal.SIGINT, handle_exit)
    main()