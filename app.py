from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from database import engine, Base
from database import SessionLocal
import models


app = FastAPI()

templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="templates"), name="static")

Base.metadata.create_all(bind=engine)
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    db = SessionLocal()
    total_patients = db.query(models.Patient).count()
    total_appointments = db.query(models.Appointment).count()
    db.close()

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request,
            "total_patients": total_patients,
            "total_appointments": total_appointments
        }
    )


@app.get("/register", response_class=HTMLResponse)
def register(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="register.html",
        context={"request": request}
    )
@app.post("/register", response_class=HTMLResponse)
def save_patient(
    request: Request,
    patient_id: str = Form(...),
    name: str = Form(...),
    age: int = Form(...),
    gender: str = Form(...),
    phone: str = Form(...),
    blood: str = Form(...)
):
    db = SessionLocal()

    patient = models.Patient(
        patient_id=patient_id,
        name=name,
        age=age,
        gender=gender,
        phone=phone,
        blood=blood
    )

    db.add(patient)
    db.commit()
    db.close()

    return templates.TemplateResponse(
        request=request,
        name="success.html",
        context={
            "request": request,
            "title": "Patient Registered Successfully",
            "message": "Patient details have been saved to the database.",
            "icon": "✓"
        }
    )
@app.get("/patients", response_class=HTMLResponse)
def view_patients(request: Request):
    db = SessionLocal()

    patient_list = db.query(models.Patient).all()

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="patients.html",
        context={"request": request, "patient_list": patient_list}
    )
@app.get("/search", response_class=HTMLResponse)
def search_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="search.html",
        context={"request": request}
    )
@app.post("/search-result", response_class=HTMLResponse)
def search_result(request: Request, patient_id: str = Form(...)):
    db = SessionLocal()
    patient = db.query(models.Patient).filter(
        models.Patient.patient_id == patient_id
    ).first()
    db.close()

    return templates.TemplateResponse(
        request=request,
        name="search_result.html",
        context={
            "request": request,
            "patient": patient,
            "title": "Patient Found" if patient else "Patient Not Found"
        }
    )
@app.get("/update", response_class=HTMLResponse)
def update_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="update.html",
        context={"request": request}
    )
@app.post("/update", response_class=HTMLResponse)
def update_patient(
    request: Request,
    patient_id: str = Form(...),
    name: str = Form(...),
    age: int = Form(...),
    gender: str = Form(...),
    phone: str = Form(...),
    blood: str = Form(...)
):
    db = SessionLocal()
    patient = db.query(models.Patient).filter(
        models.Patient.patient_id == patient_id
    ).first()

    if patient:
        patient.name = name
        patient.age = age
        patient.gender = gender
        patient.phone = phone
        patient.blood = blood
        db.commit()
        db.close()

        return templates.TemplateResponse(
            request=request,
            name="action_result.html",
            context={
                "request": request,
                "success": True,
                "title": "Patient Updated Successfully",
                "message": "The patient details have been updated in the database.",
                "primary_text": "View Patients",
                "primary_link": "/patients",
                "secondary_text": "Update Another",
                "secondary_link": "/update"
            }
        )

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="action_result.html",
        context={
            "request": request,
            "success": False,
            "title": "Patient Not Found",
            "message": "No patient record was found with the entered Patient ID.",
            "primary_text": "Try Again",
            "primary_link": "/update",
            "secondary_text": "Back to MediTrack",
            "secondary_link": "/"
        }
    )
@app.get("/delete", response_class=HTMLResponse)
def delete_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="delete.html",
        context={"request": request}
    )
@app.post("/delete", response_class=HTMLResponse)
def delete_patient(
    request: Request,
    patient_id: str = Form(...)
):
    db = SessionLocal()

    patient = db.query(models.Patient).filter(
        models.Patient.patient_id == patient_id
    ).first()

    if patient:
        db.delete(patient)
        db.commit()
        db.close()

        return templates.TemplateResponse(
            request=request,
            name="action_result.html",
            context={
                "request": request,
                "success": True,
                "title": "Patient Deleted Successfully",
                "message": "The patient record has been deleted from the database.",
                "primary_text": "View Patients",
                "primary_link": "/patients",
                "secondary_text": "Delete Another",
                "secondary_link": "/delete"
            }
        )

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="action_result.html",
        context={
            "request": request,
            "success": False,
            "title": "Patient Not Found",
            "message": "No patient record was found with the entered Patient ID.",
            "primary_text": "Try Again",
            "primary_link": "/delete",
            "secondary_text": "Back to MediTrack",
            "secondary_link": "/"
        }
    )
@app.get("/book-appointment", response_class=HTMLResponse)
def book_appointment_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="book_appointment.html",
        context={"request": request}
    )

