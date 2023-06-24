from at_requests import *
from db_helpers import *
from helpers import *
from datetime import datetime, timedelta

today = datetime.today().date()
range_end = today + timedelta(days=365)
yesterday = today - timedelta(days=1)
today_str = today.strftime("%Y-%m-%d")
range_end_str = range_end.strftime("%Y-%m-%d")
yesterday_str = yesterday.strftime("%Y-%m-%d")

all_resources = get_all_resources()  # gets a list of all resources in AT

today_str = "2024-06-01"
range_end_str = "2024-06-30"

# Get a list of service calls from AutoTask and from the database
service_calls = get_service_calls(today_str, range_end_str)
db_service_calls = fetch_table_rows("service_calls")
print("all service calls in range: \n", service_calls)

# Compare to find service calls not in the database, return a list of IDs
new_service_call_ids = find_missing_ids(service_calls, db_service_calls)
print("new service calls:", new_service_call_ids)

# Compare to find service calls with newer date modified than in the database
modified_service_call_ids = compare_date_modified(
    db_service_calls, service_calls)
print("modified service calls: ", modified_service_call_ids)

# Create list of all new and modified service calls
new_and_updated = filter_by_ids(
    service_calls, new_service_call_ids + modified_service_call_ids)


# Get additional data from AutoTask for new and updated service calls
for s in new_and_updated:
    # add resource emails:
    service_call_ticket_id = get_service_call_ticket(s['id'])[0]["id"]
    resources = get_service_call_resources(service_call_ticket_id)
    resource_emails = []
    try:
        for r in resources:
            resource_emails.append(next(
                item for item in all_resources if item["id"] == r["resourceID"])["email"])
    except:
        print('ERROR RETRIEVING RESOURCE EMAILS')
    s.update({"emails": resource_emails})

    # add company:
    company_id = get_company_data(s["companyID"])
    company = company_id[0]['companyName']
    s.update({"company": company})

    location = get_company_location(s['companyLocationID'])

    if len(location) > 0:
        location = location[0]['address1'] + '\n' + location[0]['address2'] + '\n' + \
            location[0]['city'] + '\n' + location[0]['state'] + \
            '\n' + location[0]['postalCode']
    else:
        location = ''

    print(location)
    # Add to database:
    s_emails = result = ', '.join(s['emails'])
    # update_db_service_calls(call_id, startDateTime, endDateTime, description, company, location, resources, needs_sync
    update_db_service_calls(s['id'], s['startDateTime'], s['endDateTime'], s['lastModifiedDateTime'],
                            s['description'], s['company'], location, s_emails, 1)


# Compare to find service calls not in AutoTask (deleted), return a list of IDs
deleted_service_call_ids = find_missing_ids(db_service_calls, service_calls)
# then check to see if the date time is within range
print("deleted: ", deleted_service_call_ids)
mark_rows_as_deleted(deleted_service_call_ids,
                     today_str, range_end_str)
