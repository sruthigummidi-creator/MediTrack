from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
import os
from jose import jwt
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from database import engine, Base
from database import SessionLocal
import models
from datetime import datetime

SECRET_KEY = "meditrack-secret-key-2026"
ALGORITHM = "HS256"
app = FastAPI()
def verify_token(token: str):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        return payload
    except Exception:
        return None
def create_audit_log(db, username, action, details):
    log = models.AuditLog(
        username=username,
        action=action,
        details=details,
        timestamp=datetime.now()
    )

    db.add(log)
    db.commit()
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET", "meditrack-milestone2-secret")
)

templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="templates"), name="static")

Base.metadata.create_all(bind=engine)
def create_default_users():
    db = SessionLocal()

    if not db.query(models.User).filter(
        models.User.username == "doctor"
    ).first():
        db.add(models.User(
            username="doctor",
            password="doctor123",
            role="doctor"
        ))

    if not db.query(models.User).filter(
        models.User.username == "patient"
    ).first():
        db.add(models.User(
            username="patient",
            password="patient123",
            role="patient"
        ))

    db.commit()
    db.close()


create_default_users()

@app.get("/login", response_class=HTMLResponse)
def login_page():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>MediTrack Login</title>
        <style>
    * {
        box-sizing: border-box;
    }

    body {
        margin: 0;
        min-height: 100vh;
        font-family: Arial, sans-serif;
        background: #06172D;
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .login-container {
        width: 100%;
        max-width: 430px;
        background: #102F50;
        border: 1px solid #315878;
        border-radius: 18px;
        padding: 40px;
        box-shadow: 0 15px 40px rgba(0,0,0,0.3);
    }

    .label {
        color: #F4C542;
        font-size: 12px;
        font-weight: bold;
        letter-spacing: 2px;
        margin-bottom: 10px;
    }

    h1 {
        margin: 0 0 8px;
        font-size: 32px;
    }

    .subtitle {
        color: #AFC1D2;
        margin-bottom: 30px;
        font-size: 14px;
    }

    .form-group {
        margin-bottom: 20px;
    }

    label {
        display: block;
        margin-bottom: 8px;
        color: #DDE7F1;
        font-size: 14px;
        font-weight: bold;
    }

    input,
    select {
        width: 100%;
        padding: 13px;
        border-radius: 8px;
        border: 1px solid #315878;
        background: #081D35;
        color: white;
        font-size: 14px;
        outline: none;
    }

    input:focus,
    select:focus {
        border-color: #F4C542;
    }

    select option {
        background: #081D35;
        color: white;
    }

    button {
        width: 100%;
        padding: 14px;
        margin-top: 10px;
        border: none;
        border-radius: 9px;
        background: #F4C542;
        color: #06172D;
        font-size: 15px;
        font-weight: bold;
        cursor: pointer;
    }

    button:hover {
        opacity: 0.9;
        transform: translateY(-1px);
    }

    .logo {
        width: 55px;
        height: 55px;
        border-radius: 14px;
        background: #F4C542;
        color: #06172D;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 28px;
        font-weight: bold;
        margin-bottom: 25px;
    }
</style>
    </head>

    <body>
<body>

    <div class="login-container">

        <div class="logo">+</div>

        <div class="label">MEDITRACK</div>

        <h1>Welcome Back</h1>

        <p class="subtitle">
            Login to access your healthcare portal.
        </p>

        <form action="/login" method="post">

            <div class="form-group">
                <label>Username</label>
                <input type="text" name="username" required>
            </div>

            <div class="form-group">
                <label>Password</label>
                <input type="password" name="password" required>
            </div>

            <div class="form-group">
                <label>Role</label>
                <select name="role" required>
                    <option value="">Select Role</option>
                    <option value="patient">Patient</option>
                    <option value="doctor">Doctor</option>
                </select>
            </div>

            <button type="submit">Login</button>

        </form>

    </div>

</body>
    </body>
    </html>
    """
@app.post("/login", response_class=HTMLResponse)
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    role: str = Form(...)
):
    db = SessionLocal()

    user = db.query(models.User).filter(
        models.User.username == username,
        models.User.password == password,
        models.User.role == role
    ).first()

    db.close()

    if not user:
        audit_db = SessionLocal()

        create_audit_log(
            audit_db,
            username,
            "FAILED_LOGIN",
            f"Failed login attempt with role {role}"
        )

        audit_db.close()
        return HTMLResponse(
           
        """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Invalid Login - MediTrack</title>

            <style>
                * {
                    box-sizing: border-box;
                }

                body {
                    margin: 0;
                    min-height: 100vh;
                    font-family: Arial, sans-serif;
                    background: #06172D;
                    color: white;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }

                .error-card {
                    width: 100%;
                    max-width: 430px;
                    background: #102F50;
                    border: 1px solid #315878;
                    border-radius: 18px;
                    padding: 40px;
                    text-align: center;
                    box-shadow: 0 15px 40px rgba(0,0,0,0.3);
                }

                .error-icon {
                    width: 65px;
                    height: 65px;
                    margin: 0 auto 20px;
                    border-radius: 50%;
                    background: #F4C542;
                    color: #06172D;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 30px;
                    font-weight: bold;
                }

                .label {
                    color: #F4C542;
                    font-size: 12px;
                    font-weight: bold;
                    letter-spacing: 2px;
                }

                h2 {
                    font-size: 28px;
                    margin: 12px 0;
                }

                p {
                    color: #AFC1D2;
                    font-size: 14px;
                    line-height: 1.6;
                }

                .try-again {
                    display: inline-block;
                    margin-top: 20px;
                    padding: 13px 25px;
                    background: #F4C542;
                    color: #06172D;
                    border-radius: 9px;
                    text-decoration: none;
                    font-weight: bold;
                }

                .try-again:hover {
                    opacity: 0.9;
                }
            </style>
        </head>

        <body>

            <div class="error-card">

                <div class="error-icon">!</div>

                <div class="label">MEDITRACK LOGIN</div>

                <h2>Invalid Login</h2>

                <p>
                    Username, password, or role is incorrect.
                    Please check your login details and try again.
                </p>

                <a href="/login" class="try-again">
                    Try Again
                </a>

            </div>

        </body>
        </html>
        """
    )
    request.session["username"] = user.username
    request.session["role"] = user.role
    request.session["patient_id"] = user.patient_id
    audit_db = SessionLocal()

    create_audit_log(
        audit_db,
        user.username,
        "LOGIN",
        f"Successful login as {user.role}"
    )

    audit_db.close()
    token_data = {
    "username": user.username,
    "role": user.role,
    "patient_id": user.patient_id
    }

    token = jwt.encode(
        token_data,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    request.session["access_token"] = token
    

    if user.role == "patient":
        return RedirectResponse("/patient-dashboard", status_code=303)

    if user.role == "doctor":
        return RedirectResponse("/doctor-dashboard", status_code=303)

    return RedirectResponse("/dashboard", status_code=303)
@app.get("/patient-dashboard", response_class=HTMLResponse)
def patient_dashboard(request: Request):
    token = request.session.get("access_token")
    payload = verify_token(token) if token else None

    if not payload or payload.get("role") != "patient":
        return RedirectResponse("/login", status_code=303)

    if request.session.get("role") != "patient":
        return RedirectResponse("/login", status_code=303)

    db = SessionLocal()

    patient_id = request.session.get("patient_id")

    notifications = db.query(models.Notification).filter(
        models.Notification.patient_id == patient_id
    ).all()

    db.close()

    notification_html = ""

    for notification in notifications:
        notification_html += f"""
        <div class="notification-item">
            <div class="notification-icon">🔔</div>

            <div>
                <h3>{notification.notification_type}</h3>
                <p>{notification.message}</p>
            </div>
        </div>
        """

    if not notification_html:
        notification_html = """
        <div class="notification-item">
            <div class="notification-icon">✓</div>

            <div>
                <h3>No Notifications</h3>
                <p>You don't have any notifications yet.</p>
            </div>
        </div>
        """

    return f"""
    <!DOCTYPE html>
    <html>

    <head>
        <title>Patient Dashboard - MediTrack</title>

        <style>

            * {{
                box-sizing: border-box;
            }}

            body {{
                margin: 0;
                min-height: 100vh;
                font-family: Arial, sans-serif;
                background: #06172D;
                color: white;
            }}

            .container {{
                max-width: 1100px;
                margin: auto;
                padding: 50px 30px;
            }}

            .header {{
                background: #12385D;
                padding: 40px;
                border-radius: 18px;
                margin-bottom: 30px;
                border: 1px solid #315878;
            }}

            .label {{
                color: #F4C542;
                font-size: 13px;
                font-weight: bold;
                letter-spacing: 2px;
            }}

            .header h1 {{
                font-size: 38px;
                margin: 12px 0;
            }}

            .header p {{
                color: #C4D2DF;
                font-size: 16px;
            }}

            .section-title {{
                margin: 30px 0 18px;
                color: #F4C542;
                font-size: 13px;
                font-weight: bold;
                letter-spacing: 2px;
            }}

            .notification-card {{
                background: #102F50;
                border: 1px solid #315878;
                border-radius: 16px;
                padding: 20px;
                margin-bottom: 30px;
            }}

            .notification-item {{
                display: flex;
                align-items: center;
                gap: 15px;
                padding: 15px;
                background: #081D35;
                border-radius: 10px;
                margin-bottom: 10px;
            }}

            .notification-icon {{
                width: 45px;
                height: 45px;
                border-radius: 10px;
                background: #29475D;
                color: #F4C542;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 20px;
                flex-shrink: 0;
            }}

            .notification-item h3 {{
                margin: 0 0 5px;
                color: #F4C542;
                font-size: 14px;
            }}

            .notification-item p {{
                margin: 0;
                color: #C4D2DF;
                font-size: 13px;
            }}

            .cards {{
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 20px;
            }}

            .card {{
                background: #102F50;
                border: 1px solid #315878;
                border-radius: 16px;
                padding: 28px;
                text-decoration: none;
                color: white;
                transition: 0.2s;
            }}

            .card:hover {{
                transform: translateY(-5px);
                border-color: #F4C542;
            }}

            .icon {{
                width: 50px;
                height: 50px;
                background: #29475D;
                border-radius: 12px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: #F4C542;
                font-size: 22px;
                margin-bottom: 18px;
            }}

            .card h2 {{
                font-size: 19px;
                margin: 0 0 10px;
            }}

            .card p {{
                color: #AFC1D2;
                font-size: 14px;
                line-height: 1.5;
            }}

            .logout {{
                display: inline-block;
                margin-top: 30px;
                padding: 13px 25px;
                background: #F4C542;
                color: #06172D;
                border-radius: 9px;
                text-decoration: none;
                font-weight: bold;
            }}

            .logout:hover {{
                background: #FFD45C;
            }}

            @media (max-width: 800px) {{
                .cards {{
                    grid-template-columns: 1fr;
                }}
            }}

        </style>
    </head>

    <body>

        <div class="container">

            <div class="header">

                <div class="label">PATIENT PORTAL</div>

                <h1>Welcome to MediTrack</h1>

                <p>
                    Manage your appointments and medical records from one place.
                </p>

            </div>

            <div class="section-title">
                NOTIFICATIONS
            </div>

            <div class="notification-card">

                {notification_html}

            </div>

            <div class="section-title">
                PATIENT ACCESS
            </div>

            <div class="cards">

                <a href="/appointments" class="card">
                    <div class="icon">▣</div>
                    <h2>My Appointments</h2>
                    <p>
                        View your scheduled appointments.
                    </p>
                </a>

                <a href="/consultations" class="card">
                    <div class="icon">✚</div>
                    <h2>Consultation History</h2>
                    <p>
                        View your previous consultations.
                    </p>
                </a>

                <a href="/prescriptions" class="card">
                    <div class="icon">▤</div>
                    <h2>My Prescriptions</h2>
                    <p>
                        View your prescribed medicines.
                    </p>
                </a>

            </div>

            <a href="/logout" class="logout">
                Logout
            </a>

        </div>

    </body>
    </html>
    """
@app.get("/doctor-dashboard", response_class=HTMLResponse)
def doctor_dashboard(request: Request):
    token = request.session.get("access_token")
    payload = verify_token(token) if token else None

    if not payload or payload.get("role") != "doctor":
        return RedirectResponse("/login", status_code=303)
    if request.session.get("role") != "doctor":
        return RedirectResponse("/login", status_code=303)

    return """
    <!DOCTYPE html>
    <html>

    <head>
        <title>Doctor Dashboard - MediTrack</title>

        <style>
            * {
                box-sizing: border-box;
            }

            body {
                margin: 0;
                min-height: 100vh;
                font-family: Arial, sans-serif;
                background: #06172D;
                color: white;
            }

            .container {
                max-width: 1100px;
                margin: auto;
                padding: 50px 30px;
            }

            .header {
                background: #12385D;
                padding: 40px;
                border-radius: 18px;
                margin-bottom: 30px;
                border: 1px solid #315878;
            }

            .label {
                color: #F4C542;
                font-size: 13px;
                font-weight: bold;
                letter-spacing: 2px;
            }

            .header h1 {
                font-size: 38px;
                margin: 12px 0;
            }

            .header p {
                color: #C4D2DF;
                font-size: 16px;
            }

            .section-title {
                margin: 30px 0 18px;
                color: #F4C542;
                font-size: 13px;
                font-weight: bold;
                letter-spacing: 2px;
            }

            .cards {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 20px;
            }

            .card {
                background: #102F50;
                border: 1px solid #315878;
                border-radius: 16px;
                padding: 28px;
                text-decoration: none;
                color: white;
                transition: 0.2s;
            }

            .card:hover {
                transform: translateY(-5px);
                border-color: #F4C542;
            }

            .icon {
                width: 50px;
                height: 50px;
                background: #29475D;
                border-radius: 12px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: #F4C542;
                font-size: 22px;
                margin-bottom: 18px;
            }

            .card h2 {
                font-size: 19px;
                margin: 0 0 10px;
            }

            .card p {
                color: #AFC1D2;
                font-size: 14px;
                line-height: 1.5;
            }

            .logout {
                display: inline-block;
                margin-top: 30px;
                padding: 13px 25px;
                background: #F4C542;
                color: #06172D;
                border-radius: 9px;
                text-decoration: none;
                font-weight: bold;
            }

            @media (max-width: 800px) {
                .cards {
                    grid-template-columns: 1fr;
                }
            }
        </style>
    </head>

    <body>

        <div class="container">

            <div class="header">

                <div class="label">DOCTOR PORTAL</div>

                <h1>Welcome to MediTrack</h1>

                <p>
                    Manage patients, appointments and medical records.
                </p>

            </div>

            <div class="section-title">DOCTOR ACCESS</div>

            <div class="cards">

                <a href="/patients" class="card">
                    <div class="icon">♟</div>
                    <h2>View Patients</h2>
                    <p>
                        View registered patient information.
                    </p>
                </a>

                <a href="/appointments" class="card">
                    <div class="icon">▣</div>
                    <h2>Appointments</h2>
                    <p>
                        View scheduled patient appointments.
                    </p>
                </a>

                <a href="/consultation" class="card">
                    <div class="icon">✚</div>
                    <h2>Start Consultation</h2>
                    <p>
                        Record symptoms, diagnosis and treatment.
                    </p>
                </a>

                <a href="/consultations" class="card">
                <div class="icon">▤</div>
                <h2>Consultation History</h2>
                <p>
                View previous consultation records.
                </p>
                </a>

                <a href="/prescription" class="card">
                    <div class="icon">▥</div>
                    <h2>Generate Prescription</h2>
                    <p>
                        Create prescriptions for patients.
                    </p>
                </a>

                <a href="/prescriptions" class="card">
                    <div class="icon">▤</div>
                    <h2>View Prescriptions</h2>
                    <p>
                        View generated prescriptions.
                    </p>
                </a>

            </div>
            <a href="/logout" class="logout">Logout</a>


        </div>

    </body>

    </html>
    """
@app.get("/api/patients")
def get_patients(request: Request):

    token = request.session.get("access_token")
    payload = verify_token(token) if token else None

    if not payload or payload.get("role") != "doctor":
        return {"error": "Unauthorized"}

    db = SessionLocal()

    patients = db.query(models.User).filter(
        models.User.role == "patient"
    ).all()

    result = []

    for patient in patients:
        result.append({
            "id": patient.id,
            "username": patient.username,
            "patient_id": patient.patient_id
        })

    db.close()

    return result
@app.post("/api/appointments")
def create_appointment(
    request: Request,
    patient_id: str = Form(...),
    doctor: str = Form(...),
    date: str = Form(...),
    time: str = Form(...)
):
    token = request.session.get("access_token")
    payload = verify_token(token) if token else None

    if not payload or payload.get("role") != "patient":
        return {"error": "Unauthorized"}

    db = SessionLocal()
    existing = db.query(models.Appointment).filter(
        models.Appointment.doctor == doctor,
        models.Appointment.date == date,
        models.Appointment.time == time
    ).first()

    if existing:
        db.close()
        return {
            "error": "Slot already booked",
            "message": "This doctor already has an appointment at the selected date and time."
        }

    appointment = models.Appointment(
        patient_id=patient_id,
        doctor=doctor,
        date=date,
        time=time
    )

    db.add(appointment)
    db.commit()

    notification = models.Notification(
        patient_id=patient_id,
        message=f"Your appointment with {doctor} is scheduled on {date} at {time}.",
        notification_type="appointment"
    )

    db.add(notification)
    db.commit()
    create_audit_log(
        db,
        payload.get("username"),
        "CREATE_APPOINTMENT",
        f"Appointment with {doctor} on {date} at {time}"
    )

    db.close()

    return {
        "message": "Appointment created successfully",
        "patient_id": patient_id,
        "doctor": doctor,
        "date": date,
        "time": time
    }
@app.get("/api/appointments")
def get_appointments(request: Request):

    token = request.session.get("access_token")
    payload = verify_token(token) if token else None

    if not payload:
        return {"error": "Unauthorized"}

    db = SessionLocal()

    appointments = db.query(models.Appointment).all()

    result = []

    for appointment in appointments:
        result.append({
            "id": appointment.id,
            "patient_id": appointment.patient_id,
            "doctor": appointment.doctor,
            "date": appointment.date,
            "time": appointment.time
        })

    db.close()

    return result
@app.put("/api/appointments/{appointment_id}")
def update_appointment(
    appointment_id: int,
    request: Request,
    doctor: str = Form(...),
    date: str = Form(...),
    time: str = Form(...)
):
    token = request.session.get("access_token")
    payload = verify_token(token) if token else None

    if not payload or payload.get("role") != "patient":
        return {"error": "Unauthorized"}

    db = SessionLocal()

    appointment = db.query(models.Appointment).filter(
        models.Appointment.id == appointment_id
    ).first()

    if not appointment:
        db.close()
        return {"error": "Appointment not found"}

    existing = db.query(models.Appointment).filter(
        models.Appointment.id != appointment_id,
        models.Appointment.doctor == doctor,
        models.Appointment.date == date,
        models.Appointment.time == time
    ).first()

    if existing:
        db.close()
        return {
            "error": "Slot already booked",
            "message": "This doctor already has an appointment at the selected date and time."
        }

    appointment.doctor = doctor
    appointment.date = date
    appointment.time = time

    db.commit()
    create_audit_log(
        db,
        payload.get("username"),
        "UPDATE_APPOINTMENT",
        f"Appointment {appointment_id} updated to {doctor} on {date} at {time}"
    )
    db.close()

    return {
        "message": "Appointment updated successfully",
        "appointment_id": appointment_id,
        "doctor": doctor,
        "date": date,
        "time": time
    }
@app.delete("/api/appointments/{appointment_id}")
def delete_appointment(
    appointment_id: int,
    request: Request
):
    token = request.session.get("access_token")
    payload = verify_token(token) if token else None

    if not payload or payload.get("role") != "patient":
        return {"error": "Unauthorized"}

    db = SessionLocal()

    appointment = db.query(models.Appointment).filter(
        models.Appointment.id == appointment_id
    ).first()

    if not appointment:
        db.close()
        return {"error": "Appointment not found"}

    db.delete(appointment)
    db.commit()
    create_audit_log(
        db,
        payload.get("username"),
        "DELETE_APPOINTMENT",
        f"Appointment {appointment_id} deleted"
    )
    db.close()

    return {
        "message": "Appointment deleted successfully",
        "appointment_id": appointment_id
    }
@app.get("/api/audit-logs")
def get_audit_logs(request: Request):

    token = request.session.get("access_token")
    payload = verify_token(token) if token else None

    if not payload or payload.get("role") != "doctor":
        return {"error": "Unauthorized"}

    db = SessionLocal()

    logs = db.query(models.AuditLog).all()

    result = []

    for log in logs:
        result.append({
            "id": log.id,
            "username": log.username,
            "action": log.action,
            "details": log.details
        })

    db.close()

    return result
@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=303)
@app.get("/")
def home(request: Request):
    if "username" not in request.session:
        return RedirectResponse("/login", status_code=303)

    return RedirectResponse("/dashboard", status_code=303)

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

    notification = models.Notification(
    patient_id=patient_id,

    message=f"Your appointment with {doctor} is scheduled on {date} at {time}.",

    notification_type="appointment"
    )

    db.add(notification)
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
def view_consultations(request: Request):
    db = SessionLocal()

    if request.session.get("role") == "patient":
        patient_id = request.session.get("patient_id")

        consultation_list = db.query(models.Consultation).filter(
            models.Consultation.patient_id == patient_id
        ).all()

    elif request.session.get("role") == "doctor":
        consultation_list = db.query(models.Consultation).all()

    else:
        db.close()
        return RedirectResponse("/login", status_code=303)

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
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    if "username" not in request.session:
        return RedirectResponse("/login", status_code=303)

    return RedirectResponse("/dashboard", status_code=303)

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