@app.post("/book-appointment", response_class=HTMLResponse)
def save_appointment(
    request: Request,
    patient_id: str = Form(...),
    doctor: str = Form(...),
    date: str = Form(...),
    time: str = Form(...)
):
    db = SessionLocal()

    existing = db.query(models.Appointment).filter(
        models.Appointment.doctor == doctor,
        models.Appointment.date == date,
        models.Appointment.time == time
    ).first()

    if existing:
        db.close()

        return templates.TemplateResponse(
            request=request,
            name="action_result.html",
            context={
                "request": request,
                "success": False,
                "title": "Slot Already Booked",
                "message": "This doctor already has an appointment at the selected date and time. Please choose another slot.",
                "primary_text": "Try Another Slot",
                "primary_link": "/book-appointment",
                "secondary_text": "View Appointments",
                "secondary_link": "/appointments"
            }
        )

    appointment = models.Appointment(
        patient_id=patient_id,
        doctor=doctor,
        date=date,
        time=time
    )

    db.add(appointment)
    db.commit()
    db.close()

    return templates.TemplateResponse(
        request=request,
        name="action_result.html",
        context={
            "request": request,
            "success": True,
            "title": "Appointment Booked Successfully",
            "message": "The appointment has been saved to the database.",
            "primary_text": "View Appointments",
            "primary_link": "/appointments",
            "secondary_text": "Book Another",
            "secondary_link": "/book-appointment"
        }
    )
@app.get("/appointments", response_class=HTMLResponse)
def view_appointments(request: Request):
    db = SessionLocal()
    appointment_list = db.query(models.Appointment).all()
    db.close()

    return templates.TemplateResponse(
        request=request,
        name="appointments.html",
        context={
            "request": request,
            "appointment_list": appointment_list
        }
    )

@app.get("/cancel-appointment", response_class=HTMLResponse)
def cancel_appointment_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="cancel_appointment.html",
        context={"request": request}
    )
@app.post("/cancel-appointment", response_class=HTMLResponse)
def cancel_appointment(
    request: Request,
    patient_id: str = Form(...)
):
    db = SessionLocal()
    appointment = db.query(models.Appointment).filter(
        models.Appointment.patient_id == patient_id
    ).first()

    if appointment:
        db.delete(appointment)
        db.commit()
        db.close()

        return templates.TemplateResponse(
            request=request,
            name="action_result.html",
            context={
                "request": request,
                "success": True,
                "title": "Appointment Cancelled Successfully",
                "message": "The appointment has been cancelled successfully.",
                "primary_text": "View Appointments",
                "primary_link": "/appointments",
                "secondary_text": "Cancel Another",
                "secondary_link": "/cancel-appointment"
            }
        )

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="action_result.html",
        context={
            "request": request,
            "success": False,
            "title": "Appointment Not Found",
            "message": "No appointment was found for the entered Patient ID.",
            "primary_text": "Try Again",
            "primary_link": "/cancel-appointment",
            "secondary_text": "View Appointments",
            "secondary_link": "/appointments"
        }
    )
