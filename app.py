from flask import Flask, render_template, request, send_file, session, redirect, url_for
import os
import sqlite3
import re
from datetime import datetime
import PyPDF2
import docx
from werkzeug.security import generate_password_hash, check_password_hash
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
import csv
from io import StringIO
from flask import Response


app = Flask(__name__)
app.secret_key = "supersecretkey"

UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


#  ROLE SKILLS
ROLE_SKILLS = {
    "Python Developer": ["python","flask","django","sql","api","oop","pandas","numpy"],
    "Web Developer": ["html","css","javascript","react","bootstrap","node"],
    "Data Analyst": ["python","sql","excel","pandas","numpy","power bi","machine learning"],
    "Frontend Developer": ["html","css","javascript","react","angular","vue","bootstrap","responsive"],
    "Backend Developer": ["python","java","node","sql","mongodb","api","authentication"],
    "Full Stack Developer": ["html","css","javascript","react","node","python","sql","mongodb"],
    "Machine Learning Engineer": ["python","machine learning","tensorflow","keras","pandas","numpy","scikit","deep learning"],
    "Cyber Security Analyst": ["network security","penetration testing","ethical hacking","firewall","encryption","vulnerability"],
    "DevOps Engineer": ["docker","kubernetes","aws","azure","ci/cd","linux","jenkins"]
}


#  INIT DATABASE (SAFE UPGRADE)
def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT,
            score INTEGER,
            matched TEXT,
            missing TEXT,
            ats_score INTEGER,
            grade TEXT,
            date TEXT
        )
    """)

    # Safe upgrade if grade column missing
    try:
        cursor.execute("ALTER TABLE analysis ADD COLUMN grade TEXT")
    except:
        pass

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)

    cursor.execute("SELECT * FROM users WHERE username=?", ("admin",))
    if not cursor.fetchone():
        hashed = generate_password_hash("admin123")
        cursor.execute("INSERT INTO users (username,password) VALUES (?,?)",("admin",hashed))

    conn.commit()
    conn.close()


# SAVE DATA
def save_to_db(role, score, matched, missing, ats_score, grade):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO analysis (role, score, matched, missing, ats_score, grade, date)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """,(
        role,
        score,
        ", ".join(matched),
        ", ".join(missing),
        ats_score,
        grade,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()


#  FILE EXTRACTORS
def extract_pdf(filepath):
    text=""
    with open(filepath,"rb") as file:
        reader=PyPDF2.PdfReader(file)
        for page in reader.pages:
            if page.extract_text():
                text+=page.extract_text()
    return text.lower()


def extract_docx(filepath):
    doc=docx.Document(filepath)
    text=""
    for para in doc.paragraphs:
        text+=para.text
    return text.lower()


# SKILL SCORE
def calculate_score(resume_text, role):
    required_skills = ROLE_SKILLS.get(role, [])
    matched=[]

    for skill in required_skills:
        if skill.lower() in resume_text:
            matched.append(skill)

    score=int((len(matched)/len(required_skills))*100) if required_skills else 0
    missing=list(set(required_skills)-set(matched))

    return score, matched, missing


#  AUTO ROLE DETECTION
def detect_best_role(resume_text):
    best_role=None
    best_score=0

    for role in ROLE_SKILLS:
        score,_ ,_ = calculate_score(resume_text,role)
        if score>best_score:
            best_score=score
            best_role=role

    return best_role,best_score


#  GRADE SYSTEM
def get_grade(score):
    if score >= 85:
        return "A+"
    elif score >= 70:
        return "A"
    elif score >= 50:
        return "B"
    else:
        return "Needs Improvement"


#  ADVANCED ATS CHECK
def ats_check(resume_text):
    score=0
    feedback=[]

    if re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", resume_text):
        score+=15
    else:
        feedback.append("Add professional email address.")

    if re.search(r"\b\d{10}\b", resume_text):
        score+=15
    else:
        feedback.append("Add phone number.")

    sections = {
        "education":15,
        "experience":15,
        "project":15,
        "skills":15
    }

    for sec,pts in sections.items():
        if sec in resume_text:
            score+=pts
        else:
            feedback.append(f"Add {sec} section.")

    if len(resume_text.split())>300:
        score+=10
    else:
        feedback.append("Resume too short. Add more content.")

    return score,feedback


#  SMART SUGGESTIONS
def generate_suggestions(missing):
    suggestions=[]
    for skill in missing:
        suggestions.append(f"Add real-world project using {skill}.")
        suggestions.append(f"Mention hands-on experience with {skill}.")
    if not suggestions:
        suggestions.append("Excellent resume! Add certifications for more impact.")
    return suggestions


# 📄 PDF GENERATE (WITH GRADE)
def generate_pdf(role,score,matched,missing,ats_score,grade):
    file_path="analysis_report.pdf"
    doc=SimpleDocTemplate(file_path,pagesize=letter)
    elements=[]
    styles=getSampleStyleSheet()

    elements.append(Paragraph("<b>AI Resume Report</b>",styles['Title']))
    elements.append(Spacer(1,0.3*inch))
    elements.append(Paragraph(f"Role: {role}",styles['Normal']))
    elements.append(Paragraph(f"Skill Score: {score}%",styles['Normal']))
    elements.append(Paragraph(f"ATS Score: {ats_score}%",styles['Normal']))
    elements.append(Paragraph(f"Grade: {grade}",styles['Normal']))
    elements.append(Spacer(1,0.3*inch))

    elements.append(Paragraph("<b>Matched Skills:</b>",styles['Heading3']))
    elements.append(ListFlowable([ListItem(Paragraph(s,styles['Normal'])) for s in matched]))

    elements.append(Spacer(1,0.2*inch))
    elements.append(Paragraph("<b>Missing Skills:</b>",styles['Heading3']))
    elements.append(ListFlowable([ListItem(Paragraph(s,styles['Normal'])) for s in missing]))

    doc.build(elements)
    return file_path


# MAIN ROUTE
@app.route("/",methods=["GET","POST"])
def index():
    if request.method=="POST":
        file=request.files.get("resume")
        role=request.form.get("role")

        if file:
            filepath=os.path.join(app.config["UPLOAD_FOLDER"],file.filename)
            file.save(filepath)

            if file.filename.endswith(".pdf"):
                resume_text=extract_pdf(filepath)
            elif file.filename.endswith(".docx"):
                resume_text=extract_docx(filepath)
            else:
                resume_text=open(filepath,"r",encoding="utf-8",errors="ignore").read().lower()

            detected_role,detected_score=detect_best_role(resume_text)

            if not role:
                role=detected_role

            score,matched,missing=calculate_score(resume_text,role)
            ats_score,ats_feedback=ats_check(resume_text)
            grade=get_grade(score)
            suggestions=generate_suggestions(missing)

            save_to_db(role,score,matched,missing,ats_score,grade)
            os.remove(filepath)

            return render_template("result.html",
                score=score,
                matched=matched,
                missing=missing,
                role=role,
                suggestions=suggestions,
                ats_score=ats_score,
                ats_feedback=ats_feedback,
                detected_role=detected_role,
                detected_score=detected_score,
                grade=grade
            )

    return render_template("index.html")


# 📥 DOWNLOAD
@app.route("/download")
def download():
    role=request.args.get("role")
    score=request.args.get("score")
    matched=request.args.getlist("matched")
    missing=request.args.getlist("missing")
    ats_score=request.args.get("ats_score")
    grade=request.args.get("grade")

    file_path=generate_pdf(role,score,matched,missing,ats_score,grade)
    return send_file(file_path,as_attachment=True)


# 🔐 LOGIN
@app.route("/login",methods=["GET","POST"])
def login():
    if request.method=="POST":
        username=request.form.get("username")
        password=request.form.get("password")

        conn=sqlite3.connect("database.db")
        cursor=conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=?",(username,))
        user=cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[2],password):
            session["admin"]=True
            return redirect(url_for("admin_panel"))
        else:
            return render_template("login.html",error="Invalid Credentials")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("admin",None)
    return redirect("/")


