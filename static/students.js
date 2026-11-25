const studentList = document.querySelector("#student-list");
const studentForm = document.querySelector("#student-form");
const statusMessage = document.querySelector("#status-message");
const studentCount = document.querySelector("#student-count");
const courseCount = document.querySelector("#course-count");

function showMessage(message, isError = false) {
    statusMessage.textContent = message;
    statusMessage.classList.toggle("error", isError);
}

function updateSummary() {
    const rows = [...studentList.querySelectorAll("tr[data-student-id]")];
    const courses = new Set(
        rows.map((row) => row.querySelector(".course-tag").textContent)
    );
    studentCount.textContent = rows.length;
    courseCount.textContent = courses.size;
}

function createStudentRow(student) {
    const row = document.createElement("tr");
    row.dataset.studentId = student.id;

    const nameCell = document.createElement("td");
    nameCell.className = "student-name";
    nameCell.textContent = student.name;

    const emailCell = document.createElement("td");
    emailCell.textContent = student.email;

    const courseCell = document.createElement("td");
    const courseTag = document.createElement("span");
    courseTag.className = "course-tag";
    courseTag.textContent = student.course;
    courseCell.append(courseTag);

    const actionsCell = document.createElement("td");
    actionsCell.className = "actions";
    const form = document.createElement("form");
    form.method = "post";
    form.action = studentList.dataset.deleteUrl.replace(/0\/delete$/, `${student.id}/delete`);
    form.dataset.deleteForm = "";

    const button = document.createElement("button");
    button.className = "delete-button";
    button.type = "submit";
    button.textContent = "Delete";
    form.append(button);
    actionsCell.append(form);

    row.append(nameCell, emailCell, courseCell, actionsCell);
    return row;
}

function removeEmptyState() {
    studentList.querySelector(".empty-row")?.remove();
}

studentForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const submitButton = studentForm.querySelector('button[type="submit"]');
    submitButton.disabled = true;

    try {
        const formData = new FormData(studentForm);
        const response = await fetch(studentList.dataset.apiUrl, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(Object.fromEntries(formData))
        });
        const result = await response.json();

        if (!response.ok) {
            showMessage(result.error || "Could not add the student.", true);
            return;
        }

        removeEmptyState();
        studentList.prepend(createStudentRow(result));
        studentForm.reset();
        updateSummary();
        showMessage("Student added successfully.");
    } catch {
        showMessage("Could not reach the server. Please try again.", true);
    } finally {
        submitButton.disabled = false;
    }
});

studentList.addEventListener("submit", async (event) => {
    const form = event.target.closest("[data-delete-form]");
    if (!form) {
        return;
    }

    event.preventDefault();
    const row = form.closest("tr");
    const studentId = row.dataset.studentId;

    try {
        const response = await fetch(`${studentList.dataset.apiUrl}/${studentId}`, {
            method: "DELETE"
        });

        if (!response.ok) {
            const result = await response.json();
            showMessage(result.error || "Could not delete the student.", true);
            return;
        }

        row.remove();
        if (!studentList.querySelector("tr[data-student-id]")) {
            const emptyRow = document.createElement("tr");
            emptyRow.className = "empty-row";
            const cell = document.createElement("td");
            cell.colSpan = 4;
            cell.textContent = "No students yet. Add a record below to get started.";
            emptyRow.append(cell);
            studentList.append(emptyRow);
        }
        updateSummary();
        showMessage("Student record deleted.");
    } catch {
        showMessage("Could not reach the server. Please try again.", true);
    }
});
