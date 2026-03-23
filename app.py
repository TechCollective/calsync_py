from at_requests import *
from helpers import *
from log import *
import sys
import os
import subprocess
from dotenv import load_dotenv
from service_call import ServiceCall
from google_event import *
from datetime import datetime, timedelta

load_dotenv(override=True)

# ______________________ Get service calls from Autotask ______________________

today = datetime.today().date()
range_end = today + timedelta(days=365)
today_str = today.strftime("%Y-%m-%d")
range_end_str = range_end.strftime("%Y-%m-%d")

# Custom dates for testing
if os.getenv("TESTMODE") == 'TRUE':
    today_str = "2025-12-20"
    range_end_str = "2025-12-25"

log_event("\n\n Starting Sync")

# Get a list of service calls from AutoTask and from the database. Exit if can't get either.
at_service_calls = get_service_calls(today_str, range_end_str)
if at_service_calls is False:
    log_event("Unable to fetch service calls from Autotaks, aborting sync")
    sys.exit()
if not os.path.exists('data.db'):
    log_error("Database not found, running db_init.py to create a new one")
    try:
        subprocess.run([sys.executable, 'db_init.py'], check=True)
        log_event("Database created successfully")
    except Exception as e:
        log_error(f"Failed to create database: {e}")
        sys.exit()

try:
    db_service_calls = ServiceCall.fetch_all()
except Exception as e:
    log_error(f"Unable to fetch service calls from database, aborting sync: {e}")
    sys.exit()

# Compare to find service calls not in the database, return a list of IDs
new_service_call_ids = find_missing_ids(at_service_calls, db_service_calls)
log_event(f"new service calls: {new_service_call_ids}")

# Compare to find service calls with newer date modified than in the database
modified_service_call_ids = compare_date_modified(
    db_service_calls, at_service_calls)
log_event(f"modified service calls: {modified_service_call_ids}")

# Create list of all new and modified service calls
new_and_updated = filter_by_ids(
    at_service_calls, new_service_call_ids + modified_service_call_ids)

# Get a list of all resources in AT
all_resources = get_all_resources()
if all_resources is False:
    log_error("Unable to retrieve list of resources from AutoTask, aborting sync")
    sys.exit()

# ______________________ helper: normalize datetimes ______________________


def _norm(dt_in):
    try:
        dt = parse_datetime_flexible(dt_in)
        return dt.strftime('%Y-%m-%dT%H:%M:%SZ')
    except Exception:
        log_error(
            f"Unparseable datetime: {dt_in!r}; falling back to date-only or now")
        try:
            d = extract_date(dt_in)
            if d:
                return f"{d.strftime('%Y-%m-%d')}T00:00:00Z"
        except Exception:
            pass
        # last resort
        return datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')


# Get additional data from AutoTask for new and updated service calls
for s in new_and_updated:
    # Skip if ID isn't an integer
    if not isinstance(s['id'], int):
        log_error(f'not a integer {s}')
        continue

    # Add resource emails:
    s_emails = ''
    try:
        tickets = get_service_call_ticket(s['id'])
        if tickets:
            service_call_ticket_id = tickets[0]["id"]
            resources = get_service_call_resources(service_call_ticket_id)
            resource_emails = []
            for r in resources:
                match = next(
                    (item for item in all_resources if item["id"] == r["resourceID"]), None)
                if match:
                    resource_emails.append(match["email"])
            s.update({"emails": resource_emails})
            s_emails = ', '.join(s['emails'])
    except Exception as e:
        log_error(
            f"Error retrieving resource emails for service call {s['id']}: {e}")

    # Add company
    company = ''
    try:
        company_data = get_company_data(s["companyID"])
        if company_data:
            company = company_data[0]['companyName']
    except Exception as e:
        log_error(f"Error retrieving company for service call {s['id']}: {e}")
    s.update({"company": company})

    # Add location
    location = ''
    try:
        location_data = get_company_location(s['companyLocationID'])
        if len(location_data) > 0:
            location = (
                location_data[0]['address1'] + '\n' + location_data[0]['address2'] + '\n' +
                location_data[0]['city'] + '\n' + location_data[0]['state'] +
                '\n' + location_data[0]['postalCode']
            )
    except Exception as e:
        log_error(f"Error retrieving location for service call {s['id']}: {e}")

    # Add ticket info
    ticket_ids = []
    ticketInfo = '\n'

    try:
        service_call_ticket_info = get_service_call_ticket(s['id'])
        ticket_ids = [i['ticketID'] for i in service_call_ticket_info]
        for i in ticket_ids:
            ticketInfo += (
                'https://ww14.autotask.net/Autotask/AutotaskExtend/ExecuteCommand.aspx?Code=OpenTicketDetail&TicketID='
                + str(i) + '\n'
            )
    except Exception as e:
        log_error(f'Error getting ticket ids {e}')

    for id in ticket_ids:
        try:
            ticketInfo += f'\n{get_ticket(id)[0]["description"]}'
        except Exception as e:
            log_error(f'Error getting ticket description: {e}')

    # ______________________ Sync to Database ______________________

    try:
        s['startDateTime'] = _norm(s['startDateTime'])
        s['endDateTime'] = _norm(s['endDateTime'])

        # (self, call_id, startDateTime, endDateTime, lastModifiedDateTime, description, company, location, resources, ticketInfo, deleted, needs_sync):
        updated_service_call = ServiceCall(
            s['id'], s['startDateTime'], s['endDateTime'], s['lastModifiedDateTime'],
            s['description'], s['company'], location, s_emails, ticketInfo, 0, 1
        )
        updated_service_call.save()
        log_event(
            f"Added/updated service call to db:  {s['id']} {s['startDateTime']} {s['description']} {s['company']} {s_emails}"
        )
    except Exception as e:
        ticket_links = ' '.join(
            line.strip() for line in ticketInfo.splitlines() if 'TicketID=' in line)
        log_error(
            f"ERROR: Unable to add/update service call to db:  {s['id']} {s.get('startDateTime')} {s['description']} {s['company']} {s_emails} {ticket_links}: {e}"
        )

