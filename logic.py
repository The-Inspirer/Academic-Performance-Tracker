"""
Academic Performance Tracker - Business Logic & Data Store
-----------------------------------------------------------
Features:
- Strict Year -> Semester -> Subject academic hierarchy.
- 32 realistic B.Tech subjects (4 subjects per semester for 8 semesters).
- 60 unique Indian students across 4 passing batches (2027, 2028, 2029, 2030).
  * Degree is 4 years: Passing Year = Admission Year + 4.
  * Admission 2023 (2023UCS1001-15) -> Passing Year 2027 (Year 4 Seniors)
  * Admission 2024 (2024UCS1001-15) -> Passing Year 2028 (Year 3 Pre-Finals)
  * Admission 2025 (2025UCS1001-15) -> Passing Year 2029 (Year 2 Sophomores)
  * Admission 2026 (2026UCS1001-15) -> Passing Year 2030 (Year 1 Freshmen)
- Seeded generator (random.seed(42)) producing a rich, deterministic evaluation dataset.
- Primary identification by Roll Number.
- Enforce One Name & Passing Year per Roll Number: prevents assigning different names to an existing roll number.
- Admission prefix validation: passing_year must equal admission_year + 4.
- Duplicate prevention for (roll_number, semester, subject).
- Multi-parameter filtering (passing_year, year, semester, subject).
- Comprehensive analytics: unique student counts, averages, highest marks, topper info.
"""

import random

# -------------------------------------------------------------
# 1. Academic Hierarchy: 32 Subjects (4 per semester)
# -------------------------------------------------------------
SEMESTER_SUBJECTS = {
    1: [
        "Problem Solving using Python",
        "Engineering Mathematics I",
        "Physics for Engineers",
        "Basic Electrical Engineering"
    ],
    2: [
        "Programming in C",
        "Engineering Mathematics II",
        "Engineering Chemistry",
        "Basic Electronics"
    ],
    3: [
        "Data Structures and Algorithms",
        "Discrete Mathematics",
        "Digital Logic and Design",
        "Object Oriented Programming in Java"
    ],
    4: [
        "Operating Systems",
        "Computer Organization & Architecture",
        "Database Management Systems",
        "Theory of Computation"
    ],
    5: [
        "Design and Analysis of Algorithms",
        "Computer Networks",
        "Software Engineering",
        "Microprocessors & Microcontrollers"
    ],
    6: [
        "Artificial Intelligence",
        "Web Technologies & Frameworks",
        "Compiler Design",
        "Information Security"
    ],
    7: [
        "Machine Learning",
        "Cloud Computing & DevOps",
        "Distributed Systems",
        "Internet of Things (IoT)"
    ],
    8: [
        "Deep Learning & NLP",
        "Big Data Analytics",
        "Cyber Security & Forensics",
        "Blockchain Technology"
    ]
}

YEAR_SEMESTERS = {
    1: [1, 2],
    2: [3, 4],
    3: [5, 6],
    4: [7, 8]
}

