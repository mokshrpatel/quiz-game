# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, session
from database import engine
from sqlalchemy import text
import secrets

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        try:
            with engine.connect() as connection:
                query = text("SELECT id, username FROM users WHERE username = :username AND password = :password")
                result = connection.execute(query, {'username': username, 'password': password})
                user = result.mappings().first()  # Get as dictionary
                
                if user:
                    session['user_id'] = user['id']
                    session['username'] = user['username']
                    flash('Logged in successfully!', 'success')
                    print(f"User {username} logged in, redirecting to dashboard")  # Debug print
                    return redirect(url_for('dashboard'))
                else:
                    flash('Invalid username or password', 'danger')
        except Exception as e:
            flash('Database error occurred', 'danger')
            print(f"Database error: {e}")
    
    return render_template('login.html')



@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('signup'))
        
        try:
            with engine.begin() as connection:  # begin() automatically commits/rollbacks
                # Check if username exists
                check_query = text("SELECT id FROM users WHERE username = :username")
                if connection.execute(check_query, {'username': username}).fetchone():
                    flash('Username already taken', 'danger')
                    return redirect(url_for('signup'))
                
                # Insert new user
                insert_query = text("INSERT INTO users (username, password) VALUES (:username, :password)")
                connection.execute(insert_query, {'username': username, 'password': password})
                
                flash('Registration successful! Please login.', 'success')
                return redirect(url_for('login'))
        except Exception as e:
            flash('Registration failed', 'danger')
            print(f"Database error: {e}")
    
    return render_template('signup.html')


@app.route('/join_quiz', methods=['POST'])
def join_quiz():
    quiz_id = request.form['quiz_id']  # Changed from quiz_code
    participant_name = request.form['name']
    
    try:
        with engine.begin() as connection:
            # Verify quiz exists
            quiz_check = text("SELECT 1 FROM question WHERE q_id = :quiz_id")
            if not connection.execute(quiz_check, {'quiz_id': quiz_id}).fetchone():
                flash('Invalid Quiz ID', 'danger')
                return redirect(url_for('login'))
            
            # Insert participant
            insert_query = text("""
                INSERT INTO participants (quiz_id, name)
                VALUES (:quiz_id, :name)
            """)
            connection.execute(insert_query, 
                             {'quiz_id': quiz_id, 
                              'name': participant_name})
            
            flash(f'Joined quiz {quiz_id} as {participant_name}', 'success')
            return redirect(url_for('quiz_interface'))
            
    except Exception as e:
        flash('Error joining quiz', 'danger')
        print(f"Database error: {e}")
        return redirect(url_for('login'))
    


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Get quizzes for the current user
    quizzes = []
    try:
        with engine.connect() as connection:
            # Query the question table for this user's quizzes
            query = text("""
                SELECT q_id as id, q_name as title 
                FROM question 
                WHERE user_id = :user_id
                ORDER BY q_id DESC
            """)
            result = connection.execute(query, {'user_id': session['user_id']})
            quizzes = [dict(row._mapping) for row in result.all()]

    except Exception as e:
        flash('Error loading quizzes', 'danger')
        print(f"Database error: {e}")
    
    return render_template('dashboard.html', 
                         username=session['username'],
                         quizzes=quizzes)



