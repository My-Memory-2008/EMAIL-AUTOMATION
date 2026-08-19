# import json
# import time
# import subprocess
# from datetime import datetime
# import sys
# import pytz

# # Setup Indian Standard Timezone
# IST = pytz.timezone('Asia/Kolkata')

# # Track the absolute start time of this scheduler script
# MASTER_START_TIME = time.time()
# # Define the intervals and thresholds
# RUN_INTERVAL_SECONDS = 30 * 60  # 30 minutes
# MAX_RUNTIME_SECONDS = 5 * 60 * 60  # 5 hours
# WAIT_AFTER_CONTROLLER_SECONDS = 10 # Time to wait after triggering controller before exiting

# def get_current_ist():
#     return datetime.now(IST)

# def run_command(command):
#     """Executes a shell command and returns stdout, stderr, and the return code."""
#     result = subprocess.run(command, shell=True, text=True, capture_output=True)
#     return result.stdout.strip(), result.stderr.strip(), result.returncode

# def get_new_run_id(workflow_file):
#     """Reliably fetches the Run ID of the newly triggered workflow."""
#     # Try up to 5 times to find the newly queued/in_progress run
#     for attempt in range(5):
#         # Using --json instead of --jq to avoid shell quoting issues on Windows/Linux runners
#         cmd = f'gh run list --workflow={workflow_file} --limit=5 --json databaseId,status'
#         out, err, code = run_command(cmd)
        
#         if code == 0 and out:
#             try:
#                 runs = json.loads(out)
#                 # Find the first run that is actively running or queued
#                 for run in runs:
#                     if run.get("status") in ["queued", "in_progress"]:
#                         return str(run["databaseId"])
#             except json.JSONDecodeError:
#                 pass
        
#         time.sleep(3) # Wait a few seconds before checking again
    
#     # Fallback: If all are completed, just return the most recent one
#     if runs:
#         return str(runs[0]["databaseId"])
#     return None

# def trigger_workflow(workflow_file):
#     """Triggers a GitHub workflow using the GitHub CLI (gh)."""
#     print(f"[{get_current_ist().strftime('%Y-%m-%d %H:%M:%S')}] Triggering workflow: {workflow_file}", flush=True)
#     cmd = f"gh workflow run {workflow_file} --ref main"
#     out, err, code = run_command(cmd)
    
#     if code != 0:
#         print(f"Error triggering workflow: {err}", flush=True)
#         return None
    
#     print("Waiting for GitHub to register the new run...", flush=True)
#     run_id = get_new_run_id(workflow_file)
    
#     if not run_id:
#         print("Failed to fetch the new Run ID.", flush=True)
#         return None
        
#     print(f"Successfully captured new Run ID: {run_id}", flush=True)
#     return run_id

# def monitor_workflow(run_id, workflow_file, job_start_time):
#     """Monitors a workflow run. Triggers scheduler-controller.yml, cancels the run if it exceeds 5 hours."""
    
#     five_hours_in_seconds = 5 * 60 * 60
#     print(f"Monitoring Workflow Run ID: {run_id} for {workflow_file}", flush=True)
    
#     while True:
#         elapsed_time = time.time() - job_start_time
#         print(f"Checking status... Elapsed time for this job: {elapsed_time / 3600:.2f} hours", flush=True)
            
#         if elapsed_time >= five_hours_in_seconds:
#             print(f"⚠️ Alert: Workflow {workflow_file} (Run ID: {run_id}) has reached the 5-hour limit!", flush=True)
                
#             controller_wf = "scheduler-controller.yml"
#             print(f"Triggering controller workflow: {controller_wf}...", flush=True)
#             trigger_cmd = f"gh workflow run {controller_wf} --ref main"
            
#             t_out, t_err, t_code = run_command(trigger_cmd)
                
#             if t_code == 0:
#                 print(f"✅ {controller_wf} triggered successfully. Cancelling target workflow...", flush=True)
#                 cancel_cmd = f"gh run cancel {run_id}"
#                 c_out, c_err, c_code = run_command(cancel_cmd)
                
#                 if c_code != 0:
#                     print(f"Error cancelling workflow via GitHub CLI: {c_err}", flush=True)
#                 else:
#                     print(f"Successfully eliminated target workflow {workflow_file}.", flush=True)
                    
