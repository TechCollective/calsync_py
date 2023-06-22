from at_requests import *
from db_helpers import *
from helpers import *
from datetime import datetime, timedelta

today = datetime.today().date()
range_end = today + timedelta(days=365)
yesterday = today - timedelta(days=1)

all_resources = get_all_resources()  # gets a list of all resources in AT

today_testing = "2024-06-01"
range_end_testing = "2024-06-30"

# Get a list of service calls from AutoTask and from the database
service_calls = get_service_calls(today_testing, range_end_testing)
db_service_calls = fetch_table_rows("service_calls")
print("all service calls in range: \n", service_calls)

# Compare to find service calls not in the database, return a list of IDs
new_service_call_ids = find_missing_ids(service_calls, db_service_calls)
print("new service calls:", new_service_call_ids)

# Compare to find service calls with newer date modified than in the database
modified_service_call_ids = compare_date_modified(
    db_service_calls, service_calls)
print("modified service calls: ", modified_service_call_ids)

new_and_updated = filter_by_ids(
    service_calls, new_service_call_ids + modified_service_call_ids)
print(new_and_updated)

# updated_service_calls = service_calls.copy()
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


# print(updated_service_calls)

# add to database
for s in new_and_updated:
    s_emails = result = ', '.join(s['emails'])
    # upsert_service_call(call_id, start_date_time, end_date_time, description, company, resources, needs_sync
    upsert_service_call(s['id'], s['startDateTime'], s['endDateTime'], s['lastModifiedDateTime'],
                        s['description'], s['company'], s_emails, 1)


# Compare to find service calls not in AutoTask (deleted), return a list of IDs
deleted_service_call_ids = find_missing_ids(db_service_calls, service_calls)
# then check to see if the date time is within range


print("deleted: ", deleted_service_call_ids)

mark_rows_as_deleted(deleted_service_call_ids,
                     today_testing, range_end_testing)