# Compare to find service calls not in AutoTask (deleted), return a list of IDs
missing_service_call_ids = []
try:
    missing_service_call_ids = find_missing_ids(
        db_service_calls, at_service_calls)
    log_event(
        f"missing (deleted in AT or outside AT fetch date-range) service calls: {missing_service_call_ids}")
except Exception as e:
    log_error(f'Error finding missing service calls: {e}')
try:
    ServiceCall.mark_as_deleted(
        missing_service_call_ids, today_str, range_end_str)
except Exception as e:
    log_error(f'Error marking service calls as deleted: {e}')

# ______________________ Sync to Google ______________________

try:
    events_needing_gsync = ServiceCall.get_rows_needing_sync()
except Exception as e:
    log_error(f'Error retrieving events needed sync from database: {e}')
    events_needing_gsync = []

for event in events_needing_gsync:
    try:
        if event['description'][0:6].lower() == 'remote':
            title = 'Remote: ' + event['company']
        elif event['description'][0:6].lower() == 'onsite':
            title = 'Onsite: ' + event['company']
        else:
            title = event['company']

        db_id = event["id"]
        event_id = f'autotask{event["id"]}'

        event_resources = [e for e in (
            event['resources'] or '').split(', ') if e]
        attendees = [{'email': email, 'responseStatus': 'accepted'}
                     for email in event_resources]

        start_iso = _norm(event['startDateTime'])
        end_iso = _norm(event['endDateTime'])

        result = {
            'id': event_id,
            'summary': title,
            'description': event['description'] + event['ticketInfo'],
            'start': {
                'dateTime': start_iso,
                'timeZone': 'America/New_York',
            },
            'end': {
                'dateTime': end_iso,
                'timeZone': 'America/New_York',
            },
            'attendees': attendees,
            'location': event['location'],
        }
    except Exception as e:
        log_error(
            f"Error building Google event for service call {event.get('id')}: {e}")
        continue

    try:
        if event_exists(event_id) is False:
            add_event(result)
        else:
            modify_event(result)

        try:
            ServiceCall.mark_as_synced(db_id)
        except Exception as e:
            log_error(
                f'Error marking service call {db_id} as synced in database: {e}')
    except Exception as e:
        log_error(f'Error syncing service call {db_id} to Google: {e}')

# ______________________ Delete from Google ______________________

try:
    events_needing_deletion = ServiceCall.get_rows_needing_deletion()
except Exception as e:
    log_error(f'Error retrieving events needing deletion from database: {e}')
    events_needing_deletion = []

for event in events_needing_deletion:
    db_id = event["id"]
    event_id = f'autotask{event["id"]}'
    try:
        if event_exists(event_id):
            delete_event(event_id)
        ServiceCall.delete(db_id)
    except Exception as e:
        log_error(f'Error deleting Google event for service call {db_id}: {e}')

# ______________________ Clean DB ______________________

delete_date = datetime.strptime(today_str, '%Y-%m-%d') - timedelta(days=1)
try:
    log_event(
        f"Removing any old service calls from the database (before {delete_date})")
    ServiceCall.delete_old_events(delete_date)
except Exception as e:
    log_error(f"Error removing old service calls from database \n{e}")

log_event("sync complete with errors" if has_errors() else "sync complete")
