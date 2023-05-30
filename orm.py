import uuid
from datetime import date
from datetime import datetime
from typing import List
from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy import Column
from sqlalchemy import Date
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import select
from sqlalchemy.orm import declarative_base
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Session

from datastore import DataStore
from datastore import Appointment
from datastore import Patient
from exceptions import AppointmentNotFoundException
from exceptions import PatientNotFoundException
from exceptions import PatientAlreadyExistsException
from utils import Status

Base = declarative_base()


class ORMPatient(Base, Patient):
    __tablename__ = 'patient'
    nhs_num = Column(String(10), primary_key=True)
    name = Column('name', String(50))
    date_of_birth = Column('date_of_birth', Date)
    postcode = Column('postcode', String(8))

    def __init__(self, nhs_num: str, name: str, date_of_birth: date, postcode: str):
        super(ORMPatient, self).__init__(nhs_num=nhs_num, name=name, date_of_birth=date_of_birth, postcode=postcode)


class ORMAppointment(Base, Appointment):
    __tablename__ = 'appointments'
    id = Column(String(36), primary_key=True)
    patient_id = Column(String(10), ForeignKey('patient.nhs_num'))
    status = Column('status', String(10))
    time = Column('title', DateTime)
    duration_mins = Column('duration_mins', Integer)
    clinician = Column('clinician', String(50))
    department = Column('department', String(20))
    postcode = Column('postcode', String(8))
    patient = relationship('ORMPatient')

    def __init__(self, id: str, patient_id: str, status: str, time: datetime, duration_mins: int, clinician: str,
                 department: str, postcode: str):
        super(ORMAppointment, self).__init__(id=id, patient_id=patient_id, status=status, time=time,
                                             duration_mins=duration_mins, clinician=clinician, department=department,
                                             postcode=postcode)


class AlchemyDatastore(DataStore):

    def __init__(self, db_url: str):
        self.engine = create_engine(db_url, echo=True)
        Base.metadata.create_all(self.engine)

    def create_appointment(self, patient: str, appointment_time: datetime, duration_mins: int,
                           clinician: str, department: str, postcode: str, appointment_id: Optional[str] = None) -> str:
        if appointment_id is None:
            appointment_id = str(uuid.uuid4())
        appointment = ORMAppointment(appointment_id, patient, Status.ACTIVE.value, appointment_time, duration_mins,
                                     clinician, department, postcode)
        with Session(self.engine) as session:
            session.add(appointment)
            session.commit()
        return appointment_id

    def get_appointment(self, appointment_id: str) -> Appointment:
        stmt = select(ORMAppointment).where(ORMAppointment.id == appointment_id)
        with Session(self.engine) as session:
            return session.scalar(stmt)

    def get_appointments(self, patient_id: str) -> List[Appointment]:
        stmt = select(ORMAppointment).where(ORMAppointment.patient_id == patient_id)
        with Session(self.engine) as session:
            return [appt for appt in session.scalars(stmt)]

    def get_clinician_appointments(self, clinician: str) -> List[Appointment]:
        stmt = select(ORMAppointment).where(ORMAppointment.clinician == clinician)
        with Session(self.engine) as session:
            return [appt for appt in session.scalars(stmt)]

    def update_appointment(self, appointment_id: str, appointment_time: Optional[datetime] = None,
                           duration_mins: Optional[int] = None, clinician: Optional[str] = None,
                           status: Optional[str] = None) -> str:
        stmt = select(ORMAppointment).where(ORMAppointment.id == appointment_id)
        with Session(self.engine) as session:
            appt: ORMAppointment = session.scalar(stmt)

            if appt is None:
                raise AppointmentNotFoundException(appointment_id)
            do_commit = False
            if appointment_time is not None:
                appt.time = appointment_time
                do_commit = True
            if duration_mins is not None:
                appt.duration_mins = duration_mins
                do_commit = True
            if clinician is not None:
                appt.clinician = clinician
                do_commit = True
            if status is not None:
                appt.status = status
                do_commit = True

            if do_commit:
                session.commit()
        return appointment_id

    def create_patient(self, patient_id: str, date_of_birth: date, patient_name: str, postcode: str) -> str:
        patient = ORMPatient(patient_id, patient_name, date_of_birth, postcode)
        try:
            with Session(self.engine) as session:
                session.add(patient)
                session.commit()
        except IntegrityError as ie:
            raise PatientAlreadyExistsException(patient_id)
        return patient_id

    def update_patient(self, patient_id: str, date_of_birth: Optional[date] = None,
                       patient_name: Optional[str] = None, postcode: Optional[str] = None):
        stmt = select(ORMPatient).where(ORMPatient.nhs_num == patient_id)
        with Session(self.engine) as session:
            patient: ORMPatient = session.scalar(stmt)
            if patient is None:
                raise PatientNotFoundException(patient_id)
            do_commit = False
            if date_of_birth is not None:
                patient.date_of_birth = date_of_birth
                do_commit = True
            if patient_name is not None:
                patient.name = patient_name
                do_commit = True
            if postcode is not None:
                patient.postcode = postcode
                do_commit = True

            if do_commit:
                session.commit()
        return patient_id

    def get_patient(self, patient_id: str) -> Patient:
        stmt = select(ORMPatient).where(ORMPatient.nhs_num == patient_id)
        with Session(self.engine) as session:
            return session.scalar(stmt)

    def findPatient(self, patient_name: str, date_of_birth: Optional[date]) -> List[Patient]:
        if date_of_birth is None:
            stmt = select(ORMPatient).where(ORMPatient.name == patient_name)
        else:
            stmt = select(ORMPatient).where(ORMPatient.name == patient_name and
                                            ORMPatient.date_of_birth == date_of_birth)
        with Session(self.engine) as session:
            return [patient for patient in session.scalars(stmt)]

    def delete_patient(self, patient_id: str) -> str:
        stmt = select(ORMPatient).where(ORMPatient.nhs_num == patient_id)
        with Session(self.engine) as session:
            patient = session.scalar(stmt)
            if patient is None:
                raise PatientNotFoundException(patient_id)
            session.delete(patient)
            session.commit()
        return patient_id

    def is_db_empty(self) -> bool:
        with Session(self.engine) as session:
            return session.query(ORMAppointment).count() == 0 and session.query(ORMPatient).count() == 0