# -------------------------------------------------------------
# 2. 60 Realistic Indian Students (15 per passing batch)
# B.Tech is 4 years: Passing Year = Admission Year + 4
# -------------------------------------------------------------
STUDENT_ROSTER_60 = [
    # Batch: Admission 2023 -> Passing Year 2027 (Year 4: Graduating Senior Batch) - 15 Students
    {"roll_number": "2023UCS1001", "name": "Diya Patel", "passing_year": 2027, "active_year": 4},
    {"roll_number": "2023UCS1002", "name": "Aarav Sharma", "passing_year": 2027, "active_year": 4},
    {"roll_number": "2023UCS1003", "name": "Rohan Verma", "passing_year": 2027, "active_year": 4},
    {"roll_number": "2023UCS1004", "name": "Ananya Iyer", "passing_year": 2027, "active_year": 4},
    {"roll_number": "2023UCS1005", "name": "Kabir Mehta", "passing_year": 2027, "active_year": 4},
    {"roll_number": "2023UCS1006", "name": "Sneha Kulkarni", "passing_year": 2027, "active_year": 4},
    {"roll_number": "2023UCS1007", "name": "Vikram Singh", "passing_year": 2027, "active_year": 4},
    {"roll_number": "2023UCS1008", "name": "Riya Sen", "passing_year": 2027, "active_year": 4},
    {"roll_number": "2023UCS1009", "name": "Aditya Rao", "passing_year": 2027, "active_year": 4},
    {"roll_number": "2023UCS1010", "name": "Pooja Hegde", "passing_year": 2027, "active_year": 4},
    {"roll_number": "2023UCS1011", "name": "Arjun Reddy", "passing_year": 2027, "active_year": 4},
    {"roll_number": "2023UCS1012", "name": "Meera Nambiar", "passing_year": 2027, "active_year": 4},
    {"roll_number": "2023UCS1013", "name": "Siddharth Joshi", "passing_year": 2027, "active_year": 4},
    {"roll_number": "2023UCS1014", "name": "Tanvi Deshmukh", "passing_year": 2027, "active_year": 4},
    {"roll_number": "2023UCS1015", "name": "Nikhil Choudhary", "passing_year": 2027, "active_year": 4},

    # Batch: Admission 2024 -> Passing Year 2028 (Year 3: Pre-Final Year Batch) - 15 Students
    {"roll_number": "2024UCS1001", "name": "Aryan Gupta", "passing_year": 2028, "active_year": 3},
    {"roll_number": "2024UCS1002", "name": "Ishita Banerjee", "passing_year": 2028, "active_year": 3},
    {"roll_number": "2024UCS1003", "name": "Devendra Rathore", "passing_year": 2028, "active_year": 3},
    {"roll_number": "2024UCS1004", "name": "Prerna Mishra", "passing_year": 2028, "active_year": 3},
    {"roll_number": "2024UCS1005", "name": "Varun Nair", "passing_year": 2028, "active_year": 3},
    {"roll_number": "2024UCS1006", "name": "Neha Bhatia", "passing_year": 2028, "active_year": 3},
    {"roll_number": "2024UCS1007", "name": "Harish Venkatesh", "passing_year": 2028, "active_year": 3},
    {"roll_number": "2024UCS1008", "name": "Kriti Sanon", "passing_year": 2028, "active_year": 3},
    {"roll_number": "2024UCS1009", "name": "Aman Tripathi", "passing_year": 2028, "active_year": 3},
    {"roll_number": "2024UCS1010", "name": "Shreya Ghoshal", "passing_year": 2028, "active_year": 3},
    {"roll_number": "2024UCS1011", "name": "Yash Singhania", "passing_year": 2028, "active_year": 3},
    {"roll_number": "2024UCS1012", "name": "Anjali Menon", "passing_year": 2028, "active_year": 3},
    {"roll_number": "2024UCS1013", "name": "Rahul Dravid", "passing_year": 2028, "active_year": 3},
    {"roll_number": "2024UCS1014", "name": "Bhavna Pillai", "passing_year": 2028, "active_year": 3},
    {"roll_number": "2024UCS1015", "name": "Karan Johar", "passing_year": 2028, "active_year": 3},

    # Batch: Admission 2025 -> Passing Year 2029 (Year 2: Sophomore Batch) - 15 Students
    {"roll_number": "2025UCS1001", "name": "Ayushmann Khurrana", "passing_year": 2029, "active_year": 2},
    {"roll_number": "2025UCS1002", "name": "Radhika Madan", "passing_year": 2029, "active_year": 2},
    {"roll_number": "2025UCS1003", "name": "Kunal Kapoor", "passing_year": 2029, "active_year": 2},
    {"roll_number": "2025UCS1004", "name": "Sanya Malhotra", "passing_year": 2029, "active_year": 2},
    {"roll_number": "2025UCS1005", "name": "Manan Vora", "passing_year": 2029, "active_year": 2},
    {"roll_number": "2025UCS1006", "name": "Divya Khosla", "passing_year": 2029, "active_year": 2},
    {"roll_number": "2025UCS1007", "name": "Tarun Tahiliani", "passing_year": 2029, "active_year": 2},
    {"roll_number": "2025UCS1008", "name": "Swati Mohan", "passing_year": 2029, "active_year": 2},
    {"roll_number": "2025UCS1009", "name": "Gaurav Chopra", "passing_year": 2029, "active_year": 2},
    {"roll_number": "2025UCS1010", "name": "Nandini Sundar", "passing_year": 2029, "active_year": 2},
    {"roll_number": "2025UCS1011", "name": "Sameer Kochhar", "passing_year": 2029, "active_year": 2},
    {"roll_number": "2025UCS1012", "name": "Pallavi Sharda", "passing_year": 2029, "active_year": 2},
    {"roll_number": "2025UCS1013", "name": "Rajat Tokas", "passing_year": 2029, "active_year": 2},
    {"roll_number": "2025UCS1014", "name": "Alisha Chinai", "passing_year": 2029, "active_year": 2},
    {"roll_number": "2025UCS1015", "name": "Chirag Paswan", "passing_year": 2029, "active_year": 2},

    # Batch: Admission 2026 -> Passing Year 2030 (Year 1: Freshman Batch) - 15 Students
    {"roll_number": "2026UCS1001", "name": "Tanishq Abraham", "passing_year": 2030, "active_year": 1},
    {"roll_number": "2026UCS1002", "name": "Avani Lekhara", "passing_year": 2030, "active_year": 1},
    {"roll_number": "2026UCS1003", "name": "Pranav Anand", "passing_year": 2030, "active_year": 1},
    {"roll_number": "2026UCS1004", "name": "Suhani Shah", "passing_year": 2030, "active_year": 1},
    {"roll_number": "2026UCS1005", "name": "Vihaan Agrawal", "passing_year": 2030, "active_year": 1},
    {"roll_number": "2026UCS1006", "name": "Ridhima Ghosh", "passing_year": 2030, "active_year": 1},
    {"roll_number": "2026UCS1007", "name": "Samarth Jaiswal", "passing_year": 2030, "active_year": 1},
    {"roll_number": "2026UCS1008", "name": "Lavanya Tripathi", "passing_year": 2030, "active_year": 1},
    {"roll_number": "2026UCS1009", "name": "Omkar Kadam", "passing_year": 2030, "active_year": 1},
    {"roll_number": "2026UCS1010", "name": "Anika Surendran", "passing_year": 2030, "active_year": 1},
    {"roll_number": "2026UCS1011", "name": "Parthiv Patel", "passing_year": 2030, "active_year": 1},
    {"roll_number": "2026UCS1012", "name": "Trisha Krishnan", "passing_year": 2030, "active_year": 1},
    {"roll_number": "2026UCS1013", "name": "Madhavan Balaji", "passing_year": 2030, "active_year": 1},
    {"roll_number": "2026UCS1014", "name": "Ishani Roy", "passing_year": 2030, "active_year": 1},
    {"roll_number": "2026UCS1015", "name": "Reyansh Goel", "passing_year": 2030, "active_year": 1}
]


