from datetime import datetime
from datetime import date
from typing import List
from typing import Optional

from datastore import DataStore, Appointment, Patient
from exceptions import NoResultsException, TimeInTheFutureException
from exceptions import InvalidStatusChangeException
from exceptions import TimeInThePastException
from exceptions import PatientNotFoundException
from messages import MSG_CANT_REINSTATE_CANCELLED
from utils import Duration, MINS_TO_DURATION, Status
from utils import DURATION_TO_MINS


def appointment_to_dict(appointment: Appointment) -> dict:
    return {
        "clinician": appointment.clinician,
        "department": appointment.department,
        "duration": MINS_TO_DURATION[appointment.duration_mins].value,
        "id": appointment.id,
        "patient": appointment.patient_id,
        "postcode": appointment.postcode,
        "status": appointment.status,
        "time": appointment.time
    }


def patient_to_dict(patient: Patient) -> dict:
    return {
        "date_of_birth": patient.date_of_birth,
        "name": patient.name,
        "patient": patient.nhs_num,
        "postcode": patient.postcode
    }


def time_in_the_future(time: datetime) -> bool:
    return time > datetime.now()


def date_in_the_future(dateVal: date) -> bool:
    return dateVal > datetime.now().date()


APPOINTMENT_ID_FIELD = "appointment_id"
PATIENT_ID_FIELD = "patient_id"


class PatientAppointmentsApp:
    """
    Repository of Application business logic
    Handles validated requests and performs related queries
    Checks for disallowed requests
    """
    def __init__(self, dataStore: DataStore):
        self.dataStore = dataStore

    def create_appointment(self, patient: str, appointment_time: datetime, duration: Duration,
                           clinician: str, department: str, postcode: str, existing_id: Optional[str] = None) -> dict:
        duration_mins = DURATION_TO_MINS[duration]
        if not time_in_the_future(appointment_time):
            raise TimeInThePastException(str(appointment_time))
        appointment_id = self.dataStore.create_appointment(patient, appointment_time, duration_mins,
                                                           clinician, department, postcode, appointment_id=existing_id)
        return {APPOINTMENT_ID_FIELD: appointment_id}

    def get_appointment(self, appointment_id: str) -> dict:
        appointment = self.dataStore.get_appointment(appointment_id)
        if appointment is None:
            raise NoResultsException(appointment_id)
        return appointment_to_dict(appointment)

    def get_patient_appointments(self, patient: str) -> List[dict]:
        return [appointment_to_dict(appt) for appt in self.dataStore.get_appointments(patient)]

    def get_clinician_appointments(self, clinician: str) -> List[dict]:
        return [appointment_to_dict(appt) for appt in self.dataStore.get_clinician_appointments(clinician)]

    def update_appointment(self, appointment_id: str, *, appointment_time: Optional[datetime] = None,
                           duration: Optional[Duration] = None, clinician: Optional[str] = None,
                           status: Optional[str] = None) -> dict:
        if status is not None:
            appt: Appointment = self.dataStore.get_appointment(appointment_id)
            if appt.status == Status.CANCELLED.value and status == Status.ACTIVE.value:
                # Cancelled appointments cannot be reinstated
                raise InvalidStatusChangeException(MSG_CANT_REINSTATE_CANCELLED)
        duration_mins = DURATION_TO_MINS[duration] if duration is not None else None
        appt_id = self.dataStore.update_appointment(appointment_id, appointment_time=appointment_time,
                                                    duration_mins=duration_mins, clinician=clinician,
                                                    status=status)
        return {APPOINTMENT_ID_FIELD: appt_id}

    def create_patient(self, patient: str, date_of_birth: date, patient_name: str, postcode: str) -> dict:
        if date_in_the_future(date_of_birth):
            raise TimeInTheFutureException(str(date_of_birth))
        patient_id = self.dataStore.create_patient(patient, date_of_birth, patient_name, postcode)
        return {PATIENT_ID_FIELD: patient_id}

    def update_patient(self, patient: str, *, date_of_birth: Optional[date] = None,
                       patient_name: Optional[str] = None, postcode: Optional[str] = None) -> dict:
        patient_id = self.dataStore.update_patient(patient, date_of_birth=date_of_birth,
                                                   patient_name=patient_name, postcode=postcode)
        return {PATIENT_ID_FIELD: patient_id}

    def get_patient(self, patient_id: str) -> dict:
        patient: Patient = self.dataStore.get_patient(patient_id)
        if patient is None:
            raise PatientNotFoundException(patient_id)
        return patient_to_dict(patient)

    def find_patient(self, patient_name: str, date_of_birth: Optional[date]) -> List[dict]:
        return [patient_to_dict(patient) for patient in self.dataStore.findPatient(patient_name, date_of_birth)]

    def delete_patient(self, patient_id) -> dict:
        return {"patient": self.dataStore.delete_patient(patient_id)}