@app.get("/consultation", response_class=HTMLResponse)
def consultation_page():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Start Consultation | MediTrack</title>
        <link rel="stylesheet" href="/static/style.css">
        <style>
            .consultation-page{
                min-height:100vh;
                background:#06172D;
                padding:60px 30px;
                display:flex;
                justify-content:center;
                box-sizing:border-box;
            }

            .consultation-card{
                width:100%;
                max-width:850px;
                background:#0D2947;
                border:1px solid #234766;
                border-radius:18px;
                overflow:hidden;
                box-shadow:0 20px 45px rgba(0,0,0,.3);
            }

            .consultation-header{
                display:flex;
                align-items:center;
                gap:18px;
                padding:30px 34px;
                background:#102F50;
                border-bottom:1px solid #234766;
            }

            .consultation-icon{
                width:58px;
                height:58px;
                border-radius:15px;
                background:#F4C542;
                color:#06172D;
                display:flex;
                align-items:center;
                justify-content:center;
                font-size:28px;
                font-weight:700;
            }

            .consultation-header span{
                display:block;
                margin-bottom:7px;
                color:#F4C542;
                font-size:10px;
                font-weight:800;
                letter-spacing:1.5px;
            }

            .consultation-header h1{
                margin:0 0 6px;
                color:#FFFFFF;
                font-size:27px;
            }

            .consultation-header p{
                margin:0;
                color:#9FB1C7;
                font-size:12px;
            }

            .consultation-card form{
                padding:32px 34px;
            }

            .consultation-grid{
                display:grid;
                grid-template-columns:1fr 1fr;
                gap:22px 26px;
            }

            .consultation-group{
                display:flex;
                flex-direction:column;
            }

            .consultation-group.full-width{
                grid-column:1/-1;
            }

            .consultation-group label{
                margin-bottom:8px;
                color:#DDE7F1;
                font-size:11px;
                font-weight:700;
            }

            .consultation-group input,
            .consultation-group textarea{
                width:100%;
                box-sizing:border-box;
                border:1px solid #315370;
                border-radius:9px;
                background:#081D35;
                color:#FFFFFF;
                padding:13px 14px;
                font-family:inherit;
                font-size:12px;
                outline:none;
            }

            .consultation-group input{
                height:47px;
            }

            .consultation-group textarea{
                min-height:90px;
                resize:vertical;
            }

            .consultation-group input::placeholder,
            .consultation-group textarea::placeholder{
                color:#7188A1;
            }

            .consultation-group input:focus,
            .consultation-group textarea:focus{
                border-color:#F4C542;
                box-shadow:0 0 0 4px rgba(244,197,66,.1);
            }

            .consultation-footer{
                margin-top:30px;
                padding-top:22px;
                border-top:1px solid #234766;
                display:flex;
                align-items:center;
                justify-content:space-between;
            }

            .consultation-back{
                color:#AFC0D1;
                text-decoration:none;
                font-size:12px;
                font-weight:600;
            }

            .consultation-back:hover{
                color:#F4C542;
            }

            .consultation-btn{
                height:46px;
                padding:0 25px;
                border:0;
                border-radius:9px;
                background:#F4C542;
                color:#06172D;
                font-size:12px;
                font-weight:800;
                cursor:pointer;
            }

            .consultation-btn:hover{
                background:#D9A91F;
            }

            @media(max-width:650px){
                .consultation-page{
                    padding:25px 15px;
                }

                .consultation-grid{
                    grid-template-columns:1fr;
                }

                .consultation-group.full-width{
                    grid-column:auto;
                }

                .consultation-footer{
                    flex-direction:column-reverse;
                    gap:15px;
                    align-items:stretch;
                }

                .consultation-btn{
                    width:100%;
                }

                .consultation-back{
                    text-align:center;
                }
            }
        </style>
    </head>

    <body>

        <div class="consultation-page">

            <div class="consultation-card">

                <div class="consultation-header">
                    <div class="consultation-icon">✚</div>

                    <div>
                        <span>CONSULTATION MANAGEMENT</span>
                        <h1>Start Consultation</h1>
                        <p>Record consultation details for a registered patient.</p>
                    </div>
                </div>

                <form action="/consultation" method="post">

                    <div class="consultation-grid">

                        <div class="consultation-group">
                            <label>Patient ID</label>
                            <input type="text" name="patient_id" placeholder="Enter Patient ID" required>
                        </div>

                        <div class="consultation-group">
                            <label>Doctor</label>
                            <input type="text" name="doctor" placeholder="Enter Doctor Name" required>
                        </div>

                        <div class="consultation-group full-width">
                            <label>Symptoms</label>
                            <textarea name="symptoms" placeholder="Enter patient symptoms" required></textarea>
                        </div>

                        <div class="consultation-group full-width">
                            <label>Diagnosis</label>
                            <textarea name="diagnosis" placeholder="Enter diagnosis" required></textarea>
                        </div>

                        <div class="consultation-group full-width">
                            <label>Treatment</label>
                            <textarea name="treatment" placeholder="Enter treatment details" required></textarea>
                        </div>

                    </div>

                    <div class="consultation-footer">
                        <a href="/" class="consultation-back">← Back to MediTrack</a>
                        <button type="submit" class="consultation-btn">Save Consultation</button>
                    </div>

                </form>

            </div>

        </div>

    </body>
    </html>
    """
@app.post("/consultation", response_class=HTMLResponse)
def save_consultation(
    patient_id: str = Form(...),
    doctor: str = Form(...),
    symptoms: str = Form(...),
    diagnosis: str = Form(...),
    treatment: str = Form(...)
):
    db = SessionLocal()

    patient = db.query(models.Patient).filter(
        models.Patient.patient_id == patient_id
    ).first()

    if not patient:
        db.close()

        return """
        <h1>Patient Not Found</h1>
        <p>Please enter a registered Patient ID.</p>
        <a href="/consultation">Try Again</a>
        <br><br>
        <a href="/">Back to MediTrack</a>
        """

    consultation = models.Consultation(
        patient_id=patient_id,
        doctor=doctor,
        symptoms=symptoms,
        diagnosis=diagnosis,
        treatment=treatment
    )

    db.add(consultation)
    db.commit()
    db.close()

    return """