@app.route('/create_quiz', methods=['GET', 'POST'])
def create_quiz():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            with engine.begin() as connection:
                # Insert into question table
                quiz_query = text("""
                    INSERT INTO question (q_name, user_id, 
                    q1, ans1, q2, ans2, q3, ans3, q4, ans4, 
                    q5, ans5, q6, ans6, q7, ans7, q8, ans8, 
                    q9, ans9, q10, ans10)
                    VALUES (:q_name, :user_id, 
                    :q1, :ans1, :q2, :ans2, :q3, :ans3, :q4, :ans4,
                    :q5, :ans5, :q6, :ans6, :q7, :ans7, :q8, :ans8,
                    :q9, :ans9, :q10, :ans10)
                """)
                
                quiz_data = {
                    'q_name': request.form['quiz_name'],
                    'user_id': session['user_id'],
                    # Questions 1-10 and their answers
                    'q1': request.form['q1'], 'ans1': int(request.form['ans1']),
                    'q2': request.form['q2'], 'ans2': int(request.form['ans2']),
                    'q3': request.form['q3'], 'ans3': int(request.form['ans3']),
                    'q4': request.form['q4'], 'ans4': int(request.form['ans4']),
                    'q5': request.form['q5'], 'ans5': int(request.form['ans5']),
                    'q6': request.form['q6'], 'ans6': int(request.form['ans6']),
                    'q7': request.form['q7'], 'ans7': int(request.form['ans7']),
                    'q8': request.form['q8'], 'ans8': int(request.form['ans8']),
                    'q9': request.form['q9'], 'ans9': int(request.form['ans9']),
                    'q10': request.form['q10'], 'ans10': int(request.form['ans10'])
                }
                
                result = connection.execute(quiz_query, quiz_data)
                q_id = result.lastrowid
                
                # Insert into options table
                options_query = text("""
                    INSERT INTO options (q_id, 
                    o1, o2, o3, o4, o5, o6, o7, o8, o9, o10,
                    o11, o12, o13, o14, o15, o16, o17, o18, o19, o20,
                    o21, o22, o23, o24, o25, o26, o27, o28, o29, o30,
                    o31, o32, o33, o34, o35, o36, o37, o38, o39, o40)
                    VALUES (:q_id,
                    :o1, :o2, :o3, :o4, :o5, :o6, :o7, :o8, :o9, :o10,
                    :o11, :o12, :o13, :o14, :o15, :o16, :o17, :o18, :o19, :o20,
                    :o21, :o22, :o23, :o24, :o25, :o26, :o27, :o28, :o29, :o30,
                    :o31, :o32, :o33, :o34, :o35, :o36, :o37, :o38, :o39, :o40)
                """)
                
                options_data = {'q_id': q_id}
                # Add all 40 options (4 options per question × 10 questions)
                for q_num in range(1, 11):
                    for opt_num in range(1, 5):
                        key = f'q{q_num}_opt{opt_num}'
                        options_key = f'o{(q_num-1)*4 + opt_num}'
                        options_data[options_key] = request.form[key]
                
                connection.execute(options_query, options_data)
                
                flash('Quiz created successfully!', 'success')
                return redirect(url_for('dashboard'))
                
        except Exception as e:
            flash('Error creating quiz', 'danger')
            print(f"Database error: {e}")
    
    return render_template('create_quiz.html')


@app.route('/quiz/<int:quiz_id>')
def view_quiz(quiz_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        with engine.connect() as connection:
            # Get quiz questions
            questions_query = text("""
                SELECT * FROM question WHERE q_id = :quiz_id AND user_id = :user_id
            """)
            quiz = connection.execute(questions_query, 
                                    {'quiz_id': quiz_id, 'user_id': session['user_id']}).mappings().first()
            
            if not quiz:
                flash('Quiz not found', 'danger')
                return redirect(url_for('dashboard'))
            
            # Get quiz options
            options_query = text("SELECT * FROM options WHERE q_id = :quiz_id")
            options = connection.execute(options_query, {'quiz_id': quiz_id}).mappings().first()
            
            return render_template('view_quiz.html', quiz=quiz, options=options)
            
    except Exception as e:
        flash('Error loading quiz', 'danger')
        print(f"Database error: {e}")
        return redirect(url_for('dashboard'))



@app.route('/quiz/<int:quiz_id>/confirm-start')
def start_quiz_confirmation(quiz_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        with engine.connect() as connection:
            # Get quiz info
            quiz_query = text("""
                SELECT q_id as id, q_name as title 
                FROM question 
                WHERE q_id = :quiz_id AND user_id = :user_id
            """)
            quiz = connection.execute(quiz_query, 
                                   {'quiz_id': quiz_id, 'user_id': session['user_id']}).mappings().first()
            
            if not quiz:
                flash('Quiz not found', 'danger')
                return redirect(url_for('dashboard'))
            
            # Get participants who joined this quiz
            participants_query = text("""
                SELECT name, joined_at FROM participants
                WHERE quiz_id = :quiz_id
                ORDER BY joined_at DESC
            """)
            participants = connection.execute(participants_query, 
                                            {'quiz_id': quiz_id}).mappings().all()
            
            return render_template('start_confirmation.html',
                                 quiz=quiz,
                                 participants=participants)
            
    except Exception as e:
        flash('Error loading quiz confirmation', 'danger')
        print(f"Database error: {e}")
        return redirect(url_for('dashboard'))

@app.route('/quiz/<int:quiz_id>/start', methods=['POST'])
def start_quiz(quiz_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        # Here you would add logic to actually start the quiz
        # For now, we'll just flash a message
        flash(f'Quiz {quiz_id} has started!', 'success')
        return redirect(url_for('dashboard'))
    
    except Exception as e:
        flash('Error starting quiz', 'danger')
        print(f"Database error: {e}")
        return redirect(url_for('dashboard'))



@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)