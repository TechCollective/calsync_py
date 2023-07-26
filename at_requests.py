import requests
import os
import json
from dotenv import load_dotenv
from log import *

load_dotenv()

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
            "companylocationID",
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
        return response.json()['items']
    except:
        log_error(f"{response.status_code} {response.reason} {response.text}")
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
        return response.json()['items']
    except:
        log_error('\nERROR RETRIEVING SERVICE CALL TICKETS\n')
        log_error(f"{response.status_code} {response.reason} {response.text}")
        # return False


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
        return response.json()['items']
    except:
        log_error(f"{response.status_code} {response.reason} {response.text}")
        log_error('\nERROR RETRIEVING SERVICE CALL TICKET RESOURCES\n')
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

        return response.json()['items']  # saves as list
    except:
        log_error('\nERROR RETRIEVING COMPANY DATA\n')
        log_error(f"{response.status_code} {response.reason} {response.text}")


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

        return response.json()['items']  # saves as list
    except:
        log_error("Error retreiving all resources from autotask")
        log_error(f"{response.status_code} {response.reason} {response.text}")
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

        # print(response.json()['items'])
        return response.json()['items']  # saves as list
    except:
        log_error('\nERROR RETRIEVING COMPANY LOCATION\n')
        log_error(f"{response.status_code} {response.reason} {response.text}")
        return []


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
        return response.json()['items']
    except:
        log_error('\nERROR RETRIEVING TICKET\n')
        log_error(f"{response.status_code} {response.reason} {response.text}")
