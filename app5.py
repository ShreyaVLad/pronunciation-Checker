from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import speech_recognition as sr
from difflib import SequenceMatcher
import pyttsx3
import mysql.connector
import secrets

app = Flask(__name__)

app.secret_key = secrets.token_hex(16)

# Database configuration
db_host = 'localhost'
db_user = 'root'
db_password = ''
db_name = 'project'

# Helper function to connect to the database
def connect_to_db():
    return mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name)

@app.route('/')
def index():
    return render_template('welcomemain.html')

@app.route('/mainpageofmini')
def mainpageofmini():
    return render_template('mainpageofmini.html')

@app.route('/level/1')
def level1():
    return render_template('level1.html')

@app.route('/level/2')
def level2():
    return render_template('level2.html')

@app.route('/level/3')
def level3():
    return render_template('level3.html')

@app.route('/level/4')
def level4():
    return render_template('level4.html')

@app.route('/level/5')
def level5():
    return render_template('level5.html')

@app.route('/check_pronunciation', methods=['POST'])
def check_pronunciation():
    pronunciation = request.form['pronunciation'].lower()

    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("Please pronounce the words:")
        audio = recognizer.listen(source)

    try:
        user_pronunciation = recognizer.recognize_google(audio).lower()
        reference_words = pronunciation.split()
        user_words = user_pronunciation.split()

        feedback = []

        if len(reference_words) != len(user_words):
            feedback.append("Incorrect number of words. Extra words detected.")

        for ref_word, user_word in zip(reference_words, user_words):
            similarity = SequenceMatcher(None, ref_word, user_word).ratio()
            if similarity < 1.0:
                feedback.append(f"Word '{ref_word}' is not pronounced correctly. Similarity: {similarity:.2f}")

        if feedback:
            result = {"feedback": "\n".join(feedback), "status": "error"}
        else:
            result = {"feedback": "Perfect pronunciation!", "status": "success"}

        speaker = pyttsx3.init()
        speaker.say(f"The correct pronunciation is: {pronunciation}")
        speaker.runAndWait()

    except sr.UnknownValueError:
        result = {"feedback": "Sorry, could not understand audio.", "status": "error"}
    except sr.RequestError as e:
        result = {"feedback": f"Could not request results from Google Speech Recognition service; {e}", "status": "error"}

    return jsonify(result)

@app.route('/check_pronunciation1', methods=['POST'])
def check_pronunciation1():
    temp = request.get_json()
    pronunciation = temp['pronunciation']

    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("Please pronounce the words:")
        audio = recognizer.listen(source)

    try:
        user_pronunciation = recognizer.recognize_google(audio).lower()
        reference_words = pronunciation.split()
        user_words = user_pronunciation.split()

        feedback = []

        if len(reference_words) != len(user_words):
            feedback.append("Incorrect number of words. Extra words detected.")

        for ref_word, user_word in zip(reference_words, user_words):
            similarity = SequenceMatcher(None, ref_word, user_word).ratio()
            if similarity < 1.0:
                feedback.append(f"Word '{ref_word}' is not pronounced correctly. Similarity: {similarity:.2f}")

        if feedback:
            result = {"feedback": "\n".join(feedback), "status": "error"}
        else:
            result = {"feedback": "Perfect pronunciation!", "status": "success"}

        speaker = pyttsx3.init()
        speaker.say(f"The correct pronunciation is: {pronunciation}")
        speaker.runAndWait()

    except sr.UnknownValueError:
        result = {"feedback": "Sorry, could not understand audio.", "status": "error"}
    except sr.RequestError as e:
        result = {"feedback": f"Could not request results from Google Speech Recognition service; {e}", "status": "error"}

    return jsonify(result)

# Handle login and registration
@app.route('/login_registration', methods=['GET', 'POST'])
def login_registration():
    loginErrorMessage = ""
    signupErrorMessage = ""

    if request.method == 'POST':
        # Handle login logic
        if 'loginSubmit' in request.form:
            username = request.form['loginUsername']
            password = request.form['loginPassword']

            try:
                conn = connect_to_db()
                with conn.cursor(dictionary=True) as cursor:
                    login_query = "SELECT * FROM login_info WHERE Username = %s"
                    cursor.execute(login_query, (username,))
                    row = cursor.fetchone()

                    if row:
                        if password == row['Password']:
                            # Set session variable to indicate successful login
                            session['loggedin'] = True

                            # Redirect to mainpageofmini.html
                            return redirect(url_for('mainpageofmini'))
                        else:
                            loginErrorMessage = "Invalid username or password"
                    else:
                        loginErrorMessage = "Username not found"

            except mysql.connector.Error as e:
                print(f"Error: {e}")
                loginErrorMessage = 'An error occurred during login'

            finally:
                conn.close()

        # Handle registration logic
        elif 'signupSubmit' in request.form:
            first_name = request.form['signupFirstName']
            last_name = request.form['signupLastName']
            username = request.form['signupUsername']
            age = request.form['signupAge']
            password = request.form['signupPassword']
            confirm_password = request.form['confirmPassword']
        if password != confirm_password:
            signupErrorMessage = "Password and Confirm Password must be the same."
        else:
            try:
                conn = connect_to_db()
                with conn.cursor() as cursor:
                    # Check if the username already exists
                    check_username_query = "SELECT * FROM login_info WHERE Username = %s"
                    cursor.execute(check_username_query, (username,))
                    existing_user = cursor.fetchone()

                    if existing_user:
                        signupErrorMessage = "Username already exists. Choose a different username."
                    else:
                        # Insert the new user into the database
                        insert_user_query = "INSERT INTO login_info (Username, First_name, Last_name, Age, Password, Confirm_password) VALUES (%s, %s, %s, %s, %s, %s)"
                        cursor.execute(insert_user_query, (username, first_name, last_name, age, password, confirm_password))
                        conn.commit()

                        # Set session variable to indicate successful registration and login
                        session['loggedin'] = True

                        # Redirect to mainpageofmini.html
                        return redirect(url_for('mainpageofmini'))

            except mysql.connector.Error as e:
                print(f"Error: {e}")
                signupErrorMessage = "An error occurred during registration"

            finally:
                conn.close()

    return render_template('login_register.html', loginErrorMessage=loginErrorMessage, signupErrorMessage=signupErrorMessage)

if __name__ == "__main__":
    app.run(debug=True)
