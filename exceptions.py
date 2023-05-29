import messages as msgs


class MissingDatastoreException(Exception):
    def __init__(self, msg: str):
        super(MissingDatastoreException, self).__init__(msg)


class DataEntryFieldException(Exception):
    def __init__(self, msg: str):
        super(DataEntryFieldException, self).__init__(msg)
        self.user_message = msg


class InvalidStatusChangeException(DataEntryFieldException):
    def __init__(self, msg: str):
        super(InvalidStatusChangeException, self).__init__(msg)


class NoResultsException(DataEntryFieldException):
    def __init__(self, field_name: str):
        super(NoResultsException, self).__init__(f"{msgs.MSG_APPT_NOT_FOUND} {field_name}")
        self.field_name = field_name


class MissingFieldException(DataEntryFieldException):
    def __init__(self, field_name: str):
        super(MissingFieldException, self).__init__(f"{msgs.MSG_MISSING_FIELD} {field_name}")
        self.field_name = field_name


class InvalidFieldException(DataEntryFieldException):
    def __init__(self, msg: str):
        super(InvalidFieldException, self).__init__(msg)


class InvalidDateException(InvalidFieldException):
    def __init__(self, field: str):
        super(InvalidDateException, self).__init__(f"{msgs.MSG_FIELD_NOT_DATE} {field}")
        self.field = field


class InvalidDateTimeException(InvalidFieldException):
    def __init__(self, field: str):
        super(InvalidDateTimeException, self).__init__(f"{msgs.MSG_FIELD_NOT_DATETIME} {field}")
        self.field = field


class InvalidPostcodeException(InvalidFieldException):
    def __init__(self, field: str):
        super(InvalidPostcodeException, self).__init__(f"{msgs.MSG_FIELD_INVALID_POSTCODE} {field}")
        self.field = field


class InvalidPatientIdException(InvalidFieldException):
    def __init__(self, field: str):
        super(InvalidPatientIdException, self).__init__(f"{msgs.MSG_FIELD_INVALID_PATIENT_ID} {field}")
        self.field = field


class InvalidDurationException(InvalidFieldException):
    def __init__(self, field: str):
        super(InvalidDurationException, self).__init__(f"{msgs.MSG_FIELD_INVALID_DURATION} {field}")
        self.field = field


class InvalidStatusException(InvalidFieldException):
    def __init__(self, field: str):
        super(InvalidStatusException, self).__init__(f"{msgs.MSG_FIELD_INVALID_STATUS} {field}")
        self.field = field


class AppointmentNotFoundException(InvalidFieldException):
    def __init__(self, field: str):
        super(AppointmentNotFoundException, self).__init__(f"{msgs.MSG_FIELD_INVALID_APPOINTMENT} {field}")
        self.field = field


class TimeInThePastException(InvalidFieldException):
    def __init__(self, field: str):
        super(TimeInThePastException, self).__init__(f"{msgs.MSG_FIELD_TIME_PAST} {field}")
        self.field = field


class TimeInTheFutureException(InvalidFieldException):
    def __init__(self, field: str):
        super(TimeInTheFutureException, self).__init__(f"{msgs.MSG_FIELD_TIME_FUTURE} {field}")
        self.field = field


class PatientAlreadyExistsException(InvalidFieldException):
    def __init__(self, field: str):
        super(PatientAlreadyExistsException, self).__init__(f"{msgs.MSG_FIELD_PATIENT_EXISTS} {field}")
        self.field = field


class PatientNotFoundException(InvalidFieldException):
    def __init__(self, field: str):
        super(PatientNotFoundException, self).__init__(f"{msgs.MSG_PATIENT_NOT_FOUND} {field}")
        self.field = field
