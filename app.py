# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, session
from database import engine
from sqlalchemy import text
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'dbms'

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
    quiz_id = request.form['quiz_id']
    participant_name = request.form['name']
    
    try:
        with engine.begin() as connection:
            # Verify quiz exists and is active
            quiz_check = text("""
                SELECT 1 FROM question q
                JOIN quiz_sessions qs ON q.q_id = qs.quiz_id
                WHERE q.q_id = :quiz_id AND qs.is_active = TRUE
            """)
            if not connection.execute(quiz_check, {'quiz_id': quiz_id}).fetchone():
                flash('Invalid Quiz ID or quiz not active', 'danger')
                return redirect(url_for('login'))
            
            # Insert participant
            insert_query = text("""
                INSERT INTO participants (quiz_id, name)
                VALUES (:quiz_id, :name)
            """)
            connection.execute(insert_query, 
                             {'quiz_id': quiz_id, 
                              'name': participant_name})
            
            return redirect(url_for('participate_quiz', quiz_id=quiz_id, name=participant_name))
            
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
        with engine.begin() as connection:
            # Verify the quiz belongs to the current user
            verify_query = text("""
                SELECT 1 FROM question 
                WHERE q_id = :quiz_id AND user_id = :user_id
            """)
            if not connection.execute(verify_query, 
                                   {'quiz_id': quiz_id, 
                                    'user_id': session['user_id']}).fetchone():
                flash('Quiz not found', 'danger')
                return redirect(url_for('dashboard'))
            
            # Create a new quiz session
            session_query = text("""
                INSERT INTO quiz_sessions (quiz_id, is_active, start_time)
                VALUES (:quiz_id, TRUE, NOW())
            """)
            connection.execute(session_query, {'quiz_id': quiz_id})
            
            flash('Quiz started successfully!', 'success')
            return redirect(url_for('host_quiz', quiz_id=quiz_id))
            
    except Exception as e:
        flash('Error starting quiz', 'danger')
        print(f"Database error: {e}")
        return redirect(url_for('dashboard'))

# new
@app.route('/quiz/<int:quiz_id>/host')
def host_quiz(quiz_id):
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
            
            # Create or get quiz session
            session_query = text("""
                INSERT INTO quiz_sessions (quiz_id, is_active, start_time)
                VALUES (:quiz_id, TRUE, NOW())
                ON DUPLICATE KEY UPDATE is_active=TRUE
            """)
            connection.execute(session_query, {'quiz_id': quiz_id})
            
            # Get participants
            participants_query = text("""
                SELECT name, joined_at FROM participants
                WHERE quiz_id = :quiz_id
                ORDER BY joined_at DESC
            """)
            participants = connection.execute(participants_query, 
                                           {'quiz_id': quiz_id}).mappings().all()
            
            return render_template('host_quiz.html',
                                quiz=quiz,
                                participants=participants)
            
    except Exception as e:
        flash('Error starting quiz session', 'danger')
        print(f"Database error: {e}")
        return redirect(url_for('dashboard'))

# @app.route('/quiz/<int:quiz_id>/participate')
# def participate_quiz(quiz_id):
#     try:
#         with engine.connect() as connection:
#             # Verify quiz exists and is active
#             quiz_query = text("""
#                 SELECT q.q_id as id, q.q_name as title, qs.is_active
#                 FROM question q
#                 LEFT JOIN quiz_sessions qs ON q.q_id = qs.quiz_id
#                 WHERE q.q_id = :quiz_id
#             """)
#             quiz = connection.execute(quiz_query, 
#                                    {'quiz_id': quiz_id}).mappings().first()
            
#             if not quiz:
#                 flash('Quiz not found', 'danger')
#                 return redirect(url_for('login'))
            
#             if not quiz['is_active']:
#                 flash('Quiz is not active', 'danger')
#                 return redirect(url_for('login'))
            
#             # Get current question
#             session_query = text("""
#                 SELECT current_question FROM quiz_sessions
#                 WHERE quiz_id = :quiz_id
#             """)
#             session_info = connection.execute(session_query, 
#                                            {'quiz_id': quiz_id}).mappings().first()
            
#             current_question = session_info['current_question'] if session_info else 1
            
#             # Get question and options
#             question_query = text("""
#                 SELECT q{q_num} as question, ans{q_num} as correct_answer
#                 FROM question
#                 WHERE q_id = :quiz_id
#             """.format(q_num=current_question))
#             question = connection.execute(question_query, 
#                                        {'quiz_id': quiz_id}).mappings().first()
            
#             options_query = text("""
#                 SELECT o{start}, o{start+1}, o{start+2}, o{start+3}
#                 FROM options
#                 WHERE q_id = :quiz_id
#             """.format(start=(current_question-1)*4 + 1))
#             options = connection.execute(options_query, 
#                                        {'quiz_id': quiz_id}).mappings().first()
            
#             return render_template('participate_quiz.html',
#                                 quiz=quiz,
#                                 question_num=current_question,
#                                 question=question['question'],
#                                 options=[options[f'o{(current_question-1)*4 + 1}'],
#                                          options[f'o{(current_question-1)*4 + 2}'],
#                                          options[f'o{(current_question-1)*4 + 3}'],
#                                          options[f'o{(current_question-1)*4 + 4}']],
#                                 correct_answer=question['correct_answer'])
            