# 🗄 ADMIN PANEL
@app.route("/admin")
def admin_panel():
    if not session.get("admin"):
        return redirect(url_for("login"))

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # All records
    cursor.execute("SELECT * FROM analysis ORDER BY id DESC")
    records = cursor.fetchall()

    # Total analysis
    cursor.execute("SELECT COUNT(*) FROM analysis")
    total = cursor.fetchone()[0]

    # Average skill score
    cursor.execute("SELECT AVG(score) FROM analysis")
    avg_score = cursor.fetchone()[0] or 0

    # Average ATS score
    cursor.execute("SELECT AVG(ats_score) FROM analysis")
    avg_ats = cursor.fetchone()[0] or 0

    # Role wise count (FOR CHART)
    cursor.execute("SELECT role, COUNT(*) FROM analysis GROUP BY role")
    role_data = cursor.fetchall()

    conn.close()

    # Separate roles and counts
    roles = [row[0] for row in role_data] if role_data else []
    counts = [row[1] for row in role_data] if role_data else []

    return render_template(
        "admin.html",
        records=records,
        total=total,
        avg_score=round(avg_score, 2),
        avg_ats=round(avg_ats, 2),
        roles=roles,
        counts=counts
    )

# EXPORT CSV (Admin Feature)
@app.route("/export_csv")
def export_csv():
    if not session.get("admin"):
        return redirect(url_for("login"))

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, role, score, matched, missing, ats_score, grade, date FROM analysis")
    records = cursor.fetchall()
    conn.close()

    # Create CSV in memory
    output = StringIO()
    writer = csv.writer(output)

    # Header row
    writer.writerow(["ID", "Role", "Score", "Matched Skills", "Missing Skills", "ATS Score", "Grade", "Date"])

    # Data rows
    for row in records:
        writer.writerow(row)

    output.seek(0)

    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=resume_analysis_data.csv"}
    )


# Render/Gunicorn startup
init_db()

if __name__=="__main__":
    app.run(debug=True)