<!DOCTYPE html>
<html>
<head>

    <title>Consultation Saved | MediTrack</title>

    <style>

        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            font-family: Arial, sans-serif;
            background: #06172D;
        }

        .success-page {
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 30px;
        }

        .success-card {
            width: 100%;
            max-width: 600px;
            background: #0D2947;
            border: 1px solid #315370;
            border-radius: 18px;
            padding: 45px;
            text-align: center;
            box-shadow: 0 20px 50px rgba(0,0,0,0.35);
        }

        .success-icon {
            width: 75px;
            height: 75px;
            margin: 0 auto 22px;
            border-radius: 50%;
            background: #F4C542;
            color: #06172D;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 38px;
            font-weight: bold;
        }

        .success-card h1 {
            margin: 0 0 12px;
            color: white;
            font-size: 27px;
        }

        .success-card p {
            margin: 0;
            color: #AFC0D1;
            font-size: 13px;
            line-height: 1.6;
        }

        .success-actions {
            margin-top: 30px;
            display: flex;
            justify-content: center;
            gap: 12px;
        }

        .success-btn {
            padding: 13px 20px;
            border-radius: 9px;
            background: #F4C542;
            color: #06172D;
            text-decoration: none;
            font-size: 12px;
            font-weight: bold;
        }

        .success-btn:hover {
            background: #D9A91F;
        }

        .success-btn.secondary {
            background: #173A5A;
            color: white;
            border: 1px solid #315370;
        }

        .success-btn.secondary:hover {
            background: #204967;
        }

        .success-back {
            display: inline-block;
            margin-top: 25px;
            color: #AFC0D1;
            text-decoration: none;
            font-size: 12px;
        }

        .success-back:hover {
            color: #F4C542;
        }

    </style>

</head>

<body>

    <div class="success-page">

        <div class="success-card">

            <div class="success-icon">
                ✓
            </div>

            <h1>
                Consultation Saved Successfully
            </h1>

            <p>
                The consultation details have been saved to the database.
            </p>

            <div class="success-actions">

                <a href="/consultation" class="success-btn secondary">
                    New Consultation
                </a>

                <a href="/consultations" class="success-btn">
                    View Consultation History
                </a>

            </div>

            <a href="/" class="success-back">
                ← Back to MediTrack
            </a>

        </div>

    </div>

