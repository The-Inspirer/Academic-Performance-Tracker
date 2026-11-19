"""
Academic Performance Tracker - Flask Backend & REST API
--------------------------------------------------------
Contains:
- Flask server initialization.
- Web UI route (GET /).
- Academic structure metadata route (GET /api/academic-structure).
- Student lookup route for modal auto-fill (GET /api/student/<roll_number>).
- Filtered leaderboard & analytics route (GET /api/students).
- Assessment creation with strict validation (POST /api/students).
- Clean record deletion route (DELETE /api/students/<id>).
"""

from flask import Flask, render_template, request, jsonify
from logic import (
    get_students_and_stats,
    add_student,
    delete_student,
    get_student_by_roll,
    YEAR_SEMESTERS,
    SEMESTER_SUBJECTS
)

app = Flask(__name__)


# -------------------------------------------------------------
# 1. Frontend Page Route
# -------------------------------------------------------------
@app.route("/")
def index():
    """
    Renders the single-page application interface.
    """
    return render_template("index.html")


# -------------------------------------------------------------
# 2. Academic Structure Metadata (Strict Year -> Sem -> Subject)
# -------------------------------------------------------------
@app.route("/api/academic-structure", methods=["GET"])
def get_academic_structure():
    """
    Returns the strict academic hierarchy mapping:
      - Year -> Semesters
      - Semester -> 4 Subjects
    Allows the frontend to stay in 100% sync with backend validation.
    """
    return jsonify({
        "years": YEAR_SEMESTERS,
        "subjects": SEMESTER_SUBJECTS
    }), 200


# -------------------------------------------------------------
# 3. Student Metadata Lookup (Auto-fill & Name Lock)
# -------------------------------------------------------------
@app.route("/api/student/<string:roll_number>", methods=["GET"])
def get_student_info(roll_number):
    """
    GET /api/student/<roll_number>
    Checks if a student already exists with this roll number.
    Returns:
      {"found": True, "name": ..., "passing_year": ...}
      or {"found": False}
    """
    data = get_student_by_roll(roll_number)
    return jsonify(data), 200


# -------------------------------------------------------------
# 4. Retrieve Filtered Student Leaderboard & Analytics
# -------------------------------------------------------------
@app.route("/api/students", methods=["GET"])
def get_students():
    """
    GET /api/students?passing_year=all&year=all&semester=1&subject=all
    Accepts query parameters:
      - passing_year: 'all' or specific year ('2027', '2028', '2029', '2030')
      - year: 'all' or '1' to '4'
      - semester: 'all' or '1' to '8' (defaults to '1')
      - subject: 'all' or specific subject string
    Returns HTTP 200 with JSON payload containing:
      - students: sorted list of ranked records
      - stats: summary analytics dictionary
    """
    passing_year = request.args.get("passing_year", "all")
    year = request.args.get("year", "all")
    semester = request.args.get("semester", "1")
    subject = request.args.get("subject", "all")

    data = get_students_and_stats(
        year=year,
        semester=semester,
        subject=subject,
        passing_year=passing_year
    )
    return jsonify(data), 200


# -------------------------------------------------------------
# 5. Add a New Student Assessment Record
# -------------------------------------------------------------
@app.route("/api/students", methods=["POST"])
def create_student():
    """
    POST /api/students
    Accepts JSON body:
      {
        "roll_number": str,
        "name": str,
        "passing_year": int,
        "year": int,
        "semester": int,
        "subject": str,
        "mid_sem": num,
        "ct_viva": num,
        "end_sem": num
      }
    Validates limits, ensures 1 name per roll number, verifies admission vs passing year,
    and prevents duplicate (roll_number, semester, subject).
    Returns HTTP 201 with created record, or HTTP 400 on error.
    """
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Malformed request. Expected valid JSON."}), 400

    new_student, error = add_student(data)
    if error:
        return jsonify({"error": error}), 400

    return jsonify(new_student), 201


# -------------------------------------------------------------
# 6. Delete an Assessment Record by Unique ID
# -------------------------------------------------------------
@app.route("/api/students/<int:student_id>", methods=["DELETE"])
def remove_student(student_id):
    """
    DELETE /api/students/<student_id>
    Removes a specific record by its unique database ID.
    Returns HTTP 200 on success, or HTTP 404 if not found.
    """
    success = delete_student(student_id)
    if success:
        return jsonify({"message": f"Record #{student_id} successfully deleted."}), 200
    else:
        return jsonify({"error": f"Record with ID {student_id} not found."}), 404


# -------------------------------------------------------------
# Run Server
# -------------------------------------------------------------
if __name__ == "__main__":
    print("Academic Performance Tracker running on http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
