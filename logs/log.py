import datetime

def log_action(action):
    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"{current_time} {action}\n"

    with open("logs.txt", "a") as log_file:
        log_file.write(log_entry)

def error_action(action):
    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"ERROR {current_time} {action}\n"

    with open("errors.txt", "a") as log_file:
        log_file.write(log_entry)