# -------------------------------------------------------------
# 3. Deterministic Dataset Generator
# -------------------------------------------------------------
def generate_seed_records():
    """
    Generates realistic marks for all 60 students across completed semesters.
    Uses random.seed(42) to ensure 100% deterministic, reproducible data.
    """
    random.seed(42)
    records = []
    current_id = 1

    for student_meta in STUDENT_ROSTER_60:
        roll_no = student_meta["roll_number"]
        name = student_meta["name"]
        passing_yr = student_meta["passing_year"]
        active_yr = student_meta["active_year"]

        # Student has records for all semesters up to their current year's semesters
        # Year 1 -> Sem 1 & 2
        # Year 2 -> Sem 1, 2, 3, 4
        # Year 3 -> Sem 1, 2, 3, 4, 5, 6
        # Year 4 -> Sem 1, 2, 3, 4, 5, 6, 7, 8
        max_sem = active_yr * 2

        for sem in range(1, max_sem + 1):
            yr = (sem + 1) // 2
            subjects = SEMESTER_SUBJECTS[sem]

            for subj in subjects:
                # Generate realistic assessment marks:
                # Mid-Sem (out of 20): range 12 to 20
                mid_sem = random.randint(12, 20)
                # CT & Lab Viva (out of 30): range 18 to 30
                ct_viva = random.randint(18, 30)
                # End-Sem (out of 50): range 28 to 50
                end_sem = random.randint(28, 50)
                total = mid_sem + ct_viva + end_sem

                record = {
                    "id": current_id,
                    "roll_number": roll_no,
                    "name": name,
                    "passing_year": passing_yr,
                    "year": yr,
                    "semester": sem,
                    "subject": subj,
                    "mid_sem": mid_sem,
                    "ct_viva": ct_viva,
                    "end_sem": end_sem,
                    "total": total
                }
                records.append(record)
                current_id += 1

    return records, current_id


