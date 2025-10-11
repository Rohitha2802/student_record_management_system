from flask import Flask, render_template, request, redirect, url_for, flash
import operator

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # For flash messages

students = []  # In-memory storage

def sort_students(students_list, sort_by, direction='asc'):
    """Helper to sort students list."""
    reverse = direction == 'desc'
    try:
        if sort_by == 'id':
            students_list.sort(key=operator.itemgetter('id'), reverse=reverse)
        elif sort_by == 'name':
            students_list.sort(key=operator.itemgetter('name'), reverse=reverse)
        elif sort_by == 'age':
            students_list.sort(key=lambda x: int(x['age']) if x['age'].isdigit() else 0, reverse=reverse)
        elif sort_by == 'grade':
            students_list.sort(key=operator.itemgetter('grade'), reverse=reverse)
    except Exception as e:
        flash(f'Sorting error: {str(e)}', 'error')
    return students_list

@app.route('/')
@app.route('/view/<sort_by>/<direction>')
def index(sort_by=None, direction='asc'):
    # Always start with a copy of the global students list
    students_to_pass = students[:]
    
    # Apply sorting if requested
    if sort_by:
        students_to_pass = sort_students(students_to_pass, sort_by, direction)
    
    return render_template('index.html', students=students_to_pass)

@app.route('/add', methods=['POST'])
def add_student():
    student_id = request.form['id'].strip()
    if any(s['id'] == student_id for s in students):
        flash('Error: Student ID already exists!', 'error')
        return redirect(url_for('index'))
    
    name = request.form['name'].strip()
    age = request.form['age'].strip()
    grade = request.form['grade'].strip()
    
    student = {
        'id': student_id,
        'name': name,
        'age': age,
        'grade': grade
    }
    students.append(student)
    flash(f'Student "{name}" added successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/search', methods=['GET', 'POST'])
def search_student():
    if request.method == 'POST':
        search_term = request.form['search_term'].strip().lower()
        search_results = [s for s in students if (search_term in s['id'].lower() or search_term in s['name'].lower())]
        # Pass full students list too, for consistency
        return render_template('index.html', students=students, search_results=search_results, search_term=search_term)
    return redirect(url_for('index'))

@app.route('/update/<student_id>', methods=['POST'])
def update_student(student_id):
    for student in students:
        if student['id'] == student_id:
            old_name = student['name']
            student['name'] = request.form.get('name', student['name']).strip()
            student['age'] = request.form.get('age', student['age']).strip()
            student['grade'] = request.form.get('grade', student['grade']).strip()
            flash(f'Student "{student["name"]}" (ID: {student_id}) updated successfully!', 'success')
            return redirect(url_for('index'))
    flash('Error: Student ID not found for update!', 'error')
    return redirect(url_for('index'))

@app.route('/delete/<student_id>')
def delete_student(student_id):
    for student in students:
        if student['id'] == student_id:
            deleted_name = student['name']
            students.remove(student)
            flash(f'Student "{deleted_name}" (ID: {student_id}) deleted successfully!', 'success')
            return redirect(url_for('index'))
    flash('Error: Student ID not found for deletion!', 'error')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)