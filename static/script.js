/**
 * Academic Performance Tracker - Frontend Controller
 * ----------------------------------------------------
 * Features:
 * - Pure HTML/CSS/JS Modal Popup controls for adding student records.
 * - Strict Year -> Semester -> Subject dropdown coupling in Modal & Filters.
 * - Live Fetch API requests (GET with 4 filter parameters, POST, DELETE).
 * - Real-time updates for 4 Analytics Cards and Leaderboard table.
 * - One Name per Roll Number enforcement:
 *     Auto-looks up existing roll numbers, auto-fills name and passing year,
 *     and locks them so duplicate roll numbers cannot have conflicting names.
 * - B.Tech 4-Year calculation:
 *     Admission Year prefix + 4 auto-selects expected Passing Year.
 */

// -------------------------------------------------------------
// 1. Academic Hierarchy (32 Subjects across 8 Semesters)
// -------------------------------------------------------------
const SEMESTER_SUBJECTS = {
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
};

const YEAR_SEMESTERS = {
  1: [1, 2],
  2: [3, 4],
  3: [5, 6],
  4: [7, 8]
};


// -------------------------------------------------------------
// 2. DOM Elements
// -------------------------------------------------------------
// Modal Elements
const addStudentModal = document.getElementById("add-student-modal");
const openModalBtn = document.getElementById("open-modal-btn");
const closeModalBtn = document.getElementById("close-modal-btn");
const cancelModalBtn = document.getElementById("cancel-modal-btn");

// Form Elements
const studentForm = document.getElementById("student-form");
const rollNumberInput = document.getElementById("roll_number");
const nameInput = document.getElementById("name");
const formPassingYearSelect = document.getElementById("form-passing-year");
const formYearSelect = document.getElementById("form-year");
const formSemesterSelect = document.getElementById("form-semester");
const formSubjectSelect = document.getElementById("form-subject");
const midSemInput = document.getElementById("mid_sem");
const ctVivaInput = document.getElementById("ct_viva");
const endSemInput = document.getElementById("end_sem");

// Status Hints in Form
const rollStatusHint = document.getElementById("roll-status-hint");
const nameStatusHint = document.getElementById("name-status-hint");

// Filter Toolbar Elements
const filterPassingYear = document.getElementById("filter-passing-year");
const filterYear = document.getElementById("filter-year");
const filterSemester = document.getElementById("filter-semester");
const filterSubject = document.getElementById("filter-subject");

// Table & Alert Elements
const studentsTableBody = document.getElementById("students-table-body");
const studentCountBadge = document.getElementById("student-count-badge");
const alertBox = document.getElementById("alert-box");

// Analytics Cards Elements
const statViewStudents = document.getElementById("stat-view-students");
const statTotalStudents = document.getElementById("stat-total-students");
const statAvgMarks = document.getElementById("stat-avg-marks");
const statHighestMarks = document.getElementById("stat-highest-marks");
const statTopperName = document.getElementById("stat-topper-name");
const statTopperMeta = document.getElementById("stat-topper-meta");

let alertTimeout = null;
let rollLookupTimer = null;


// -------------------------------------------------------------
// 3. Notification Helper
// -------------------------------------------------------------
function showAlert(message, type = "success") {
  if (alertTimeout) {
    clearTimeout(alertTimeout);
  }

  alertBox.textContent = message;
  alertBox.className = `alert-box ${type}`;

  alertTimeout = setTimeout(() => {
    alertBox.className = "alert-box hidden";
  }, 4000);
}


// -------------------------------------------------------------
// 4. Modal Open / Close Logic
// -------------------------------------------------------------
function openModal() {
  addStudentModal.classList.remove("hidden");
  unlockStudentFields(false);
  syncModalDropdowns();
  setTimeout(() => rollNumberInput.focus(), 50);
}

function closeModal() {
  addStudentModal.classList.add("hidden");
  unlockStudentFields(false);
  studentForm.reset();
}


// -------------------------------------------------------------
// 5. One Name Per Roll Number: Auto-fill & Locking
// -------------------------------------------------------------
function lockStudentFields(name, passingYear) {
  nameInput.value = name;
  nameInput.readOnly = true;
  formPassingYearSelect.value = passingYear;
  formPassingYearSelect.disabled = true;

  if (rollStatusHint) {
    rollStatusHint.textContent = "🔒 Registered student found";
    rollStatusHint.className = "field-hint locked";
  }
  if (nameStatusHint) {
    nameStatusHint.textContent = `Locked to registered name: ${name} (Batch ${passingYear})`;
    nameStatusHint.className = "field-hint locked";
  }
}