#                 print("🏁 Script logic complete. Terminating scheduler process successfully.", flush=True)
#                 sys.exit(0)
#             else:
#                 print(f"❌ Failed to trigger {controller_wf}. Error: {t_err}. Aborting.", flush=True)
#                 sys.exit(1)

#         # Check status using --json to avoid jq parsing issues
#         status_cmd = f"gh run view {run_id} --json status,conclusion"
#         status_json, status_err, status_code = run_command(status_cmd)
        
#         if status_code != 0 or not status_json:
#             print(f"CLI Error checking status. Details: {status_err}", flush=True)
#         else:
#             try:
#                 status_data = json.loads(status_json)
#                 status = status_data.get("status")
#                 conclusion = status_data.get("conclusion")
                    
#                 if status == "completed":
#                     print(f"Workflow {workflow_file} finished naturally with conclusion: {conclusion}", flush=True)
#                     break 
                
#             except Exception as e:
#                 print(f"Parsing error: {e}. Raw payload received: {status_json}", flush=True)

#         time.sleep(60)

# def check_and_execute_main_job():
#     """Triggers the main email_check.yml workflow every 30 minutes."""
#     print(f"[{get_current_ist().strftime('%Y-%m-%d %H:%M:%S')}] Initiating scheduled check for email_check.yml", flush=True)
    
#     job_start_time = time.time()
#     run_id = trigger_workflow("email_check.yml") # Hardcode the workflow name
    
#     if run_id:
#         monitor_workflow(run_id, "email_check.yml", job_start_time)
#     else:
#         print("⚠️ Could not retrieve Run ID for email_check.yml. Skipping monitoring for this run.", flush=True)

# def main():
#     print("🚀 Long-running master scheduler started via Python loop engine...", flush=True)
#     print(f"Will trigger 'email_check.yml' every {RUN_INTERVAL_SECONDS / 60} minutes.", flush=True)
#     print(f"Will trigger 'scheduler-controller.yml' if running for more than {MAX_RUNTIME_SECONDS / 3600} hours.", flush=True)
    
#     # Calculate the time for the next scheduled run
#     next_run_time = time.time() + RUN_INTERVAL_SECONDS
    
#     while True:
#         current_time = time.time()
        
#         # Check total runtime of the master scheduler script itself
#         elapsed_master_time = current_time - MASTER_START_TIME
#         if elapsed_master_time >= MAX_RUNTIME_SECONDS:
#             print(f"\n⚠️ Alert: Master script runtime ({elapsed_master_time / 3600:.2f} hours) has exceeded the 5-hour limit!", flush=True)
            
#             controller_wf = "scheduler-controller.yml"
#             print(f"Triggering controller workflow: {controller_wf}...", flush=True)
#             trigger_cmd = f"gh workflow run {controller_wf} --ref main"
            
#             t_out, t_err, t_code = run_command(trigger_cmd)
#             if t_code == 0:
#                 print(f"✅ {controller_wf} triggered successfully.", flush=True)
#                 print(f"Waiting {WAIT_AFTER_CONTROLLER_SECONDS} seconds before terminating scheduler.py...", flush=True)
#                 time.sleep(WAIT_AFTER_CONTROLLER_SECONDS) # Wait for 10 seconds
#                 print("Terminating scheduler.py now.")
#                 sys.exit(0) # Exit the script successfully
#             else:
#                 print(f"❌ Failed to trigger {controller_wf}. Error: {t_err}. Attempting to continue.", flush=True)
#                 # Optionally, you could reset the MASTER_START_TIME here if you want to keep going
#                 # MASTER_START_TIME = time.time() # Reset timer on failure
#                 # Or exit if failure is critical
#                 # sys.exit(1)

#         # Check if it's time to run the main job (email_check.yml)
#         if current_time >= next_run_time:
#              check_and_execute_main_job()
#              # Update the time for the *next* run
#              next_run_time = time.time() + RUN_INTERVAL_SECONDS
#              print(f"Next 'email_check.yml' run scheduled for: {datetime.fromtimestamp(next_run_time).strftime('%Y-%m-%d %H:%M:%S')} IST")
        