# Initialize in-memory storage with seeded records
students, next_student_id = generate_seed_records()


# -------------------------------------------------------------
# 4. Helper: Find Student Details by Roll Number
# -------------------------------------------------------------
def get_student_by_roll(roll_number):
    """
    Finds existing student metadata (name, passing_year, year) by roll number.
    Returns:
      {"found": True, "roll_number": ..., "name": ..., "passing_year": ..., "year": ...}
      or {"found": False}
    """
    if not roll_number or not isinstance(roll_number, str):
        return {"found": False}

    cleaned_roll = roll_number.strip().upper()
    for s in students:
        if s["roll_number"].upper() == cleaned_roll:
            return {
                "found": True,
                "roll_number": s["roll_number"],
                "name": s["name"],
                "passing_year": s["passing_year"],
                "year": s["year"]
            }
    return {"found": False}


# -------------------------------------------------------------
# 5. Strict Validation Function
# -------------------------------------------------------------
def validate_student(data):
    """
    Validates input data for a new student assessment record.
    Validation rules:
      - roll_number: non-empty string (e.g. 2026UCS1001)
      - name: non-empty string
      - passing_year: integer (2020 to 2035)
      - Admission Year vs. Passing Year:
          If roll_number starts with 4 digits, passing_year must equal admission_year + 4.
      - Enforce One Name & Passing Year per Roll Number:
          If roll_number already exists, submitted name and passing_year must match.
      - year: integer (1 to 4)
      - semester: integer (1 to 8, must belong to selected year)
      - subject: must belong to the selected semester's subjects
      - mid_sem: 0 to 20
      - ct_viva: 0 to 30
      - end_sem: 0 to 50
      - uniqueness: (roll_number, semester, subject) must NOT already exist
    Returns:
      (is_valid: bool, cleaned_data_or_error: dict|str)
    """
    if not isinstance(data, dict):
        return False, "Invalid request payload. Expected JSON object."

    # Validate Roll Number
    roll_number = data.get("roll_number")
    if not roll_number or not isinstance(roll_number, str) or not roll_number.strip():
        return False, "Roll number is required (e.g. 2026UCS1001)."
    cleaned_roll = roll_number.strip().upper()

    # Validate Name
    name = data.get("name")
    if not name or not isinstance(name, str) or not name.strip():
        return False, "Student name is required and cannot be empty."
    cleaned_name = name.strip()

    # Validate Passing Year (Batch)
    try:
        passing_year = int(data.get("passing_year", 0))
    except (ValueError, TypeError):
        return False, "Passing Year must be a valid 4-digit year (e.g. 2030)."

    if passing_year < 2020 or passing_year > 2035:
        return False, "Passing Year must be between 2020 and 2035."

    # Rule 1: Validate Admission Year prefix vs. Passing Year (B.Tech = 4 years)
    if len(cleaned_roll) >= 4 and cleaned_roll[:4].isdigit():
        admission_year = int(cleaned_roll[:4])
        expected_passing_year = admission_year + 4
        if passing_year != expected_passing_year:
            return False, f"Passing Year ({passing_year}) must be exactly 4 years after Admission Year ({admission_year}). Expected Passing Year: {expected_passing_year}."

    # Rule 2: Enforce One Name & Passing Year per Roll Number
    for s in students:
        if s["roll_number"].upper() == cleaned_roll:
            if s["name"].strip().lower() != cleaned_name.lower():
                return False, f"Roll number {cleaned_roll} already belongs to {s['name']}. You cannot assign a different name."
            if s["passing_year"] != passing_year:
                return False, f"Roll number {cleaned_roll} belongs to Passing Year {s['passing_year']}. You cannot assign a different passing year."
            break

    # Validate Academic Year (1 to 4)
    try:
        year = int(data.get("year", 0))
    except (ValueError, TypeError):
        return False, "Academic Year must be an integer between 1 and 4."

    if year < 1 or year > 4:
        return False, "Academic Year must be between 1 and 4."

    # Validate Semester (1 to 8)
    try:
        semester = int(data.get("semester", 0))
    except (ValueError, TypeError):
        return False, "Semester must be an integer between 1 and 8."

    if semester < 1 or semester > 8:
        return False, "Semester must be between 1 and 8."

    # Strict Year -> Semester Coupling check
    valid_semesters = YEAR_SEMESTERS.get(year, [])
    if semester not in valid_semesters:
        return False, f"Semester {semester} does not belong to Year {year} (Year {year} comprises Semesters {valid_semesters[0]} & {valid_semesters[1]})."

    # Validate Subject (Strict Semester -> Subject Coupling)
    subject = data.get("subject")
    if not subject or not isinstance(subject, str) or not subject.strip():
        return False, "Subject is required."

    cleaned_subject = subject.strip()
    allowed_subjects = SEMESTER_SUBJECTS.get(semester, [])
    if cleaned_subject not in allowed_subjects:
        return False, f"Subject '{cleaned_subject}' is not offered in Semester {semester}. Allowed: {', '.join(allowed_subjects)}."

    # Check for Duplicate Record for this Student & Subject
    for s in students:
        if (s["roll_number"].upper() == cleaned_roll and
            s["semester"] == semester and
            s["subject"].lower() == cleaned_subject.lower()):
            return False, f"Record already exists for Roll No. {cleaned_roll} in Semester {semester} ({cleaned_subject})."

    # Validate Mid-Sem (max 20)
    try:
        mid_sem = float(data.get("mid_sem", -1))
    except (ValueError, TypeError):
        return False, "Mid-Sem marks must be a valid number."

    if mid_sem < 0 or mid_sem > 20:
        return False, "Mid-Sem marks must be between 0 and 20."

    # Validate CT & Lab Viva (max 30)
    try:
        ct_viva = float(data.get("ct_viva", -1))
    except (ValueError, TypeError):
        return False, "CT & Viva marks must be a valid number."

    if ct_viva < 0 or ct_viva > 30:
        return False, "CT & Viva marks must be between 0 and 30."

    # Validate End-Sem (max 50)
    try:
        end_sem = float(data.get("end_sem", -1))
    except (ValueError, TypeError):
        return False, "End-Sem marks must be a valid number."

    if end_sem < 0 or end_sem > 50:
        return False, "End-Sem marks must be between 0 and 50."

    def clean_number(val):
        return int(val) if val.is_integer() else round(val, 1)

    cleaned_data = {
        "roll_number": cleaned_roll,
        "name": cleaned_name,
        "passing_year": passing_year,
        "year": year,
        "semester": semester,
        "subject": cleaned_subject,
        "mid_sem": clean_number(mid_sem),
        "ct_viva": clean_number(ct_viva),
        "end_sem": clean_number(end_sem)
    }
    return True, cleaned_data