</body>
</html>
"""

@app.get("/consultations", response_class=HTMLResponse)
def view_consultations():
    db = SessionLocal()

    consultation_list = db.query(models.Consultation).all()

    db.close()

    if not consultation_list:
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Consultation History | MediTrack</title>
            <style>
                * {
                    box-sizing: border-box;
                }

                body {
                    margin: 0;
                    font-family: Arial, sans-serif;
                    background: #06172D;
                    color: white;
                }

                .history-page {
                    min-height: 100vh;
                    padding: 50px 35px;
                }

                .history-container {
                    max-width: 1000px;
                    margin: auto;
                }

                .history-header {
                    margin-bottom: 30px;
                }

                .history-label {
                    color: #F4C542;
                    font-size: 10px;
                    font-weight: bold;
                    letter-spacing: 1.5px;
                }

                .history-header h1 {
                    margin: 8px 0;
                    font-size: 30px;
                }

                .history-header p {
                    color: #9FB1C7;
                    font-size: 13px;
                }

                .empty-card {
                    background: #0D2947;
                    border: 1px solid #315370;
                    border-radius: 18px;
                    padding: 60px;
                    text-align: center;
                }

                .empty-icon {
                    width: 65px;
                    height: 65px;
                    margin: auto auto 20px;
                    border-radius: 50%;
                    background: #F4C542;
                    color: #06172D;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 28px;
                    font-weight: bold;
                }

                .empty-card h2 {
                    margin-bottom: 10px;
                }

                .empty-card p {
                    color: #9FB1C7;
                }

                .back-btn {
                    display: inline-block;
                    margin-top: 25px;
                    color: #F4C542;
                    text-decoration: none;
                }
            </style>
        </head>

        <body>

            <div class="history-page">
                <div class="history-container">

                    <div class="history-header">
                        <span class="history-label">
                            CONSULTATION MANAGEMENT
                        </span>

                        <h1>Consultation History</h1>

                        <p>
                            View previous consultation records.
                        </p>
                    </div>

                    <div class="empty-card">

                        <div class="empty-icon">✓</div>

                        <h2>No Consultations Found</h2>

                        <p>
                            No consultation records are available yet.
                        </p>

                        <a href="/consultation" class="back-btn">
                            Start Consultation
                        </a>

                    </div>

                    <a href="/" class="back-btn">
                        ← Back to MediTrack
                    </a>

                </div>
            </div>

        </body>
        </html>
        """

    html = """
    <!DOCTYPE html>
    <html>
    <head>

        <title>Consultation History | MediTrack</title>

        <style>

            * {
                box-sizing: border-box;
            }

            body {
                margin: 0;
                font-family: Arial, sans-serif;
                background: #06172D;
                color: white;
            }

            .history-page {
                min-height: 100vh;
                padding: 50px 35px;
            }

            .history-container {
                max-width: 1000px;
                margin: auto;
            }

            .history-header {
                margin-bottom: 30px;
            }

            .history-label {
                color: #F4C542;
                font-size: 10px;
                font-weight: bold;
                letter-spacing: 1.5px;
            }

            .history-header h1 {
                margin: 8px 0;
                font-size: 30px;
            }

            .history-header p {
                margin: 0;
                color: #9FB1C7;
                font-size: 13px;
            }

            .consultation-record {
                background: #0D2947;
                border: 1px solid #315370;
                border-radius: 16px;
                padding: 25px;
                margin-bottom: 18px;
                box-shadow: 0 10px 25px rgba(0,0,0,.20);
            }

            .record-top {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding-bottom: 18px;
                border-bottom: 1px solid #315370;
                margin-bottom: 20px;
            }

            .patient-id {
                color: #F4C542;
                font-size: 14px;
                font-weight: bold;
            }

            .doctor-name {
                color: #FFFFFF;
                font-size: 13px;
            }

            .record-grid {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 18px;
            }

            .record-item {
                background: #081D35;
                border: 1px solid #244766;
                border-radius: 10px;
                padding: 15px;
            }

            .record-item label {
                display: block;
                color: #F4C542;
                font-size: 9px;
                font-weight: bold;
                letter-spacing: 1px;
                margin-bottom: 8px;
            }

            .record-item p {
                margin: 0;
                color: #DDE7F1;
                font-size: 12px;
                line-height: 1.6;
            }

            .history-back {
                display: inline-block;
                margin-top: 10px;
                color: #AFC0D1;
                text-decoration: none;
                font-size: 12px;
            }

            .history-back:hover {
                color: #F4C542;
            }

            @media(max-width:700px) {

                .history-page {
                    padding: 25px 15px;
                }

                .record-grid {
                    grid-template-columns: 1fr;
                }

                .record-top {
                    flex-direction: column;
                    align-items: flex-start;
                    gap: 8px;
                }
            }

        </style>

    </head>

    <body>

        <div class="history-page">

            <div class="history-container">

                <div class="history-header">

                    <span class="history-label">
                        CONSULTATION MANAGEMENT
                    </span>

                    <h1>Consultation History</h1>

                    <p>
                        View previous consultation records.
                    </p>

                </div>
    """

    for consultation in consultation_list:

        html += f"""
                <div class="consultation-record">

                    <div class="record-top">

                        <span class="patient-id">
                            Patient ID: {consultation.patient_id}
                        </span>

                        <span class="doctor-name">
                            Doctor: {consultation.doctor}
                        </span>

                    </div>

                    <div class="record-grid">

                        <div class="record-item">
                            <label>SYMPTOMS</label>
                            <p>{consultation.symptoms}</p>
                        </div>

                        <div class="record-item">
                            <label>DIAGNOSIS</label>
                            <p>{consultation.diagnosis}</p>
                        </div>

                        <div class="record-item">
                            <label>TREATMENT</label>
                            <p>{consultation.treatment}</p>
                        </div>

                    </div>

                </div>
        """

    html += """
                <a href="/" class="history-back">
                    ← Back to MediTrack
                </a>

            </div>

        </div>

    </body>
    </html>
    """

    return html
