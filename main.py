import sqlite3
import streamlit as st
import pandas as pd

# Database setup
def create_table():
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS students (
                      id INTEGER PRIMARY KEY,
                      name TEXT NOT NULL,
                      age INTEGER,
                      grade REAL)''')
    conn.commit()
    conn.close()

def add_student(id, name, age, grade):
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO students (id, name, age, grade) VALUES (?, ?, ?, ?)", 
                   (id, name, age, grade))
    conn.commit()
    conn.close()

def view_students():
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students")
    rows = cursor.fetchall()
    conn.close()
    return rows

def update_student(id, name, age, grade):
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE students SET name=?, age=?, grade=? WHERE id=?", 
                   (name, age, grade, id))
    conn.commit()
    conn.close()

def delete_student(id):
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE id=?", (id,))
    conn.commit()
    conn.close()

def student_exists(student_id):
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM students WHERE id=?", (student_id,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists

# Sorting and Searching
def quicksort(arr, key):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x[key] < pivot[key]]
    middle = [x for x in arr if x[key] == pivot[key]]
    right = [x for x in arr if x[key] > pivot[key]]
    return quicksort(left, key) + middle + quicksort(right, key)

def binary_search(arr, target, key):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid][key] == target:
            return arr[mid]
        elif arr[mid][key] < target:
            left = mid + 1
        else:
            right = mid - 1
    return None

# Initialize the database
create_table()

# Streamlit UI
st.title("Student Record Management System")

# Two columns for Add Student and Update Student
col1, col2 = st.columns(2)

# Add Student in the first column
with col1:
    st.subheader("Add Student")
    id = st.number_input("ID", min_value=1, step=1, key="add_id")
    name = st.text_input("Name", key="add_name")
    age = st.number_input("Age", min_value=1, step=1, key="add_age")
    grade = st.number_input("Grade", min_value=0.0, step=0.1, key="add_grade")

    if st.button("Add", key="add_button"):
        if student_exists(id):
            st.error(f"Student ID {id} already exists. Please enter a unique ID.")
        else:
            add_student(id, name, age, grade)
            st.success(f"Student {name} added successfully!")

# Update Student in the second column
with col2:
    st.subheader("Update Student")
    update_id = st.number_input("Enter ID of the Student to Update", min_value=1, step=1, key="update_id")
    new_name = st.text_input("New Name", key="update_name")
    new_age = st.number_input("New Age", min_value=1, step=1, key="update_age")
    new_grade = st.number_input("New Grade", min_value=0.0, step=0.1, key="update_grade")

    if st.button("Update", key="update_button"):
        if student_exists(update_id):
            update_student(update_id, new_name, new_age, new_grade)
            st.success(f"Student ID {update_id} updated successfully!")
        else:
            st.error(f"Student ID {update_id} does not exist.")


# View Students with optional highlight and sorting
def display_students_with_highlight(students, highlight_row=None, sort_key=0):
    # Apply QuickSort to the student list
    sorted_students = quicksort(students, sort_key)

    df = pd.DataFrame(sorted_students, columns=["ID", "Name", "Age", "Grade"])

    # Highlighting condition
    if highlight_row is not None:
        def highlight_row_condition(row):
            return ['background-color: yellow' if row.name == highlight_row else '' for _ in row]

        # Apply highlighting to the DataFrame and set a fixed width for the table
        styled_df = df.style.apply(highlight_row_condition, axis=1)
        st.write(styled_df)  # Display styled DataFrame with row index visible
    else:
        # Display the DataFrame with row index visible
        st.table(df)

# Two columns for Search Student and Delete Student
col1, col2 = st.columns(2)

# Search Student in the first column
with col1:
    st.subheader("Search Student")
    search_by = st.selectbox("Search By", ["ID", "Name", "Age", "Grade"], key="search_by")
    search_value = st.text_input(f"Enter Student {search_by}", key="search_value")
    highlight_index = None

    if st.button("Search", key="search_button"):
        key = {"ID": 0, "Name": 1, "Age": 2, "Grade": 3}[search_by]
        if search_by in ["ID", "Age"]:
            search_value = int(search_value) if search_value.isdigit() else None
        elif search_by == "Grade":
            search_value = float(search_value) if search_value.replace('.', '', 1).isdigit() else None

        if search_value is not None:
            # Assuming view_students() returns the current list of students
            sorted_students = quicksort(view_students(), key)
            student = binary_search(sorted_students, search_value, key)
            if student:
                highlight_index = sorted_students.index(student)
                st.success("Student found!")
            else:
                st.error(f"No student found with {search_by}: {search_value}")
        else:
            st.error(f"Invalid {search_by} input.")

# Delete Student in the second column
with col2:
    st.subheader("Delete Student")
    delete_id = st.number_input("Enter ID of the Student to Delete", min_value=1, step=1, key="delete_id")

    if st.button("Delete", key="delete_button"):
        if student_exists(delete_id):
            delete_student(delete_id)
            st.success(f"Student ID {delete_id} deleted successfully!")
        else:
            st.error(f"Student ID {delete_id} does not exist.")

# View Students with sorting and highlighting
st.subheader("View All Students")
students = view_students()

if students:
    # Add SelectBox for sorting column selection
    sort_column = st.selectbox("Sort By", ["ID", "Name", "Age", "Grade"], key="sort_column")
    sort_key = {"ID": 0, "Name": 1, "Age": 2, "Grade": 3}[sort_column]

    # Display the sorted students with optional highlight
    display_students_with_highlight(students, highlight_row=highlight_index, sort_key=sort_key)
else:
    st.info("No student records found.")