#         # Sleep for a short period before the next check loop iteration
#         # This allows the runtime check to happen frequently
#         # Use the minimum of remaining time to next run or a fixed check interval (e.g., 1 minute)
#         remaining_time_to_next_run = max(0, next_run_time - current_time)
#         sleep_time = min(remaining_time_to_next_run, 60) # Check every minute at most
#         if sleep_time > 0:
#             print(f"Sleeping for {sleep_time:.0f} seconds...", flush=True)
#             time.sleep(sleep_time)
#         # If sleep_time is 0, the loop continues immediately to re-check times


# if __name__ == "__main__":
#     main()













import json
import time
import subprocess
from datetime import datetime
import sys
import pytz

# Setup Indian Standard Timezone
IST = pytz.timezone('Asia/Kolkata')

# Track the absolute start time of this scheduler script
MASTER_START_TIME = time.time()
# Define the intervals and thresholds
RUN_INTERVAL_SECONDS = 30 * 60  # 30 minutes
MAX_RUNTIME_SECONDS = 5 * 60 * 60  # 5 hours
WAIT_AFTER_CONTROLLER_SECONDS = 10 # Time to wait after triggering controller before exiting

def get_current_ist():
    return datetime.now(IST)

def run_command(command):
    """Executes a shell command and returns stdout, stderr, and the return code."""
    result = subprocess.run(command, shell=True, text=True, capture_output=True)
    return result.stdout.strip(), result.stderr.strip(), result.returncode

def get_new_run_id(workflow_file):
    """Reliably fetches the Run ID of the newly triggered workflow."""
    runs = []  # FIX: Initialize runs to prevent NameError
    for attempt in range(5):
        cmd = f'gh run list --workflow={workflow_file} --limit=5 --json databaseId,status'
        out, err, code = run_command(cmd)
        
        if code == 0 and out:
            try:
                runs = json.loads(out)
                for run in runs:
                    if run.get("status") in ["queued", "in_progress"]:
                        return str(run["databaseId"])
            except json.JSONDecodeError:
                pass
        
        time.sleep(3)
    
    # Fallback: If all are completed, just return the most recent one
    if runs:
        return str(runs[0]["databaseId"])
    return None

def trigger_workflow(workflow_file):
    """Triggers a GitHub workflow using the GitHub CLI (gh)."""
    print(f"[{get_current_ist().strftime('%Y-%m-%d %H:%M:%S')}] Triggering workflow: {workflow_file}", flush=True)
    cmd = f"gh workflow run {workflow_file} --ref main"
    out, err, code = run_command(cmd)
    
    if code != 0:
        print(f"Error triggering workflow: {err}", flush=True)
        return None
    
    print("Waiting for GitHub to register the new run...", flush=True)
    run_id = get_new_run_id(workflow_file)
    
    if not run_id:
        print("Failed to fetch the new Run ID.", flush=True)
        return None
        
    print(f"Successfully captured new Run ID: {run_id}", flush=True)
    return run_id

def monitor_workflow(run_id, workflow_file, job_start_time):
    """Monitors a workflow run. Triggers scheduler-controller.yml, cancels the run if it exceeds 5 hours."""
    
    five_hours_in_seconds = 5 * 60 * 60
    print(f"Monitoring Workflow Run ID: {run_id} for {workflow_file}", flush=True)
    
    while True:
        elapsed_time = time.time() - job_start_time
        print(f"Checking status... Elapsed time for this job: {elapsed_time / 3600:.2f} hours", flush=True)
            
        if elapsed_time >= five_hours_in_seconds:
            print(f"⚠️ Alert: Workflow {workflow_file} (Run ID: {run_id}) has reached the 5-hour limit!", flush=True)
                
            controller_wf = "scheduler-controller.yml"
            print(f"Triggering controller workflow: {controller_wf}...", flush=True)
            trigger_cmd = f"gh workflow run {controller_wf} --ref main"
            
            t_out, t_err, t_code = run_command(trigger_cmd)
                
            if t_code == 0:
                print(f"✅ {controller_wf} triggered successfully. Cancelling target workflow...", flush=True)
                cancel_cmd = f"gh run cancel {run_id}"
                c_out, c_err, c_code = run_command(cancel_cmd)
                
                if c_code != 0:
                    print(f"Error cancelling workflow via GitHub CLI: {c_err}", flush=True)
                else:
                    print(f"Successfully eliminated target workflow {workflow_file}.", flush=True)
                    
                print("🏁 Script logic complete. Terminating scheduler process successfully.", flush=True)
                sys.exit(0)
            else:
                print(f"❌ Failed to trigger {controller_wf}. Error: {t_err}. Aborting.", flush=True)
                sys.exit(1)

        status_cmd = f"gh run view {run_id} --json status,conclusion"
        status_json, status_err, status_code = run_command(status_cmd)
        
        if status_code != 0 or not status_json:
            print(f"CLI Error checking status. Details: {status_err}", flush=True)
        else:
            try:
                status_data = json.loads(status_json)
                status = status_data.get("status")
                conclusion = status_data.get("conclusion")
                    
                if status == "completed":
                    print(f"Workflow {workflow_file} finished naturally with conclusion: {conclusion}", flush=True)
                    break 
                
            except Exception as e:
                print(f"Parsing error: {e}. Raw payload received: {status_json}", flush=True)

        time.sleep(60)

