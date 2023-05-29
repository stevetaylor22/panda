import uuid
from copy import copy
from datetime import date
from datetime import datetime
from typing import Optional
from typing import List
from unittest import TestCase

from dateutil.relativedelta import relativedelta

from application import PatientAppointmentsApp
from datastore import DataStore
from datastore import Patient
from datastore import Appointment
from exceptions import TimeInThePastException
from exceptions import NoResultsException
from exceptions import InvalidStatusChangeException
from exceptions import TimeInTheFutureException
from exceptions import PatientNotFoundException
from utils import Duration
from utils import Status


class MockDataStore(DataStore):

    def __init__(self):
        self.one_appointment = Appointment("a1504ef1-dcdf-44ba-950c-debb711f8175", "2179136439", Status.ACTIVE.value,
                                           datetime.now() + relativedelta(years=1), 90,
                                           "Francis Stewart", "gastroentology", "LA10 3TZ")
        self.cancelled_appointment = copy(self.one_appointment)
        self.cancelled_appointment.status = Status.CANCELLED.value
        self.one_patient = Patient("2179136439", "Francis Stewart",
                                   (datetime.now() - relativedelta(years=1)).date(), "LA10 3TZ")

    def create_appointment(self, patient: str, appointment_time: datetime, duration_mins: int, clinician: str,
                           department: str, postcode: str, appointment_id: Optional[str] = None) -> str:
        return str(uuid.uuid4())

    def get_appointment(self, appointment_id: str) -> Appointment:
        return self.one_appointment

    def get_appointments(self, patient_id: str) -> List[Appointment]:
        return [self.one_appointment]

    def get_clinician_appointments(self, clinician: str) -> List[Appointment]:
        pass

    def update_appointment(self, appointment_id: str, appointment_time: Optional[datetime] = None,
                           duration_mins: Optional[int] = None, clinician: Optional[str] = None,
                           status: Optional[str] = None) -> str:
        return "a1504ef1-dcdf-44ba-950c-debb711f8175"

    def create_patient(self, patient: str, date_of_birth: date, patient_name: str, postcode: str) -> str:
        return patient

    def update_patient(self, patient: str, date_of_birth: Optional[date] = None, patient_name: Optional[str] = None,
                       postcode: Optional[str] = None) -> str:
        return patient

    def get_patient(self, patient_id) -> Patient:
        return self.one_patient

    def findPatient(self, patient_name: str, date_of_birth: Optional[date]) -> List[Patient]:
        return [self.one_patient]

    def delete_patient(self, patient_id: str) -> str:
        return patient_id

    def is_db_empty(self) -> bool:
        return False


class TestPatientAppointmentsApp(TestCase):
    def setUp(self) -> None:
        self.data_store = MockDataStore()
        self.patient_app = PatientAppointmentsApp(self.data_store)

    def test_create_appointment(self):
        now = datetime.now()
        test_date_time_future = now + relativedelta(years=1)
        result = self.patient_app.create_appointment("2179136439", test_date_time_future, Duration.MINS_90,
                                                     "Francis Stewart", "gastroentology", "LA10 3TZ")
        self.assertTrue(isinstance(result["appointment_id"], str))

        test_date_time_past = now - relativedelta(years=1)
        with self.assertRaises(TimeInThePastException):
            self.patient_app.create_appointment("2179136439", test_date_time_past, Duration.MINS_90,
                                                "Francis Stewart", "gastroentology", "LA10 3TZ")

    def test_get_appointment(self):
        result = self.patient_app.get_appointment("a1504ef1-dcdf-44ba-950c-debb711f8175")
        self.assertTrue(result == {'clinician': 'Francis Stewart',
                                   'department': 'gastroentology',
                                   'duration': '1h30m',
                                   'id': 'a1504ef1-dcdf-44ba-950c-debb711f8175',
                                   'patient': '2179136439',
                                   'postcode': 'LA10 3TZ',
                                   'status': 'active',
                                   'time': self.data_store.one_appointment.time})
        self.data_store.one_appointment = None
        with self.assertRaises(NoResultsException):
            self.patient_app.get_appointment("a1504ef1-dcdf-44ba-950c-debb711f8175")

    def test_update_appointment(self):
        result = self.patient_app.update_appointment("a1504ef1-dcdf-44ba-950c-debb711f8175",
                                                     status=Status.ATTENDED.value)
        self.assertTrue(result["appointment_id"] == "a1504ef1-dcdf-44ba-950c-debb711f8175")
        self.data_store.one_appointment = self.data_store.cancelled_appointment
        with self.assertRaises(InvalidStatusChangeException):
            self.patient_app.update_appointment("a1504ef1-dcdf-44ba-950c-debb711f8175", status=Status.ACTIVE.value)

    def test_create_patient(self):
        now = datetime.now()
        test_date_time_future = now + relativedelta(years=1)
        test_date_time_past = now - relativedelta(years=1)
        result = self.patient_app.create_patient("2179136439", test_date_time_past.date(), "Chloe Cooney", "LS1 5XT")
        self.assertTrue(result["patient_id"] == "2179136439")
        with self.assertRaises(TimeInTheFutureException):
            self.patient_app.create_patient("2179136439", test_date_time_future.date(), "Chloe Cooney", "LS1 5XT")

    def test_get_patient(self):
        result = self.patient_app.get_patient("2179136439")
        self.assertEqual(result, {'date_of_birth': self.data_store.one_patient.date_of_birth,
                                  'name': 'Francis Stewart',
                                  'patient': '2179136439',
                                  'postcode': 'LA10 3TZ'})
        self.data_store.one_patient = None
        with self.assertRaises(PatientNotFoundException):
            self.patient_app.get_patient("2179136439")
