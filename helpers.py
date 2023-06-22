from datetime import datetime

# returns any id's that are in the first list, but not in the 2nd list


def find_missing_ids(list1, list2):
    ids_list1 = {item['id'] for item in list1}
    ids_list2 = {item['id'] for item in list2}

    missing_ids = list(ids_list1 - ids_list2)

    return missing_ids


# takes a date with time, removes time, and checks to see if it's in a date range
def is_date_within_range(date, start_date, end_date):
    date_obj = datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ").date()
    start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()

    if start_date_obj <= date_obj <= end_date_obj:
        return True
    else:
        return False

# compares two lists, returns the id if the item in the first list is older than the item in the second list


def compare_date_modified(list1, list2):
    matching_ids = [item1['id'] for item1 in list1 for item2 in list2 if item1['id'] == item2['id'] and datetime.strptime(
        item1['lastModifiedDateTime'], "%Y-%m-%dT%H:%M:%S.%fZ") < datetime.strptime(item2['lastModifiedDateTime'], "%Y-%m-%dT%H:%M:%S.%fZ")]
    return matching_ids


# filters a list of dictionaries based on a list of id's
def filter_by_ids(data_list, id_list):
    matching_items = []
    for item in data_list:
        if item['id'] in id_list:
            matching_items.append(item)
    return matching_items