@app.get("/prescription", response_class=HTMLResponse)
def prescription_page():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Generate Prescription | MediTrack</title>

        <style>
            * {
                box-sizing: border-box;
            }

            body {
                margin: 0;
                font-family: Arial, sans-serif;
                background: #06172D;
            }

            .prescription-page {
                min-height: 100vh;
                padding: 50px 35px;
                display: flex;
                justify-content: center;
                align-items: flex-start;
            }

            .prescription-card {
                width: 100%;
                max-width: 850px;
                background: #0D2947;
                border: 1px solid #315370;
                border-radius: 18px;
                overflow: hidden;
                box-shadow: 0 20px 45px rgba(0,0,0,.30);
            }

            .prescription-header {
                display: flex;
                align-items: center;
                gap: 18px;
                padding: 30px 34px;
                background: #102F50;
                border-bottom: 1px solid #315370;
            }

            .prescription-icon {
                width: 58px;
                height: 58px;
                border-radius: 15px;
                background: #F4C542;
                color: #06172D;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 27px;
                font-weight: bold;
                flex-shrink: 0;
            }

            .prescription-header span {
                display: block;
                margin-bottom: 6px;
                color: #F4C542;
                font-size: 10px;
                font-weight: bold;
                letter-spacing: 1.5px;
            }

            .prescription-header h1 {
                margin: 0 0 6px;
                color: #FFFFFF;
                font-size: 27px;
            }

            .prescription-header p {
                margin: 0;
                color: #9FB1C7;
                font-size: 12px;
            }

            .prescription-card form {
                padding: 32px 34px;
            }

            .prescription-grid {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 22px 26px;
            }

            .prescription-group {
                display: flex;
                flex-direction: column;
            }

            .prescription-group label {
                margin-bottom: 8px;
                color: #DDE7F1;
                font-size: 11px;
                font-weight: bold;
            }

            .prescription-group input {
                width: 100%;
                height: 47px;
                padding: 0 14px;
                border: 1px solid #315370;
                border-radius: 9px;
                background: #081D35;
                color: #FFFFFF;
                font-size: 12px;
                outline: none;
            }

            .prescription-group input::placeholder {
                color: #7188A1;
            }

            .prescription-group input:focus {
                border-color: #F4C542;
                background: #0A2340;
                box-shadow: 0 0 0 4px rgba(244,197,66,.10);
            }

            .prescription-footer {
                margin-top: 30px;
                padding-top: 22px;
                border-top: 1px solid #315370;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }

            .prescription-back {
                color: #AFC0D1;
                text-decoration: none;
                font-size: 12px;
                font-weight: bold;
            }

            .prescription-back:hover {
                color: #F4C542;
            }

            .prescription-btn {
                height: 46px;
                padding: 0 25px;
                border: none;
                border-radius: 9px;
                background: #F4C542;
                color: #06172D;
                font-size: 12px;
                font-weight: bold;
                cursor: pointer;
            }

            .prescription-btn:hover {
                background: #D9A91F;
                transform: translateY(-2px);
            }

            @media(max-width:700px) {

                .prescription-page {
                    padding: 25px 15px;
                }

                .prescription-header {
                    padding: 24px;
                }

                .prescription-card form {
                    padding: 24px;
                }

                .prescription-grid {
                    grid-template-columns: 1fr;
                }

                .prescription-footer {
                    flex-direction: column-reverse;
                    gap: 15px;
                    align-items: stretch;
                }

                .prescription-btn {
                    width: 100%;
                }

                .prescription-back {
                    text-align: center;
                }
            }
        </style>
    </head>

    <body>

        <div class="prescription-page">

            <div class="prescription-card">

                <div class="prescription-header">

                    <div class="prescription-icon">
                        ✚
                    </div>

                    <div>
                        <span>PRESCRIPTION MANAGEMENT</span>

                        <h1>Generate Prescription</h1>

                        <p>
                            Create a prescription for a registered patient.
                        </p>
                    </div>

                </div>

                <form action="/prescription" method="post">

                    <div class="prescription-grid">

                        <div class="prescription-group">

                            <label>Patient ID</label>

                            <input
                                type="text"
                                name="patient_id"
                                placeholder="Enter Patient ID"
                                required
                            >

                        </div>

                        <div class="prescription-group">

                            <label>Doctor</label>

                            <input
                                type="text"
                                name="doctor"
                                placeholder="Enter Doctor Name"
                                required
                            >

                        </div>

                        <div class="prescription-group">

                            <label>Medicine</label>

                            <input
                                type="text"
                                name="medicine"
                                placeholder="Enter Medicine"
                                required
                            >

                        </div>

                        <div class="prescription-group">

                            <label>Dosage</label>

                            <input
                                type="text"
                                name="dosage"
                                placeholder="Example: 500mg"
                                required
                            >

                        </div>

                        <div class="prescription-group">

                            <label>Duration</label>

                            <input
                                type="text"
                                name="duration"
                                placeholder="Example: 5 days"
                                required
                            >

                        </div>

                    </div>

                    <div class="prescription-footer">

                        <a href="/" class="prescription-back">
                            ← Back to MediTrack
                        </a>

                        <button
                            type="submit"
                            class="prescription-btn">
                            Generate Prescription
                        </button>

                    </div>

                </form>

            </div>

        </div>

    </body>
    </html>
    """
@app.post("/prescription", response_class=HTMLResponse)
def save_prescription(
    patient_id: str = Form(...),
    doctor: str = Form(...),
    medicine: str = Form(...),
    dosage: str = Form(...),
    duration: str = Form(...)
):
    db = SessionLocal()

    patient = db.query(models.Patient).filter(
        models.Patient.patient_id == patient_id
    ).first()

    if not patient:
        db.close()

        return """
        <h1>Patient Not Found</h1>
        <p>Please enter a registered Patient ID.</p>
        <a href="/prescription">Try Again</a>
        <br><br>
        <a href="/">Back to MediTrack</a>
        """

    prescription = models.Prescription(
        patient_id=patient_id,
        doctor=doctor,
        medicine=medicine,
        dosage=dosage,
        duration=duration
    )

    db.add(prescription)
    db.commit()
    db.close()

    return """
<!DOCTYPE html>
<html>
<head>
    <title>Prescription Generated | MediTrack</title>

    <style>
        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            font-family: Arial, sans-serif;
            background: #06172D;
        }

        .success-page {
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 30px;
        }

        .success-card {
            width: 100%;
            max-width: 600px;
            background: #0D2947;
            border: 1px solid #315370;
            border-radius: 18px;
            padding: 45px;
            text-align: center;
            box-shadow: 0 20px 50px rgba(0,0,0,.35);
        }

        .success-icon {
            width: 75px;
            height: 75px;
            margin: 0 auto 22px;
            border-radius: 50%;
            background: #F4C542;
            color: #06172D;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 38px;
            font-weight: bold;
        }

        .success-card h1 {
            margin: 0 0 12px;
            color: #FFFFFF;
            font-size: 27px;
        }

        .success-card p {
            margin: 0;
            color: #AFC0D1;
            font-size: 13px;
            line-height: 1.6;
        }

        .success-actions {
            margin-top: 30px;
            display: flex;
            justify-content: center;
            gap: 12px;
        }

        .success-btn {
            padding: 13px 20px;
            border-radius: 9px;
            background: #F4C542;
            color: #06172D;
            text-decoration: none;
            font-size: 12px;
            font-weight: bold;
        }

        .success-btn:hover {
            background: #D9A91F;
        }

        .success-btn.secondary {
            background: #173A5A;
            color: #FFFFFF;
            border: 1px solid #315370;
        }

        .success-btn.secondary:hover {
            background: #204967;
        }

        .success-back {
            display: inline-block;
            margin-top: 25px;
            color: #AFC0D1;
            text-decoration: none;
            font-size: 12px;
        }

        .success-back:hover {
            color: #F4C542;
        }
    </style>