function unlockStudentFields(showNewHint = false) {
  nameInput.readOnly = false;
  formPassingYearSelect.disabled = false;

  if (rollStatusHint) {
    if (showNewHint) {
      rollStatusHint.textContent = "✨ New student record";
      rollStatusHint.className = "field-hint new";
    } else {
      rollStatusHint.textContent = "";
      rollStatusHint.className = "field-hint";
    }
  }
  if (nameStatusHint) {
    nameStatusHint.textContent = "";
    nameStatusHint.className = "field-hint";
  }
}

async function handleRollInput() {
  clearTimeout(rollLookupTimer);
  const rawRoll = rollNumberInput.value.trim().toUpperCase();

  // B.Tech 4-Year calculation: If starts with 4-digit admission year, auto-select Passing Year = Admission + 4
  if (rawRoll.length >= 4 && !isNaN(rawRoll.substring(0, 4))) {
    const admYear = parseInt(rawRoll.substring(0, 4), 10);
    const expectedPassing = admYear + 4;
    const exists = Array.from(formPassingYearSelect.options).some(
      (opt) => parseInt(opt.value, 10) === expectedPassing
    );
    if (exists && !formPassingYearSelect.disabled) {
      formPassingYearSelect.value = expectedPassing;
    }
  }

  if (rawRoll.length < 4) {
    unlockStudentFields(false);
    return;
  }

  // Lookup existing student from backend
  rollLookupTimer = setTimeout(async () => {
    try {
      const res = await fetch(`/api/student/${encodeURIComponent(rawRoll)}`);
      if (res.ok) {
        const data = await res.json();
        if (data.found) {
          lockStudentFields(data.name, data.passing_year);
        } else {
          unlockStudentFields(true);
        }
      } else {
        unlockStudentFields(false);
      }
    } catch (e) {
      console.warn("Roll lookup failed:", e);
      unlockStudentFields(false);
    }
  }, 200);
}


// -------------------------------------------------------------
// 6. Strict Modal Dropdown Synchronization
// -------------------------------------------------------------
function syncModalDropdowns() {
  const selectedYear = parseInt(formYearSelect.value, 10) || 1;
  const sems = YEAR_SEMESTERS[selectedYear] || [1, 2];

  // Populate Semesters for selected Year
  formSemesterSelect.innerHTML = sems
    .map((s) => `<option value="${s}">Semester ${s}</option>`)
    .join("");

  // Populate Subjects for the current Semester
  syncModalSubjects();
}

function syncModalSubjects() {
  const selectedSem = parseInt(formSemesterSelect.value, 10) || 1;
  const subjects = SEMESTER_SUBJECTS[selectedSem] || [];

  formSubjectSelect.innerHTML = subjects
    .map((sub) => `<option value="${escapeHtml(sub)}">${escapeHtml(sub)}</option>`)
    .join("");
}


// -------------------------------------------------------------
// 7. Strict Leaderboard Filter Synchronization
// -------------------------------------------------------------
function syncFilterDropdowns() {
  const yearVal = filterYear.value;
  const previousSem = filterSemester.value;

  if (yearVal === "all") {
    // Show all 8 semesters
    let semOptions = `<option value="all">All Semesters</option>`;
    for (let s = 1; s <= 8; s++) {
      semOptions += `<option value="${s}">Semester ${s}</option>`;
    }
    filterSemester.innerHTML = semOptions;
  } else {
    // Show only semesters for the selected year
    const yr = parseInt(yearVal, 10);
    const sems = YEAR_SEMESTERS[yr] || [];
    let semOptions = `<option value="all">All Semesters (Yr ${yr})</option>`;
    sems.forEach((s) => {
      semOptions += `<option value="${s}">Semester ${s}</option>`;
    });
    filterSemester.innerHTML = semOptions;
  }

  // Restore previous semester selection if still valid, otherwise default to first valid
  const exists = Array.from(filterSemester.options).some((opt) => opt.value === previousSem);
  if (exists) {
    filterSemester.value = previousSem;
  } else {
    filterSemester.selectedIndex = 0;
  }

  // Now sync subjects for the filter
  syncFilterSubjects();
}

