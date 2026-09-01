from sqlalchemy import Column, Integer, String,Boolean, DateTime
from database import Base

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String, unique=True, index=True)
    name = Column(String)
    age = Column(Integer)
    gender = Column(String)
    phone = Column(String)
    blood = Column(String)


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String)
    doctor = Column(String)
    date = Column(String)
    time = Column(String)
class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String, nullable=False)
    message = Column(String, nullable=False)
    notification_type = Column(String, nullable=False)
    is_read = Column(Boolean, default=False)
class Consultation(Base):
    __tablename__ = "consultations"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String, nullable=False)
    doctor = Column(String, nullable=False)
    symptoms = Column(String, nullable=False)
    diagnosis = Column(String, nullable=False)
    treatment = Column(String, nullable=False)


class Prescription(Base):
    __tablename__ = "prescriptions"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String, nullable=False)
    doctor = Column(String, nullable=False)
    medicine = Column(String, nullable=False)
    dosage = Column(String, nullable=False)
    duration = Column(String, nullable=False)
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False)
    patient_id = Column(String, nullable=True)
class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False)
    action = Column(String, nullable=False)
    details = Column(String, nullable=True)
    timestamp = Column(DateTime, nullable=True)