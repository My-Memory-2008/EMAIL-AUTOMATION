import time
import subprocess
import sys
import os
import requests
from datetime import datetime, timedelta

# --- Configuration ---
# Path to your main email processing script
EMAIL_SCRIPT_PATH = "email_scanner.py"
# Desired interval between checks/runs in seconds (30 minutes = 30 * 60 seconds)
INTERVAL_SECONDS = 30 * 60
# Maximum allowed time since last *scheduler check* in seconds (5 hours = 5 * 60 * 60 seconds)
MAX_TIME_SINCE_LAST_CHECK = 5 * 60 * 60
# File to store the timestamp of the last successful run
TIMESTAMP_FILE = "last_run_timestamp.txt"
# --- GitHub Workflow Configuration ---
# Repository owner (username or organization name)
REPO_OWNER = os.getenv("REPO_OWNER") # Recommended: Set via environment variable
# Repository name
REPO_NAME = os.getenv("REPO_NAME")   # Recommended: Set via environment variable
# Workflow file name (e.g., "scheduler-controller.yml")
WORKFLOW_FILE_NAME = "scheduler-controller.yml"
# GitHub Personal Access Token (PAT) with repo scope
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN") # Recommended: Set via environment variable
# Branch name where the workflow file resides
BRANCH_NAME = "main" # Change if your workflow is on a different branch

if not all([REPO_OWNER, REPO_NAME, WORKFLOW_FILE_NAME, GITHUB_TOKEN]):
    print("Error: Missing required environment variables for GitHub workflow dispatch.")
    print("Ensure REPO_OWNER, REPO_NAME, GITHUB_TOKEN are set.")
    sys.exit(1)

def load_last_run_time():
    """Loads the timestamp of the last successful run from the file."""
    if os.path.exists(TIMESTAMP_FILE):
        try:
            with open(TIMESTAMP_FILE, "r") as f:
                timestamp_str = f.read().strip()
                if timestamp_str:
                    return datetime.fromisoformat(timestamp_str)
        except (ValueError, OSError) as e:
            print(f"Warning: Could not load last run time from {TIMESTAMP_FILE}: {e}. Assuming no previous run.")
            return None
    return None

def save_run_time(run_time):
    """Saves the timestamp of the current run to the file."""
    try:
        with open(TIMESTAMP_FILE, "w") as f:
            f.write(run_time.isoformat())
    except OSError as e:
        print(f"Error: Could not save run time to {TIMESTAMP_FILE}: {e}")

def run_email_script():
    """Executes the main email processing script."""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting email processing script...")
    try:
        # Execute the email scanner script
        result = subprocess.run([sys.executable, EMAIL_SCRIPT_PATH], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Email processing script completed successfully.")
            print("STDOUT:", result.stdout)
            if result.stderr: # Print stderr if there was any, even if return code is 0
                print("STDERR:", result.stderr)
            return True
        else:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Email processing script failed with return code {result.returncode}.")
            print("STDOUT:", result.stdout) # Print stdout even if it failed
            print("STDERR:", result.stderr)
            return False
            
    except FileNotFoundError:
        print(f"Error: Email processing script '{EMAIL_SCRIPT_PATH}' not found.")
        return False
    except Exception as e:
        print(f"Error running email script: {e}")
        return False

def trigger_github_workflow():
    """Triggers the GitHub Actions workflow using the GitHub API."""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Attempting to trigger GitHub workflow '{WORKFLOW_FILE_NAME}' on branch '{BRANCH_NAME}'...")
    
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/workflows/{WORKFLOW_FILE_NAME}/dispatches"
    
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Python-Scheduler" # Good practice to identify your client
    }
    
    payload = {
        "ref": BRANCH_NAME,
        # You can add optional inputs for the workflow here if needed
        # "inputs": {
        #     "example_input": "value"
        # }
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status() # Raises an HTTPError for bad responses (4xx or 5xx)
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] GitHub workflow dispatch request sent successfully.")
        print(f"Response Status Code: {response.status_code}")
        print(f"Response Text: {response.text}")
        return True
    except requests.exceptions.HTTPError as he:
        print(f"HTTP Error triggering workflow: {he.response.status_code} - {he.response.text}")
    except requests.exceptions.RequestException as re:
        print(f"Request Error triggering workflow: {re}")
    except Exception as e:
        print(f"Unexpected error triggering workflow: {e}")
    return False


def main():
    """Main scheduling loop."""
    print("Scheduler started. Checking every 30 minutes or if 5 hours have passed since last check.")
    last_check_time = datetime.now() # Initialize the time of the first check

    while True:
        current_time = datetime.now()
        time_since_last_check = (current_time - last_check_time).total_seconds()

        should_run_script = False
        should_trigger_workflow = False
        reason_script = ""
        reason_workflow = ""

        # --- Logic for Email Script Run ---
        last_run_time = load_last_run_time()
        if last_run_time is None:
            should_run_script = True
            reason_script = "First run - no previous timestamp found."
        else:
            time_since_last_run = (current_time - last_run_time).total_seconds()
            if time_since_last_run >= INTERVAL_SECONDS:
                should_run_script = True
                reason_script = f"Scheduled 30 minutes have passed since the last run."
            elif time_since_last_run >= MAX_TIME_SINCE_LAST_RUN:
                should_run_script = True
                reason_script = f"Maximum time threshold (5 hours) exceeded since last run."

        # --- Logic for Workflow Trigger ---
        if time_since_last_check >= MAX_TIME_SINCE_LAST_CHECK:
             should_trigger_workflow = True
             reason_workflow = f"Maximum time threshold (5 hours) exceeded since last scheduler check."

        if should_run_script:
            print(f"Triggering email script: {reason_script}")
            success = run_email_script()
            if success:
                # Only save the time if the script ran successfully
                save_run_time(current_time)
                print(f"Email script run completed at {current_time.strftime('%Y-%m-%d %H:%M:%S')}.")
            else:
                print("Email script run failed.")

        if should_trigger_workflow:
            print(f"Triggering GitHub workflow: {reason_workflow}")
            workflow_success = trigger_github_workflow()
            if workflow_success:
                 print(f"Workflow dispatch successful. Terminating scheduler in 10 seconds...")
                 time.sleep(10) # Wait 10 seconds
                 print("Scheduler terminating now.")
                 sys.exit(0) # Exit the script successfully
            else:
                 print("Failed to trigger GitHub workflow. Continuing scheduler loop.")

        # Update the last check time before sleeping
        last_check_time = current_time
        # Sleep for the specified interval before the next check
        print(f"Sleeping for {INTERVAL_SECONDS} seconds (~30 minutes)...")
        time.sleep(INTERVAL_SECONDS)

if __name__ == "__main__":
    main()