function syncFilterSubjects() {
  const semVal = filterSemester.value;
  const yearVal = filterYear.value;
  const previousSub = filterSubject.value;

  let subOptions = `<option value="all">All Subjects</option>`;

  if (semVal !== "all") {
    const sem = parseInt(semVal, 10);
    const subjects = SEMESTER_SUBJECTS[sem] || [];
    subjects.forEach((sub) => {
      subOptions += `<option value="${escapeHtml(sub)}">${escapeHtml(sub)}</option>`;
    });
  } else if (yearVal !== "all") {
    const yr = parseInt(yearVal, 10);
    const sems = YEAR_SEMESTERS[yr] || [];
    sems.forEach((s) => {
      const subjects = SEMESTER_SUBJECTS[s] || [];
      subjects.forEach((sub) => {
        subOptions += `<option value="${escapeHtml(sub)}">${escapeHtml(sub)} (Sem ${s})</option>`;
      });
    });
  } else {
    // All 32 subjects
    for (let s = 1; s <= 8; s++) {
      const subjects = SEMESTER_SUBJECTS[s] || [];
      subjects.forEach((sub) => {
        subOptions += `<option value="${escapeHtml(sub)}">${escapeHtml(sub)}</option>`;
      });
    }
  }

  filterSubject.innerHTML = subOptions;

  const subExists = Array.from(filterSubject.options).some((opt) => opt.value === previousSub);
  if (subExists) {
    filterSubject.value = previousSub;
  } else {
    filterSubject.value = "all";
  }
}


// -------------------------------------------------------------
// 8. Load Filtered Records & Update Analytics
// -------------------------------------------------------------
async function loadStudents() {
  const passingYear = filterPassingYear.value;
  const year = filterYear.value;
  const semester = filterSemester.value;
  const subject = filterSubject.value;

  const url = `/api/students?passing_year=${encodeURIComponent(passingYear)}&year=${encodeURIComponent(year)}&semester=${encodeURIComponent(semester)}&subject=${encodeURIComponent(subject)}`;

  try {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`Server returned HTTP ${response.status}`);
    }

    const data = await response.json();
    const students = data.students || [];
    const stats = data.stats || {};

    // 1. Update 4 Analytics Cards
    statViewStudents.textContent = stats.view_unique_students ?? 0;
    statTotalStudents.textContent = stats.total_college_students ?? 0;
    statAvgMarks.textContent = stats.average_marks ?? "0.0";
    statHighestMarks.textContent = stats.highest_marks ?? "0";
    statTopperName.textContent = stats.topper_name ?? "N/A";
    
    if (stats.view_record_count > 0 && stats.topper_roll !== "N/A") {
      statTopperMeta.textContent = `${stats.topper_roll} • Score: ${stats.highest_marks}/100`;
    } else {
      statTopperMeta.textContent = "No Records in View";
    }

    // Update count badge in table header
    studentCountBadge.textContent = `${stats.view_record_count} Record${stats.view_record_count === 1 ? "" : "s"}`;

    // 2. Render Leaderboard Table
    studentsTableBody.innerHTML = "";

    if (students.length === 0) {
      studentsTableBody.innerHTML = `
        <tr>
          <td colspan="11" class="text-center py-4 text-muted">
            No assessment records found matching active filters (Batch: ${escapeHtml(passingYear)}, Year: ${escapeHtml(year)}, Sem: ${escapeHtml(semester)}).
          </td>
        </tr>
      `;
      return;
    }

    students.forEach((student) => {
      const row = document.createElement("tr");

      row.innerHTML = `
        <td class="text-center">
          <span class="${getRankBadgeClass(student.rank)}">${student.rank}</span>
        </td>
        <td><span class="roll-no-tag">${escapeHtml(student.roll_number)}</span></td>
        <td><strong>${escapeHtml(student.name)}</strong></td>
        <td class="text-center"><span class="batch-tag">${student.passing_year}</span></td>
        <td class="text-center"><span class="sem-tag">Yr ${student.year} • Sem ${student.semester}</span></td>
        <td><span class="subject-tag" title="${escapeHtml(student.subject)}">${escapeHtml(student.subject)}</span></td>
        <td class="text-center">${student.mid_sem}</td>
        <td class="text-center">${student.ct_viva}</td>
        <td class="text-center">${student.end_sem}</td>
        <td class="text-center"><span class="total-score">${student.total}</span></td>
        <td class="text-center">
          <button 
            type="button" 
            class="btn-delete" 
            onclick="handleDeleteStudent(${student.id}, '${escapeHtml(student.name)}', '${escapeHtml(student.subject)}')"
            title="Delete this assessment record"
          >
            ✕ Delete
          </button>
        </td>
      `;

      studentsTableBody.appendChild(row);
    });

  } catch (error) {
    console.error("Error loading records:", error);
    showAlert("Could not connect to backend server. Verify Flask is running.", "error");
  }
}