</head>

<body>

    <div class="success-page">

        <div class="success-card">

            <div class="success-icon">
                ✓
            </div>

            <h1>
                Prescription Generated Successfully
            </h1>

            <p>
                The prescription has been saved to the database.
            </p>

            <div class="success-actions">

                <a href="/prescription" class="success-btn secondary">
                    New Prescription
                </a>

                <a href="/prescriptions" class="success-btn">
                    View Prescriptions
                </a>

            </div>

            <a href="/" class="success-back">
                ← Back to MediTrack
            </a>

        </div>

    </div>

</body>
</html>
"""
    
    
@app.get("/prescriptions", response_class=HTMLResponse)
def view_prescriptions():
    db = SessionLocal()

    prescription_list = db.query(models.Prescription).all()

    db.close()

    if not prescription_list:
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Prescriptions | MediTrack</title>

            <style>
                * {
                    box-sizing: border-box;
                }

                body {
                    margin: 0;
                    font-family: Arial, sans-serif;
                    background: #06172D;
                    color: #FFFFFF;
                }

                .prescription-page {
                    min-height: 100vh;
                    padding: 50px 35px;
                }

                .prescription-container {
                    max-width: 1000px;
                    margin: auto;
                }

                .page-label {
                    color: #F4C542;
                    font-size: 10px;
                    font-weight: bold;
                    letter-spacing: 1.5px;
                }

                .page-header h1 {
                    margin: 8px 0;
                    font-size: 30px;
                }

                .page-header p {
                    color: #9FB1C7;
                    font-size: 13px;
                }

                .empty-card {
                    margin-top: 30px;
                    padding: 60px;
                    text-align: center;
                    background: #0D2947;
                    border: 1px solid #315370;
                    border-radius: 18px;
                }

                .empty-icon {
                    width: 65px;
                    height: 65px;
                    margin: auto auto 20px;
                    border-radius: 50%;
                    background: #F4C542;
                    color: #06172D;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 28px;
                    font-weight: bold;
                }

                .empty-card p {
                    color: #9FB1C7;
                }

                .back-link {
                    display: inline-block;
                    margin-top: 25px;
                    color: #F4C542;
                    text-decoration: none;
                    font-size: 12px;
                }
            </style>
        </head>

        <body>

            <div class="prescription-page">

                <div class="prescription-container">

                    <div class="page-header">
                        <span class="page-label">
                            PRESCRIPTION MANAGEMENT
                        </span>

                        <h1>Prescriptions</h1>

                        <p>
                            View all generated patient prescriptions.
                        </p>
                    </div>

                    <div class="empty-card">

                        <div class="empty-icon">✓</div>

                        <h2>No Prescriptions Found</h2>

                        <p>
                            No prescription records are available yet.
                        </p>

                        <a href="/prescription" class="back-link">
                            Generate Prescription
                        </a>

                    </div>

                    <a href="/" class="back-link">
                        ← Back to MediTrack
                    </a>

                </div>

            </div>

        </body>
        </html>
        """

    html = """
    <!DOCTYPE html>
    <html>
    <head>

        <title>Prescriptions | MediTrack</title>

        <style>

            * {
                box-sizing: border-box;
            }

            body {
                margin: 0;
                font-family: Arial, sans-serif;
                background: #06172D;
                color: #FFFFFF;
            }

            .prescription-page {
                min-height: 100vh;
                padding: 50px 35px;
            }

            .prescription-container {
                max-width: 1000px;
                margin: auto;
            }

            .page-header {
                margin-bottom: 30px;
            }

            .page-label {
                color: #F4C542;
                font-size: 10px;
                font-weight: bold;
                letter-spacing: 1.5px;
            }

            .page-header h1 {
                margin: 8px 0;
                font-size: 30px;
            }

            .page-header p {
                margin: 0;
                color: #9FB1C7;
                font-size: 13px;
            }

            .prescription-record {
                background: #0D2947;
                border: 1px solid #315370;
                border-radius: 16px;
                padding: 25px;
                margin-bottom: 18px;
                box-shadow: 0 10px 25px rgba(0,0,0,.20);
            }

            .record-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding-bottom: 18px;
                margin-bottom: 20px;
                border-bottom: 1px solid #315370;
            }

            .patient-id {
                color: #F4C542;
                font-size: 14px;
                font-weight: bold;
            }

            .doctor {
                color: #FFFFFF;
                font-size: 13px;
            }

            .prescription-grid {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 18px;
            }

            .prescription-item {
                background: #081D35;
                border: 1px solid #244766;
                border-radius: 10px;
                padding: 15px;
            }

            .prescription-item label {
                display: block;
                margin-bottom: 8px;
                color: #F4C542;
                font-size: 9px;
                font-weight: bold;
                letter-spacing: 1px;
            }

            .prescription-item p {
                margin: 0;
                color: #DDE7F1;
                font-size: 12px;
                line-height: 1.5;
            }

            .back-link {
                display: inline-block;
                margin-top: 10px;
                color: #AFC0D1;
                text-decoration: none;
                font-size: 12px;
            }

            .back-link:hover {
                color: #F4C542;
            }

            @media(max-width:700px) {

                .prescription-page {
                    padding: 25px 15px;
                }

                .prescription-grid {
                    grid-template-columns: 1fr;
                }

                .record-header {
                    flex-direction: column;
                    align-items: flex-start;
                    gap: 8px;
                }
            }

        </style>

    </head>

    <body>

        <div class="prescription-page">

            <div class="prescription-container">

                <div class="page-header">

                    <span class="page-label">
                        PRESCRIPTION MANAGEMENT
                    </span>

                    <h1>Prescriptions</h1>

                    <p>
                        View all generated patient prescriptions.
                    </p>

                </div>
    """

    for prescription in prescription_list:

        html += f"""
                <div class="prescription-record">

                    <div class="record-header">

                        <span class="patient-id">
                            Patient ID: {prescription.patient_id}
                        </span>

                        <span class="doctor">
                            Doctor: {prescription.doctor}
                        </span>

                    </div>

                    <div class="prescription-grid">

                        <div class="prescription-item">
                            <label>MEDICINE</label>
                            <p>{prescription.medicine}</p>
                        </div>

                        <div class="prescription-item">
                            <label>DOSAGE</label>
                            <p>{prescription.dosage}</p>
                        </div>

                        <div class="prescription-item">
                            <label>DURATION</label>
                            <p>{prescription.duration}</p>
                        </div>

                    </div>

                </div>
        """

    html += """
                <a href="/" class="back-link">
                    ← Back to MediTrack
                </a>

            </div>

        </div>

    </body>
    </html>
    """

    return html

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    db = SessionLocal()
    total_patients = db.query(models.Patient).count()
    total_appointments = db.query(models.Appointment).count()
    db.close()

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "request": request,
            "total_patients": total_patients,
            "total_appointments": total_appointments
        }
    )