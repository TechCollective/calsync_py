import requests
import os
import json
from dotenv import load_dotenv
from log import *

load_dotenv(override=True)

base_url = 'https://webservices14.autotask.net/ATServicesRest/V1.0/'

headers = {
    'accept': 'application/json',
    'Username': os.getenv("USERNAME"),
    'Secret': os.getenv("SECRET"),
    'APIIntegrationcode': os.getenv("APIINTEGRATIONCODE"),
    'ContentType': 'application/json'
}


def get_service_calls(start_date, end_date):
    service_call_body = {
        "MaxRecords": 0,
        "IncludeFields": [
            "id",
            "description",
            "startDateTime",
            "endDateTime",
            "companyID",
            "duration",
            "lastModifiedDateTime",
            "companyLocationID",
            "canceledDateTime",
        ],
        "Filter": [
            {
                "op": "gte",
                "field": "startDateTime",
                "value": start_date,
            },
            {
                "op": "lte",
                "field": "startDateTime",
                "value": end_date,
            }
        ]
    }

    try:
        response = requests.post(
            base_url + 'ServiceCalls/query', headers=headers, json=service_call_body)
        response.raise_for_status()
        return response.json()['items']
    except requests.exceptions.RequestException as e:
        log_error(f"Network error fetching service calls: {e}")
        return False
    except Exception as e:
        log_error(f"Error fetching service calls: {e}")
        return False


# Get the ServiceCallTicket - note this is not the same as a Ticket, but a reference to that ticket and assigned resources
# The ServiceCallTickets entity describes an Autotask ticket assigned to a service call
def get_service_call_ticket(service_call_id):
    body = {
        "maxRecords": 0,
        "includeFields": ["id", "serviceCallID", "ticketID"],
        "filter": [
            {
                "op": "eq",
                "field": "serviceCallID",
                "value": service_call_id,
            },
        ]
    }
    try:
        response = requests.post(
            base_url + 'ServiceCallTickets/query', headers=headers, json=body)
        response.raise_for_status()
        return response.json()['items']
    except requests.exceptions.RequestException as e:
        log_error(f"Network error retrieving service call tickets for {service_call_id}: {e}")
        return []
    except Exception as e:
        log_error(f"Error retrieving service call tickets for {service_call_id}: {e}")
        return []


# Get Resources assinged to a Service Call
# https://ww1.autotask.net/help/developerhelp/Content/APIs/REST/Entities/ServiceCallTicketResourceEntity.htm
# takes the id field of the ServiceCallTicketResources entity
def get_service_call_resources(service_call_ticket_id):
    body = {
        "maxRecords": 0,
        "includeFields": ["resourceID"],
        "filter": [
            {
                "op": "eq",
                "field": "serviceCallTicketID",
                "value": service_call_ticket_id,
            },
        ]
    }
    try:
        response = requests.post(
            base_url + 'ServiceCallTicketResources/query', headers=headers, json=body)
        response.raise_for_status()
        return response.json()['items']
    except requests.exceptions.RequestException as e:
        log_error(f"Network error retrieving resources for service call ticket {service_call_ticket_id}: {e}")
        return []
    except Exception as e:
        log_error(f"Error retrieving resources for service call ticket {service_call_ticket_id}: {e}")
        return []


def get_company_data(company_id):
    company_body = {
        "maxRecords": 1,
        "includeFields": [
            "companyName",
            "address1",
            "address2",
            "city",
            "state",
            "postalCode",
        ],
        "filter": [
            {
                "op": "eq",
                "field": "id",
                "value": company_id,
            },
        ],
    }
    try:
        response = requests.post(
            base_url + 'Companies/query', headers=headers, json=company_body)
        response.raise_for_status()
        return response.json()['items']  # saves as list
    except requests.exceptions.RequestException as e:
        log_error(f"Network error retrieving company data for {company_id}: {e}")
        return []
    except Exception as e:
        log_error(f"Error retrieving company data for {company_id}: {e}")
        return []


def get_all_resources():
    body = {
        "maxRecords": 0,
        "includeFields": ["id", "email"],
        "filter": [
            {
                "op": "exist",
                "field": "id",
            },
        ],
    }
    try:
        response = requests.post(
            base_url + 'Resources/query', headers=headers, json=body)
        response.raise_for_status()
        return response.json()['items']  # saves as list
    except requests.exceptions.RequestException as e:
        log_error(f"Network error retrieving all resources: {e}")
        return False
    except Exception as e:
        log_error(f"Error retrieving all resources: {e}")
        return False

# Get company location, takes the companyLocationID from the Service Call
# https://ww1.autotask.net/help/developerhelp/content/apis/rest/entities/CompanyLocationsEntity.htm


def get_company_location(location_id):
    body = {
        "maxRecords": 1,
        "includeFields": [
            "address1",
            "address2",
            "city",
            "state",
            "postalCode",
            "phone",
        ],
        "filter": [
            {
                "op": "eq",
                "field": 'id',
                "value": location_id,
            },
        ],
    }
    try:
        response = requests.post(
            base_url + 'CompanyLocations/query', headers=headers, json=body)
        response.raise_for_status()
        return response.json()['items']  # saves as list
    except requests.exceptions.RequestException as e:
        log_error(f"Network error retrieving location for {location_id}: {e}")
        return []
    except Exception as e:
        log_error(f"Error retrieving location for {location_id}: {e}")
        return []


def _get_ticket_status_picklist_values():
    """Fetch and return the raw ticket status picklist values from the AT API."""
    try:
        response = requests.get(
            base_url + 'Tickets/entityInformation/fields', headers=headers)
        response.raise_for_status()
        fields = response.json().get('fields', [])
        status_field = next((f for f in fields if f.get('name') == 'status'), None)
        return status_field.get('picklistValues', []) if status_field else []
    except Exception as e:
        log_error(f"Error fetching ticket status picklist: {e}")
        return []


def get_ticket_status_picklist():
    """Print all ticket status picklist values and their IDs. Run this to find the numeric ID for a status label."""
    values = _get_ticket_status_picklist_values()
    if values:
        print("Ticket status picklist values:")
        for item in values:
            print(f"  {item['value']:>4}  {item['label']}")
    else:
        print("No status picklist values found.")


def get_ticket_status_id(label):
    """Return the numeric picklist ID for a given ticket status label, or None if not found."""
    values = _get_ticket_status_picklist_values()
    match = next((item for item in values if item['label'].lower() == label.lower()), None)
    return match['value'] if match else None


def get_ticket(ticket_id):
    body = {
        "maxRecords": 0,
        "filter": [
            {
                "op": "eq",
                "field": "id",
                "value": ticket_id,
            },
        ]
    }
    try:
        response = requests.post(
            base_url + 'Tickets/query', headers=headers, json=body)
        response.raise_for_status()
        return response.json()['items']
    except requests.exceptions.RequestException as e:
        log_error(f"Network error retrieving ticket {ticket_id}: {e}")
        return []
    except Exception as e:
        log_error(f"Error retrieving ticket {ticket_id}: {e}")
        return []