// -------------------------------------------------------------
// 9. Handle Form Submission (Add Record)
// -------------------------------------------------------------
async function handleAddStudent(event) {
  event.preventDefault();

  const payload = {
    roll_number: rollNumberInput.value.trim().toUpperCase(),
    name: nameInput.value.trim(),
    passing_year: parseInt(formPassingYearSelect.value, 10),
    year: parseInt(formYearSelect.value, 10),
    semester: parseInt(formSemesterSelect.value, 10),
    subject: formSubjectSelect.value.trim(),
    mid_sem: parseFloat(midSemInput.value),
    ct_viva: parseFloat(ctVivaInput.value),
    end_sem: parseFloat(endSemInput.value)
  };

  try {
    const response = await fetch("/api/students", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(payload)
    });

    const result = await response.json();

    if (response.status === 201) {
      // Clear form and close modal
      studentForm.reset();
      unlockStudentFields(false);
      closeModal();

      showAlert(`✓ Saved assessment for ${result.name} (${result.roll_number}) in ${result.subject} — Score: ${result.total}/100`, "success");

      // Instantly refresh analytics and table
      loadStudents();
    } else {
      // Display validation error or duplicate error
      showAlert(result.error || "Failed to add assessment record.", "error");
    }

  } catch (error) {
    console.error("Error submitting student record:", error);
    showAlert("Network error. Could not save assessment record.", "error");
  }
}


// -------------------------------------------------------------
// 10. Handle Record Deletion
// -------------------------------------------------------------
async function handleDeleteStudent(recordId, studentName, subjectName) {
  const confirmed = confirm(`Are you sure you want to remove the assessment record for ${studentName} (${subjectName})?`);
  if (!confirmed) {
    return;
  }

  try {
    const response = await fetch(`/api/students/${recordId}`, {
      method: "DELETE"
    });

    const result = await response.json();

    if (response.ok) {
      showAlert(`✓ Assessment record removed successfully.`, "success");
      loadStudents();
    } else {
      showAlert(result.error || "Failed to delete record.", "error");
    }

  } catch (error) {
    console.error("Error deleting record:", error);
    showAlert("Network error. Could not delete assessment record.", "error");
  }
}


// -------------------------------------------------------------
// 11. Helpers
// -------------------------------------------------------------
function getRankBadgeClass(rank) {
  if (rank === 1) return "rank-badge rank-1";
  if (rank === 2) return "rank-badge rank-2";
  if (rank === 3) return "rank-badge rank-3";
  return "rank-badge rank-default";
}

function escapeHtml(text) {
  if (typeof text !== "string") return text;
  const div = document.createElement("div");
  div.innerText = text;
  return div.innerHTML;
}


// -------------------------------------------------------------
// 12. Event Listeners Initialization
// -------------------------------------------------------------
document.addEventListener("DOMContentLoaded", () => {
  // Setup Modal Event Listeners
  openModalBtn.addEventListener("click", openModal);
  closeModalBtn.addEventListener("click", closeModal);
  cancelModalBtn.addEventListener("click", closeModal);

  // Close modal when clicking outside modal-card
  addStudentModal.addEventListener("click", (e) => {
    if (e.target === addStudentModal) {
      closeModal();
    }
  });

  // Close modal on Escape key
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && !addStudentModal.classList.contains("hidden")) {
      closeModal();
    }
  });

  // Roll Number live lookup for auto-fill & name locking
  rollNumberInput.addEventListener("input", handleRollInput);

  // Modal strict couplings
  formYearSelect.addEventListener("change", syncModalDropdowns);
  formSemesterSelect.addEventListener("change", syncModalSubjects);

  // Initial modal sync
  syncModalDropdowns();

  // Filters strict couplings
  filterYear.addEventListener("change", () => {
    syncFilterDropdowns();
    loadStudents();
  });

  filterSemester.addEventListener("change", () => {
    syncFilterSubjects();
    loadStudents();
  });

  filterPassingYear.addEventListener("change", loadStudents);
  filterSubject.addEventListener("change", loadStudents);

  // Initial filter sync (defaults to Year 1 and Semester 1)
  filterYear.value = "1";
  syncFilterDropdowns();
  filterSemester.value = "1";
  syncFilterSubjects();

  // Handle Form Submission
  studentForm.addEventListener("submit", handleAddStudent);

  // Initial load
  loadStudents();
});