# -------------------------------------------------------------
# 6. Filter & Analytics Engine
# -------------------------------------------------------------
def get_students_and_stats(year=None, semester=None, subject=None, passing_year=None):
    """
    Filters student evaluation records based on academic criteria.
    Sorts matching records descending by total score.
    Computes analytics dictionary:
      - total_college_students: count of unique students across entire college (60)
      - view_unique_students: count of unique students in active filtered view
      - view_record_count: count of assessment records in active view
      - average_marks: mean score of records in view
      - highest_marks: top total score in view
      - topper_name: student name with rank 1
      - topper_roll: roll number of topper
    """
    filtered_list = []

    for s in students:
        # Check Passing Year / Batch filter
        if passing_year and str(passing_year).strip().lower() != "all":
            if str(s["passing_year"]) != str(passing_year).strip():
                continue

        # Check Academic Year filter
        if year and str(year).strip().lower() != "all":
            if str(s["year"]) != str(year).strip():
                continue

        # Check Semester filter
        if semester and str(semester).strip().lower() != "all":
            if str(s["semester"]) != str(semester).strip():
                continue

        # Check Subject filter
        if subject and str(subject).strip().lower() != "all":
            if s["subject"].strip().lower() != str(subject).strip().lower():
                continue

        # Recalculate/verify total
        total = s["mid_sem"] + s["ct_viva"] + s["end_sem"]
        total = int(total) if isinstance(total, float) and total.is_integer() else round(total, 1)
        s["total"] = total

        filtered_list.append(s.copy())

    # Sort descending by total score
    filtered_list.sort(key=lambda s: s["total"], reverse=True)

    # Assign ranks (1-indexed for the active view)
    for index, student in enumerate(filtered_list, start=1):
        student["rank"] = index

    # Total unique students in college across all records
    college_unique_students = len(set(s["roll_number"] for s in students))
    view_unique_students = len(set(s["roll_number"] for s in filtered_list))
    view_record_count = len(filtered_list)

    if view_record_count > 0:
        total_sum = sum(s["total"] for s in filtered_list)
        average_marks = round(total_sum / view_record_count, 1)
        highest_marks = filtered_list[0]["total"]
        topper_name = filtered_list[0]["name"]
        topper_roll = filtered_list[0]["roll_number"]
    else:
        average_marks = 0.0
        highest_marks = 0
        topper_name = "N/A"
        topper_roll = "N/A"

    stats = {
        "total_college_students": college_unique_students,
        "view_unique_students": view_unique_students,
        "view_record_count": view_record_count,
        "average_marks": average_marks,
        "highest_marks": highest_marks,
        "topper_name": topper_name,
        "topper_roll": topper_roll
    }

    return {
        "students": filtered_list,
        "stats": stats
    }