#     except Exception as e:
#         flash('Error joining quiz', 'danger')
#         print(f"Database error: {e}")
#         return redirect(url_for('login'))

@app.route('/quiz/<int:quiz_id>/next', methods=['POST'])
def next_question(quiz_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        with engine.begin() as connection:
            # Update to next question
            update_query = text("""
                UPDATE quiz_sessions
                SET current_question = current_question + 1
                WHERE quiz_id = :quiz_id
            """)
            connection.execute(update_query, {'quiz_id': quiz_id})
            
            flash('Moved to next question', 'success')
            return redirect(url_for('host_quiz', quiz_id=quiz_id))
            
    except Exception as e:
        flash('Error moving to next question', 'danger')
        print(f"Database error: {e}")
        return redirect(url_for('dashboard'))


@app.route('/quiz/<int:quiz_id>/submit', methods=['POST'])
def submit_answer(quiz_id):
    if 'name' not in request.form or 'answer' not in request.form:
        flash('Missing required form data', 'danger')
        return redirect(url_for('login'))

    try:
        with engine.begin() as connection:
            # 1. Verify quiz session is active
            session_query = text("""
                SELECT qs.session_id, qs.current_question, q.ans{current_q} as correct_answer
                FROM quiz_sessions qs
                JOIN question q ON qs.quiz_id = q.q_id
                WHERE qs.quiz_id = :quiz_id 
                AND qs.is_active = TRUE
            """.format(current_q=request.form.get('question_num', 1)))
            
            session_data = connection.execute(session_query,
                                           {'quiz_id': quiz_id}).mappings().first()
            
            if not session_data:
                flash('Quiz session not found or not active', 'danger')
                return redirect(url_for('login'))

            # 2. Get or create participant
            participant_query = text("""
                INSERT INTO participants (quiz_id, name)
                VALUES (:quiz_id, :name)
                ON DUPLICATE KEY UPDATE name=name
                RETURNING id
            """)
            participant = connection.execute(participant_query,
                                          {'quiz_id': quiz_id,
                                           'name': request.form['name']}).mappings().first()

            # 3. Check if answer was already submitted
            existing_response = connection.execute(
                text("""
                    SELECT 1 FROM participant_responses
                    WHERE participant_id = :participant_id
                    AND question_num = :question_num
                """),
                {'participant_id': participant['id'],
                 'question_num': session_data['current_question']}
            ).fetchone()

            if existing_response:
                flash('Answer already submitted for this question', 'info')
                return redirect(url_for('participate_quiz',
                                      quiz_id=quiz_id,
                                      name=request.form['name']))

            # 4. Calculate score (10 for correct, 0 for wrong)
            is_correct = int(request.form['answer']) == session_data['correct_answer']
            score = 10 if is_correct else 0

            # 5. Record response
            response_query = text("""
                INSERT INTO participant_responses
                (session_id, participant_id, question_num, 
                 selected_option, is_correct, score, response_time)
                VALUES (:session_id, :participant_id, :question_num,
                        :selected_option, :is_correct, :score, NOW())
            """)
            connection.execute(response_query, {
                'session_id': session_data['session_id'],
                'participant_id': participant['id'],
                'question_num': session_data['current_question'],
                'selected_option': int(request.form['answer']),
                'is_correct': is_correct,
                'score': score
            })

            # 6. Calculate current total score
            total_score_query = text("""
                SELECT COALESCE(SUM(score), 0) as total
                FROM participant_responses
                WHERE participant_id = :participant_id
            """)
            total_score = connection.execute(total_score_query,
                                           {'participant_id': participant['id']}).mappings().first()

            flash('Answer submitted successfully!', 'success')
            return redirect(url_for('participate_quiz',
                                  quiz_id=quiz_id,
                                  name=request.form['name'],
                                  current_score=total_score['total']))

    except Exception as e:
        flash(f'Error submitting answer: {str(e)}', 'danger')
        print(f"Database error: {e}")
        return redirect(url_for('login'))

# @app.route('/quiz/<int:quiz_id>/scores')
# def show_scores(quiz_id):
#     try:
#         with engine.connect() as connection:
#             # Get total scores for each participant
#             scores_query = text("""
#                 SELECT p.name, SUM(pr.score) as total_score
#                 FROM participant_responses pr
#                 JOIN participants p ON pr.participant_id = p.id
#                 JOIN quiz_sessions qs ON pr.session_id = qs.session_id
#                 WHERE qs.quiz_id = :quiz_id
#                 GROUP BY p.name
#                 ORDER BY total_score DESC
#             """)
#             scores = connection.execute(scores_query, 
#                                       {'quiz_id': quiz_id}).mappings().all()
            
#             return render_template('scores.html',
#                                  quiz_id=quiz_id,
#                                  scores=scores)
            
#     except Exception as e:
#         flash('Error retrieving scores', 'danger')
#         print(f"Database error: {e}")
#         return redirect(url_for('login'))    

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)