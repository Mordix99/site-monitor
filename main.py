
import requests 
import json
import time
from datetime import datetime
import csv
import os
from dotenv import load_dotenv

load_dotenv()

# Function to check the status of a website
def check_site(url):

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
            site_dict["status"] = "reachable"
            site_dict["status_code"] = response.status_code
            site_dict["response_time"] = response.elapsed.total_seconds()
        else:
            site_dict["status"] = "unreachable"
            site_dict["status_code"] = response.status_code
            site_dict["response_time"] = response.elapsed.total_seconds()
    except requests.exceptions.RequestException as e:
        site_dict["status"] = "unreachable"

    return site_dict

# Function to load configuration from a JSON file
def load_config(config_file="config.json"):
    with open(config_file, 'r') as f:
        config = json.load(f)
    return config
# Function to save results to a CSV file
def save_to_csv(results,filename):
    # Check if results is empty
    if not results:
        print("No results to save.")
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
        print("Discord webhook URL is not configured.")
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
            print(f"Notification sent for {result['url']}")
        else:
            print(f"Failed to send notification for {result['url']}. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending notification for {result['url']}: {e}")


# Main execution
if __name__ == "__main__":
    # Load configuration and get the Discord webhook URL
    config = load_config()
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    
    
#  
    try:
        # Set the check interval from the configuration, defaulting to 10 seconds if not specified
        interval = config.get("check_interval_seconds", 10)
        # Initialize a dictionary to keep track of the last known status of each site
        last_known_status = {}

        while True:
            # Perform the site checks and save results to CSV
            cycle_results = []
            for url in config["sites"]:
                result = check_site(url)
                cycle_results.append(result)
                print(result)
                
                previous_status = last_known_status.get(url)
                current_status = result["status"]

                # Check for status changes and send notifications accordingly
                if current_status == "unreachable" and previous_status != "unreachable":
                    send_discord_notification(webhook_url, result, event_type="DOWN")

                elif current_status == "reachable" and previous_status == "unreachable":
                    send_discord_notification(webhook_url, result, event_type="RECOVERED")
                # Update the last known status for the site
                last_known_status[url] = current_status

            # Save the results of the current cycle to a CSV file    
            save_to_csv(cycle_results, "site_status.csv")
            print("-" * 40)
            # Wait for the specified interval before the next check
            time.sleep(interval)
    except KeyboardInterrupt:
        print("Program terminated by user.")
       
  