def check_and_execute_main_job():
    """Triggers the main email_check.yml workflow every 30 minutes."""
    print(f"[{get_current_ist().strftime('%Y-%m-%d %H:%M:%S')}] Initiating scheduled check for email_check.yml", flush=True)
    
    job_start_time = time.time()
    run_id = trigger_workflow("email_check.yml")
    
    if run_id:
        monitor_workflow(run_id, "email_check.yml", job_start_time)
    else:
        print("⚠️ Could not retrieve Run ID for email_check.yml. Skipping monitoring for this run.", flush=True)

def main():
    print("🚀 Long-running master scheduler started via Python loop engine...", flush=True)
    print(f"Will trigger 'email_check.yml' every {RUN_INTERVAL_SECONDS / 60} minutes.", flush=True)
    print(f"Will trigger 'scheduler-controller.yml' if running for more than {MAX_RUNTIME_SECONDS / 3600} hours.", flush=True)
    
    # FIX: Set to current time so the first run happens immediately
    # If you want a 30-minute delay before the first run, change back to:
    # next_run_time = time.time() + RUN_INTERVAL_SECONDS
    next_run_time = time.time()
    
    while True:
        current_time = time.time()
        
        # Check total runtime of the master scheduler script itself
        elapsed_master_time = current_time - MASTER_START_TIME
        if elapsed_master_time >= MAX_RUNTIME_SECONDS:
            print(f"\n⚠️ Alert: Master script runtime ({elapsed_master_time / 3600:.2f} hours) has exceeded the 5-hour limit!", flush=True)
            
            controller_wf = "scheduler-controller.yml"
            print(f"Triggering controller workflow: {controller_wf}...", flush=True)
            trigger_cmd = f"gh workflow run {controller_wf} --ref main"
            
            t_out, t_err, t_code = run_command(trigger_cmd)
            if t_code == 0:
                print(f"✅ {controller_wf} triggered successfully.", flush=True)
                print(f"Waiting {WAIT_AFTER_CONTROLLER_SECONDS} seconds before terminating scheduler.py...", flush=True)
                time.sleep(WAIT_AFTER_CONTROLLER_SECONDS)
                print("Terminating scheduler.py now.")
                sys.exit(0)
            else:
                print(f"❌ Failed to trigger {controller_wf}. Error: {t_err}. Attempting to continue.", flush=True)

        # Check if it's time to run the main job (email_check.yml)
        if current_time >= next_run_time:
             check_and_execute_main_job()
             next_run_time = time.time() + RUN_INTERVAL_SECONDS
             # FIX: Use IST timezone for the print statement
             next_run_dt = datetime.fromtimestamp(next_run_time, tz=IST)
             print(f"Next 'email_check.yml' run scheduled for: {next_run_dt.strftime('%Y-%m-%d %H:%M:%S')} IST")
        
        remaining_time_to_next_run = max(0, next_run_time - current_time)
        sleep_time = min(remaining_time_to_next_run, 60)
        if sleep_time > 0:
            print(f"Sleeping for {sleep_time:.0f} seconds...", flush=True)
            time.sleep(sleep_time)


if __name__ == "__main__":
    main()



