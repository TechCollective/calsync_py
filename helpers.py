from datetime import datetime, date, time

# returns any id's that are in the first list, but not in the 2nd list


def find_missing_ids(list1, list2):
    ids_list1 = {item['id'] for item in list1}
    ids_list2 = {item['id'] for item in list2}
    return list(ids_list1 - ids_list2)

# takes a date with time, removes time, and checks to see if it's in a date range


def is_date_within_range(date_str, start_date, end_date):
    date_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ").date()
    start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
    return start_date_obj <= date_obj <= end_date_obj

# compares two lists, returns the id if the item in the first list is older than the item in the second list


def compare_date_modified(list1, list2):
    matching_ids = []
    for item1 in list1:
        for item2 in list2:
            if item1['id'] == item2['id']:
                try:
                    date1 = datetime.strptime(
                        item1['lastModifiedDateTime'], "%Y-%m-%dT%H:%M:%S.%fZ")
                except ValueError:
                    date1 = datetime.strptime(
                        item1['lastModifiedDateTime'], "%Y-%m-%dT%H:%M:%SZ")

                try:
                    date2 = datetime.strptime(
                        item2['lastModifiedDateTime'], "%Y-%m-%dT%H:%M:%S.%fZ")
                except ValueError:
                    date2 = datetime.strptime(
                        item2['lastModifiedDateTime'], "%Y-%m-%dT%H:%M:%SZ")

                if date1 < date2:
                    matching_ids.append(item1['id'])
    return matching_ids

# filters a list of dictionaries based on a list of id's


def filter_by_ids(data_list, id_list):
    return [item for item in data_list if item['id'] in id_list]


# functions to help with AT returning malformed date-time strings
def parse_datetime_flexible(dt_str):
    if isinstance(dt_str, datetime):  # already a datetime
        return dt_str
    if isinstance(dt_str, date):      # date -> combine with midnight
        return datetime.combine(dt_str, time.min)

    # Try exact match first
    for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S.%fZ"):
        try:
            return datetime.strptime(dt_str, fmt)
        except ValueError:
            pass

    # Fallback: strip milliseconds or trailing 'Z', then parse
    try:
        trimmed = dt_str.split(".")[0]  # remove milliseconds if present
        if trimmed.endswith("Z"):
            trimmed = trimmed[:-1]
        return datetime.strptime(trimmed, "%Y-%m-%dT%H:%M:%S")
    except ValueError:
        # Last resort: just take the date part
        return datetime.strptime(dt_str[:10], "%Y-%m-%d")


def extract_date(dt_str):
    if isinstance(dt_str, date):
        return dt_str
    try:
        return datetime.strptime(dt_str[:10], "%Y-%m-%d").date()
    except Exception:
        return None
