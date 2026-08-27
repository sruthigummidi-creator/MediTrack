from sqlalchemy import Column, Integer, String
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