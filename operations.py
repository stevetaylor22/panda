import json

from datastore import get_data_store
from datetime import date
from datetime import datetime
from typing import List
from typing import Optional
from typing import Union
from typing import Tuple

from exceptions import DataEntryFieldException
from exceptions import InvalidFieldException
from exceptions import MissingFieldException
from application import PatientAppointmentsApp

from utils import get_patient_id
from utils import get_duration_field
from utils import get_status_field
from utils import get_datetime_field
from utils import get_str_field
from utils import get_postcode_str
from utils import get_date_field
from utils import Duration
from utils import Status

# Get the configured DataStore
data_store = get_data_store()
# Use configure DataStore to initialise App class instance
appointments_app = PatientAppointmentsApp(data_store)


#######################
# APPOINTMENT HANDLERS
#######################
def create_appointment(**kwargs) -> Tuple[Union[dict, str], int]:
    existing_id: Optional[str] = None

    try:
        existing_id = get_str_field(kwargs, "id")
    except MissingFieldException:
        # that's ok, it's optional
        pass

    try:
        patient = get_patient_id(kwargs, 'patient')
        appointment_time = get_datetime_field(kwargs, 'time')
        duration = get_duration_field(kwargs, 'duration')
        clinician = get_str_field(kwargs, 'clinician')
        department = get_str_field(kwargs, 'department')
        postcode = get_postcode_str(kwargs, 'postcode')
        return appointments_app.create_appointment(patient, appointment_time, duration,
                                                   clinician, department, postcode, existing_id=existing_id), 200
    except DataEntryFieldException as fe:
        return fe.user_message, 400


def get_appointment(**kwargs) -> Tuple[Union[dict, str], int]:
    try:
        appointment_id = get_str_field(kwargs, 'id')
        return appointments_app.get_appointment(appointment_id), 200
    except DataEntryFieldException as fe:
        return fe.user_message, 400


def get_patient_appointments(**kwargs) -> Tuple[Union[List[dict], str], int]:
    try:
        patient = get_patient_id(kwargs, 'patient')
        return appointments_app.get_patient_appointments(patient), 200
    except DataEntryFieldException as fe:
        return fe.user_message, 400


def get_clinician_appointments(**kwargs) -> Tuple[Union[List[dict], str], int]:
    try:
        clinician = get_str_field(kwargs, 'clinician')
        return appointments_app.get_clinician_appointments(clinician), 200
    except DataEntryFieldException as fe:
        return fe.user_message, 400


def update_appointment(**kwargs) -> Tuple[Union[dict, str], int]:
    appointment_time: Optional[datetime] = None
    duration: Optional[Duration] = None
    clinician: Optional[str] = None
    status: Optional[Status] = None

    try:
        # Don't mind missing field exceptions as these fields are optional
        try:
            appointment_time = get_datetime_field(kwargs, 'time')
        except MissingFieldException:
            pass
        try:
            duration = get_duration_field(kwargs, 'duration')
        except MissingFieldException:
            pass
        try:
            clinician = get_str_field(kwargs, 'clinician')
        except MissingFieldException:
            pass
        try:
            status = get_status_field(kwargs, 'status')
        except MissingFieldException:
            pass
        # However, we do want to capture invalid fields if they've been included
    except InvalidFieldException as ife:
        return ife.user_message, 400

    try:
        appointment_id = get_str_field(kwargs, 'id')
        return appointments_app.update_appointment(appointment_id, appointment_time=appointment_time,
                                                   duration=duration, clinician=clinician, status=status), 200
    except DataEntryFieldException as fe:
        return fe.user_message, 400


#######################
# PATIENT HANDLERS
#######################
def create_patient(**kwargs) -> Tuple[Union[dict, str], int]:
    try:
        patient = get_patient_id(kwargs, 'nhs_number')
        date_of_birth = get_date_field(kwargs, 'date_of_birth')
        patient_name = get_str_field(kwargs, 'name')
        postcode = get_postcode_str(kwargs, 'postcode')
        return appointments_app.create_patient(patient, date_of_birth, patient_name, postcode), 200
    except DataEntryFieldException as fe:
        return fe.user_message, 400


def update_patient(**kwargs) -> Tuple[Union[dict, str], int]:
    date_of_birth: Optional[date] = None
    patient_name: Optional[str] = None
    postcode: Optional[str] = None

    try:
        # Don't mind missing field exceptions as these fields are optional
        try:
            date_of_birth: Optional[date] = get_date_field(kwargs, 'date_of_birth')
        except MissingFieldException:
            pass
        try:
            patient_name = get_str_field(kwargs, 'name')
        except MissingFieldException:
            pass
        try:
            postcode = get_postcode_str(kwargs, 'postcode')
        except MissingFieldException:
            pass
        # However, we do want to capture invalid fields if they've been included
    except InvalidFieldException as ife:
        return ife.user_message, 400

    try:
        patient_id = get_patient_id(kwargs, 'nhs_number')
        return appointments_app.update_patient(patient_id, date_of_birth=date_of_birth,
                                               patient_name=patient_name, postcode=postcode), 200
    except DataEntryFieldException as fe:
        return fe.user_message, 400


def get_patient(**kwargs) -> Tuple[Union[dict, str], int]:
    try:
        patient_id = get_patient_id(kwargs, 'nhs_number')
        return appointments_app.get_patient(patient_id), 200
    except DataEntryFieldException as fe:
        return fe.user_message, 400


def find_patient(**kwargs) -> Tuple[Union[List[dict], str], int]:
    date_of_birth: Optional[date] = None

    # Don't mind missing field exceptions as these fields are optional
    try:
        date_of_birth: Optional[date] = get_date_field(kwargs, 'date_of_birth')
    except MissingFieldException:
        pass
    # However, we do want to capture invalid fields if they've been included
    except InvalidFieldException as ife:
        return ife.user_message, 400

    try:
        patient_name = get_str_field(kwargs, 'name')
        return appointments_app.find_patient(patient_name, date_of_birth), 200
    except DataEntryFieldException as fe:
        return fe.user_message, 400


def delete_patient(**kwargs) -> Tuple[Union[dict, str], int]:
    try:
        patient_id = get_str_field(kwargs, 'nhs_number')
        return appointments_app.delete_patient(patient_id), 200
    except DataEntryFieldException as fe:
        return fe.user_message, 400


def populate_sample_data() -> None:
    with open("./sample_data/example_patients.json", "r") as json_file:
        contents = json.load(json_file)
        for jDict in contents:
            create_patient(**jDict)
    with open("./sample_data/example_appointments.json", "r") as json_file:
        contents = json.load(json_file)
        for jDict in contents:
            create_appointment(**jDict)


# Application Evaluation Facility
# Populate empty database with sample data
if data_store.is_db_empty():
    populate_sample_data()

