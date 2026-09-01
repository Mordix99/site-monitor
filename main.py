import requests 
import json
import time
from datetime import datetime
import csv
import os



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


# Main execution
if __name__ == "__main__":
    # Load configuration
    config = load_config()

    try:
        # Set the check interval from the configuration, defaulting to 10 seconds if not specified
        interval = config.get("check_interval_seconds", 10)
        while True:
            # Perform the site checks and save results to CSV
            cycle_results=[]
            for url in config["sites"]:
                result = check_site(url)
                cycle_results.append(result)
                print(result)
            save_to_csv(cycle_results, "site_status.csv")
            print("-" * 40)
            time.sleep(interval)
    except KeyboardInterrupt:
        print("Program terminated by user.")
       
  
