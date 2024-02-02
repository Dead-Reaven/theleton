import json
import datetime

# Path to your JSON file
json_file = 'data.json'

# Custom exception class for limit errors
class ErrorLimitCall(Exception):
    pass

# Function to read data from the JSON file
def read_data():
    try:
        with open(json_file, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}  # Return an empty dictionary if the file doesn't exist or is empty

# Function to write data to the JSON file
def write_data(data):
    with open(json_file, 'w') as f:
        json.dump(data, f)

# Function to increase the counter for a rule
def call(field):
    check_date(field)  # Check if the counter needs to be reset
    data = read_data()
    rule = data.get(field)

    if not rule:
        raise ValueError(f"No rule found for {field}")
    if rule['counter'] + 1 > rule['max_value']:
        raise ErrorLimitCall(f"Error: called {field} too many times per limit! log:\n {data} ")
    rule['counter'] += 1
    write_data(data)

# Function to reset the counter for a rule
def clear_counter(field):
    data = read_data()
    rule = data.get(field)
    if rule:
        rule['counter'] = 0
        rule['date_to_update'] = str(datetime.datetime.now() + datetime.timedelta(minutes=rule['max_date']))
        write_data(data)

# Function to check if the counter for a rule needs to be reset
def check_date(field):
    data = read_data()
    rule = data.get(field)
    if rule:
        last_date = datetime.datetime.strptime(rule['date_to_update'], '%Y-%m-%d %H:%M:%S.%f')
        if datetime.datetime.now() >= last_date:
            clear_counter(field)
            return True
    return False

# Function to add a new rule
def add_rule(field, max_value, max_date):
    data = read_data()
    if field not in data:
        data[field] = {
            'counter': 0,
            'max_value': max_value,
            'date_to_update': str(datetime.datetime.now() + datetime.timedelta(minutes=max_date)),
            'max_date': max_date
        }
        write_data(data)

# Usage
print("now:", str(datetime.datetime.now()))


#! testing usage
# add_rule('send_invate', 3, 1)  # Add a new rule if it doesn't exist

# try:
#     call('send_invate')  # Increase the counter by one for 'a1'
#     print(read_data())  # Print the current data
# except ErrorLimitCall as e:
#     print(str(e))  # Print the error message if a limit error occurs