# -------------------------------------------------------------
# 7. CRUD Helpers
# -------------------------------------------------------------
def add_student(data):
    """
    Validates and appends a new assessment record.
    Returns:
      (new_record, None) on success
      (None, error_message) on failure
    """
    global next_student_id

    is_valid, result = validate_student(data)
    if not is_valid:
        return None, result

    cleaned_data = result
    total = cleaned_data["mid_sem"] + cleaned_data["ct_viva"] + cleaned_data["end_sem"]
    total = int(total) if isinstance(total, float) and total.is_integer() else round(total, 1)

    new_record = {
        "id": next_student_id,
        "roll_number": cleaned_data["roll_number"],
        "name": cleaned_data["name"],
        "passing_year": cleaned_data["passing_year"],
        "year": cleaned_data["year"],
        "semester": cleaned_data["semester"],
        "subject": cleaned_data["subject"],
        "mid_sem": cleaned_data["mid_sem"],
        "ct_viva": cleaned_data["ct_viva"],
        "end_sem": cleaned_data["end_sem"],
        "total": total
    }

    students.append(new_record)
    next_student_id += 1

    return new_record, None


def delete_student(record_id):
    """
    Removes an assessment record by its unique database ID.
    Returns True if removed, False otherwise.
    """
    for index, student in enumerate(students):
        if student["id"] == record_id:
            students.pop(index)
            return True
    return False
