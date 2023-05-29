import re
from datetime import date
from datetime import datetime
from enum import Enum
from typing import Dict

from dateutil.parser import parse
from dateutil.parser import ParserError

from exceptions import MissingFieldException
from exceptions import InvalidDurationException
from exceptions import InvalidStatusException
from exceptions import InvalidDateException
from exceptions import InvalidDateTimeException
from exceptions import InvalidPostcodeException
from exceptions import InvalidPatientIdException


# Enums and converters

class Status(Enum):
    ATTENDED = 'attended'
    CANCELLED = 'cancelled'
    MISSED = 'missed'
    ACTIVE = 'active'


class Duration(Enum):
    MINS_15 = '15m'
    MINS_120 = '2h'
    MINS_60 = '1h'
    MINS_30 = '30m'
    MINS_90 = '1h30m'


DURATION_TO_MINS: Dict[Duration, int] = {
    Duration.MINS_15: 15,
    Duration.MINS_120: 120,
    Duration.MINS_60: 60,
    Duration.MINS_30: 30,
    Duration.MINS_90: 90,
}

MINS_TO_DURATION: Dict[int, Duration] = {
    15: Duration.MINS_15,
    120: Duration.MINS_120,
    60: Duration.MINS_60,
    30: Duration.MINS_30,
    90: Duration.MINS_90,
}


def strToDuration(duration_str: str) -> Duration:
    """
    Convert a duration string rxd from FE to Duration enum
    :param duration_str: rxd from FE
    :return: Duration enum
    """
    for duration in Duration:
        if duration.value == duration_str:
            return duration
    raise InvalidDurationException(duration_str)


def strToStatus(status_str: str) -> Status:
    """
    Convert a status string rxd from FE to Status enum
    :param status_str: rxd from FE
    :return: Status enum
    """
    for status in Status:
        if status.value == status_str:
            return status
    raise InvalidStatusException(status_str)


def validate_patient_id(patient_id: str) -> bool:
    """
    Perform modulo 11 check on patient_id https://www.datadictionary.nhs.uk/attributes/nhs_number.html
    :param patient_id: string representing the number to check
    :return: True if checksum digit matches
    """
    try:
        if len(patient_id) != 10:
            return False
        acc = 0
        for idx, ch in enumerate(patient_id[:9]):
            acc += int(ch) * (10-idx)
        chk_digit = 11 - acc % 11
        csum = 0 if chk_digit == 11 else chk_digit
        if csum == 10:
            return False
        return int(patient_id[9:]) == csum
    except ValueError:
        return False


# UK Gov Mainland Postcode Regex
POSTCODE_REGEX = r"^([A-PR-UWYZ0-9][A-HK-Y0-9][AEHMNPRTVXY0-9]?[ABEHMNPRVWXY0-9]? {1,2}[0-9][ABD-HJLN-UW-Z]{2}|GIR 0AA)$"
MIN_POSTCODE_LENGTH = 5


def validate_postcode(postcode: str) -> bool:
    """
    Validate a postcode according to regex specified by UK Gov
    Allow for incorrect placing of space char
    :param postcode: postcode string to check
    :return: True if matches postcode format
    """
    # Get rid of any spaces
    no_space = postcode.replace(" ", "")
    # Check is at least minimum length
    if len(no_space) < MIN_POSTCODE_LENGTH:
        return False
    # Test with spaces at permitted indices, TODO: check order of most common first
    for permitted_space_idx in [4, 3, 2]:
        if re.match(POSTCODE_REGEX, f"{no_space[:permitted_space_idx]} {no_space[permitted_space_idx:]}"):
            return True
    return False


"""
* Utility functions for handling FE data *
Rather than let these functions handle optional FE fields I decided
to do handling of that where they are used, in order to limit the number of 
Optional values seeping into the application as much as possible 
"""


def get_str_field(args: dict, field_name: str) -> str:
    """
    Get a string field from the args rxd from the FE
    Raise Exception if not present
    :param args: Args originating from FE
    :param field_name: Name of the field requested
    :return: field value string
    """
    if field_name not in args.keys():
        raise MissingFieldException(field_name)
    return str(args[field_name])


def get_duration_field(args: dict, field_name: str) -> Duration:
    """
    Get duration field str and convert to enum
    :param args: Args originating from FE
    :param field_name: Name of the field requested
    :return: Duration enum
    """
    field = get_str_field(args, field_name)
    return strToDuration(field)


def get_status_field(args: dict, field_name: str) -> Status:
    """
    Get status field str and convert to enum
    :param args: Args originating from FE
    :param field_name: Name of the field requested
    :return: Status enum
    """
    field = get_str_field(args, field_name)
    return strToStatus(field)


def get_date_field(args: dict, field_name: str) -> date:
    """
    Get date field str and convert to enum.
    The parser is lenient
    :param args: Args originating from FE
    :param field_name: Name of the field requested
    :return: date value
    """
    field = get_str_field(args, field_name)
    try:
        return parse(field, fuzzy=True).date()
    except ParserError as pe:
        raise InvalidDateException(field) from pe


def get_datetime_field(args: dict, field_name: str) -> datetime:
    """
    Get datetime field str and convert to enum.
    The parser is lenient
    :param args: Args originating from FE
    :param field_name: Name of the field requested
    :return: datetime value
    """
    field = get_str_field(args, field_name)
    try:
        return parse(field, fuzzy=True).utcnow()
    except ParserError as pe:
        raise InvalidDateTimeException(field) from pe


def get_postcode_str(args: dict, field_name: str) -> str:
    """
    Get postcode field str and validate.
    :param args: Args originating from FE
    :param field_name: Name of the field requested
    :return: validated postcode str
    """
    postcode = get_str_field(args, field_name)
    if not validate_postcode(postcode):
        raise InvalidPostcodeException(postcode)
    return postcode


def get_patient_id(args: dict, field_name: str) -> str:
    """
    Get NHS Number field str and validate.
    :param args: Args originating from FE
    :param field_name: Name of the field requested
    :return: validated NHS Number str
    """
    patient_id = get_str_field(args, field_name)
    if not validate_patient_id(patient_id):
        raise InvalidPatientIdException(patient_id)
    return patient_id
