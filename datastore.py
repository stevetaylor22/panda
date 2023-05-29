from datetime import datetime
from datetime import date
from typing import Protocol
from typing import Optional
from typing import List

from exceptions import MissingDatastoreException


"""
Abstract DataStore Definition

This file contains classes which exist to completely abstract
Data Storage implementation from use

The function set_data_store and get_data_store are important
as the are used to set and retrieve the live application 
DataStore instance
"""


class Appointment:
    """
    Data class containing Appointment information
    """
    def __init__(self, id: str, patient_id: str, status: str, time: datetime, duration_mins: int, clinician: str,
                 department: str, postcode: str):
        self.id = id
        self.patient_id = patient_id
        self.status = status
        self.time = time
        self.duration_mins = duration_mins
        self.clinician = clinician
        self.department = department
        self.postcode = postcode


class Patient:
    """
    Data class containing Patient information
    """
    def __init__(self, nhs_num: str, name: str, date_of_birth: date, postcode: str):
        self.nhs_num = nhs_num
        self.name = name
        self.date_of_birth = date_of_birth
        self.postcode = postcode


class DataStore(Protocol):
    """
    Abstract Data Store Definition
    """
    def create_appointment(self, patient: str, appointment_time: datetime, duration_mins: int,
                           clinician: str, department: str, postcode: str, appointment_id: Optional[str] = None) -> str:
        ...

    def get_appointment(self, appointment_id: str) -> Appointment:
        ...

    def get_appointments(self, patient_id: str) -> List[Appointment]:
        ...

    def get_clinician_appointments(self, clinician: str) -> List[Appointment]:
        ...

    def update_appointment(self, appointment_id: str, appointment_time: Optional[datetime] = None,
                           duration_mins: Optional[int] = None, clinician: Optional[str] = None,
                           status: Optional[str] = None) -> str:
        ...

    def create_patient(self, patient: str, date_of_birth: date, patient_name: str, postcode: str) -> str:
        ...

    def update_patient(self, patient: str, date_of_birth: Optional[date] = None,
                       patient_name: Optional[str] = None, postcode: Optional[str] = None) -> str:
        ...

    def get_patient(self, patient_id) -> Patient:
        ...

    def findPatient(self, patient_name: str, date_of_birth: Optional[date]) -> List[Patient]:
        ...

    def delete_patient(self, patient_id: str) -> str:
        ...

    def is_db_empty(self) -> bool:
        ...


# The DataStore Instance that the app will use
DATA_STORE: Optional[DataStore] = None


def set_data_store(data_store: DataStore) -> None:
    """
    Call this function to set the DataStore used by the app
    :param data_store: An implementation of DataStore
    :return: None
    """
    global DATA_STORE
    DATA_STORE = data_store


def get_data_store() -> DataStore:
    """
    Call this function to get the DataStore for the app to use
    :return: An implementation of DataStore
    """
    global DATA_STORE
    if DATA_STORE is None:
        raise MissingDatastoreException("No DataStore instance has been set for PANDA")
    return DATA_STORE
