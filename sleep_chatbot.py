# app.py - Sleep Hygiene Dashboard with Chatbot (Fixed Version)
import dash
from dash import dcc, html, Input, Output, State, callback, no_update
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
import dash_daq as daq
from datetime import datetime
import random
import json

# =============================================
# DATABASE CONFIGURATION
# =============================================
hostName = "localhost"
dbUser = "root"
dbPassword = ""  # Add your MySQL password if set
dbName = "sleep_hygiene"

# =============================================
# APP INITIALIZATION
# =============================================
app = dash.Dash(__name__, 
               external_stylesheets=[dbc.themes.FLATLY],
               suppress_callback_exceptions=True)
app.title = "Sleep Hygiene Dashboard"
server = app.server


# =============================================
# CHATBOT KNOWLEDGE BASE (ENHANCED)
# =============================================
sleep_advice = {
    "general_tips": [
        "Maintain a consistent sleep schedule, even on weekends",
        "Create a relaxing bedtime routine (reading, meditation, warm bath)",
        "Make your bedroom quiet, dark, and cool (18-24°C)",
        "Avoid caffeine, alcohol, and large meals before bedtime",
        "Get regular exercise but not too close to bedtime",
        "Limit screen time 1 hour before bed - blue light disrupts melatonin",
        "Try relaxation techniques like deep breathing or progressive muscle relaxation",
        "Use your bed only for sleep and intimacy to strengthen the mental association",
        "If you can't sleep, get up and do something relaxing until you feel sleepy",
        "Consider keeping a sleep diary to track patterns and improvements"
    ],
    "score_analysis": {
        "90-100": {
            "rating": "Excellent",
            "message": "Your sleep habits are outstanding! Keep maintaining these healthy routines.",
            "tip": "Consider sharing your strategies with others who struggle with sleep."
        },
        "80-90": {
            "rating": "Very Good",
            "message": "You have great sleep habits with just minor areas for refinement.",
            "tip": "Focus on consistency - try to keep the same schedule every day."
        },
        "70-80": {
            "rating": "Good",
            "message": "Your sleep is decent but could benefit from some improvements.",
            "tip": "Identify your weakest area (duration, disturbances, etc.) and focus there."
        },
        "50-70": {
            "rating": "Fair",
            "message": "Your sleep quality needs attention in several areas.",
            "tip": "Start with one or two key changes like setting a fixed wake-up time."
        },
        "0-50": {
            "rating": "Poor",
            "message": "Your sleep quality is significantly impacting your health and wellbeing.",
            "tip": "Consider consulting a sleep specialist if problems persist after making changes."
        }
    },
    "qa": {
        "ideal sleep duration": {
            "answer": "Most adults need 7-9 hours of sleep per night. Teenagers need 8-10 hours, and older adults (65+) may need 7-8 hours.",
            "followup": "The exact amount varies by individual. You know you're getting enough if you wake up feeling refreshed."
        },
        "best temperature": {
            "answer": "The ideal bedroom temperature is between 18-24°C (65-75°F). Cooler temperatures signal your body it's time to sleep.",
            "followup": "Experiment within this range to find your personal ideal temperature."
        },
        "reduce disturbances": {
            "answer": "Try these disturbance reducers:\n- White noise machines or earplugs for noise\n- Blackout curtains or sleep mask for light\n- Comfortable, breathable bedding\n- Keeping pets out of the bedroom if they disrupt sleep",
            "followup": "Even small improvements to your sleep environment can make a big difference."
        },
        "fall asleep faster": {
            "answer": "To fall asleep faster:\n1. Establish a relaxing pre-sleep routine\n2. Avoid screens before bed\n3. Try the 4-7-8 breathing technique\n4. Use visualization or progressive muscle relaxation\n5. Get out of bed if not asleep in 20 minutes",
            "followup": "Consistency is key - practice these techniques regularly."
        },
        "sleep tracking benefits": {
            "answer": "Sleep tracking helps you:\n- Identify patterns in your sleep habits\n- Understand how behaviors affect sleep quality\n- Measure improvements from changes you make\n- Recognize sleep disorders that may need professional help",
            "followup": "But don't become obsessed with the numbers - how you feel matters most."
        },
        "naps": {
            "answer": "Short naps (20-30 minutes) can be refreshing without affecting nighttime sleep. Avoid napping after 3pm and keep naps under 1 hour.",
            "followup": "If you have insomnia, it's often better to avoid naps altogether."
        },
        "insomnia": {
            "answer": "For insomnia:\n1. Maintain a consistent sleep schedule\n2. Create a comfortable sleep environment\n3. Limit caffeine and alcohol\n4. Manage stress through relaxation techniques\n5. Consider cognitive behavioral therapy for insomnia (CBT-I)",
            "followup": "If insomnia persists more than a few weeks, consult a healthcare provider."
        },
        "alcohol": {
            "answer": "Alcohol may help you fall asleep but reduces sleep quality. It disrupts REM sleep and can cause nighttime awakenings. Avoid alcohol within 3 hours of bedtime.",
            "followup": "Even small amounts can affect sleep architecture."
        },
        "caffeine": {
            "answer": "Caffeine can stay in your system for 6-8 hours. Avoid caffeine after 2pm or at least 6 hours before bedtime. Some people are more sensitive and need to cut off earlier.",
            "followup": "Remember caffeine is in coffee, tea, chocolate, soda, and some medications."
        },
        "sleep positions": {
            "answer": "Best sleep positions:\n- Back: Best for spine alignment, may reduce acid reflux\n- Side: Good for snorers and sleep apnea, helps digestion\n- Stomach: Generally not recommended as it strains neck and back",
            "followup": "Use pillows to support your preferred position - between knees for side sleepers, under knees for back sleepers."
        },
        "melatonin": {
            "answer": "Melatonin is a hormone that regulates sleep-wake cycles. Supplements may help with jet lag or shift work but aren't a long-term solution. Typical dose is 0.5-5mg taken 1-2 hours before bedtime.",
            "followup": "Consult your doctor before using melatonin, especially if taking other medications."
        },
        "sleep apnea": {
            "answer": "Sleep apnea symptoms include loud snoring, gasping for air, daytime sleepiness, and morning headaches. Risk factors include obesity, large neck size, and family history. Treatment may involve CPAP machines, oral devices, or lifestyle changes.",
            "followup": "If you suspect sleep apnea, see a sleep specialist for evaluation."
        },
        "dreams": {
            "answer": "Dreams occur during REM sleep. Remembering dreams varies by person. More vivid dreams may occur during stress, pregnancy, or with certain medications. Nightmares may indicate stress or trauma.",
            "followup": "Keeping a dream journal can help identify patterns or stressors."
        },
        "exercise": {
            "answer": "Regular exercise improves sleep quality but timing matters:\n- Morning/afternoon exercise is ideal\n- Evening exercise should finish 2-3 hours before bed\n- Gentle yoga or stretching before bed can be relaxing",
            "followup": "Even light activity like walking can improve sleep."
        },
        "mattress": {
            "answer": "Choose a mattress based on:\n1. Sleeping position\n2. Body type and weight\n3. Personal comfort preferences\n4. Support needs (back pain, etc.)\nReplace every 7-10 years or when uncomfortable.",
            "followup": "Test mattresses in store if possible - what feels good for 5 minutes may not work all night."
        },
        "clock watching": {
            "answer": "Clock watching increases sleep anxiety. Turn clocks away from view or remove them from the bedroom. If you wake at night, avoid checking the time.",
            "followup": "Trust your body's internal clock rather than constantly monitoring time."
        },
        "shift work": {
            "answer": "For shift workers:\n- Maintain a consistent sleep schedule even on days off\n- Use blackout curtains and white noise for daytime sleep\n- Limit caffeine in the second half of your shift\n- Take strategic naps when possible\n- Consider melatonin under medical supervision",
            "followup": "It may take several weeks to adjust to a new shift schedule."
        },
        "jet lag": {
            "answer": "To minimize jet lag:\n- Adjust your sleep schedule before traveling\n- Stay hydrated and avoid alcohol during flight\n- Seek sunlight at destination to reset circadian rhythm\n- Consider melatonin for eastward travel\n- Allow 1 day recovery per time zone crossed",
            "followup": "Eastward travel (losing time) is typically harder to adjust to than westward."
        },
        "pregnancy": {
            "answer": "During pregnancy:\n- Sleep on your side (especially left) improves circulation\n- Use pillows for support between knees and under belly\n- Elevate head slightly to reduce heartburn\n- Practice relaxation techniques for comfort",
            "followup": "Frequent urination and discomfort are common - limit fluids before bed and nap when possible."
        },
        "aging": {
            "answer": "Sleep changes with age:\n- Total sleep time may decrease\n- More nighttime awakenings\n- Earlier bedtimes and wake times\n- Reduced deep sleep\nMaintain good sleep habits and consult a doctor if sleep problems affect quality of life.",
            "followup": "Older adults still need 7-8 hours of sleep - the 'need less sleep with age' myth isn't true."
        }
    }
}

# =============================================
# DATABASE FUNCTIONS
# =============================================
def get_db_connection():
    return mysql.connector.connect(
        host=hostName,
        user=dbUser,
        password=dbPassword,
        database=dbName
    )

def setup_db():
    try:
        # Connect without specifying database first
        conn = mysql.connector.connect(
            host=hostName,
            user=dbUser,
            password=dbPassword
        )
        cursor = conn.cursor()
        
        # Drop database if exists (to start fresh)
        cursor.execute(f"DROP DATABASE IF EXISTS {dbName}")
        
        # Create database
        cursor.execute(f"CREATE DATABASE {dbName}")
        cursor.execute(f"USE {dbName}")
        
        # Create users table
        cursor.execute("""
        CREATE TABLE users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            email VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB
        """)
        
        # Create sleep_records table with proper foreign key
        cursor.execute("""
        CREATE TABLE sleep_records (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            sleep_hours FLOAT NOT NULL,
            disturbances INT NOT NULL,
            temperature FLOAT NOT NULL,
            light_exposure VARCHAR(10) NOT NULL,
            noise_level VARCHAR(10) NOT NULL,
            sleep_score INT NOT NULL,
            record_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        ) ENGINE=InnoDB
        """)
        
        # Create chatbot_conversations table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS chatbot_conversations (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            message TEXT NOT NULL,
            response TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        ) ENGINE=InnoDB
        """)
        
        conn.commit()
        print("✅ Database setup completed successfully")
        
    except mysql.connector.Error as err:
        print(f"❌ Database error: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()

# Initialize database
setup_db()

# =============================================
# CHATBOT FUNCTIONS (FIXED)
# =============================================
# =============================================
# CHATBOT FUNCTIONS (ENHANCED)
# =============================================
def get_chatbot_response(user_message, username=None, sleep_data=None):
    """Generate appropriate response based on user message with enhanced capabilities"""
    user_message = user_message.lower().strip()
    
    # Check for greetings
    if any(word in user_message for word in ["hi", "hello", "hey", "greetings"]):
        greeting = random.choice([
            "Hello! I'm your Sleep Assistant. How can I help you with your sleep today?",
            "Hi there! Ready to improve your sleep? What would you like to know?",
            "Greetings! I'm here to help with all your sleep-related questions."
        ])
        return greeting
    
    # Check for thanks
    if any(word in user_message for word in ["thanks", "thank you", "appreciate"]):
        return random.choice([
            "You're welcome! Let me know if you have any other sleep questions.",
            "Happy to help! Sweet dreams!",
            "Glad I could assist. Sleep well!"
        ])
    
    # Check for sleep score analysis request
    if any(phrase in user_message for phrase in ["analyze my sleep", "my sleep score", "how did i sleep", "sleep analysis"]):
        if not sleep_data:
            return "I need your sleep data to analyze. Please submit a sleep entry first."
        
        try:
            # Safely convert string to dict if needed
            if isinstance(sleep_data, str):
                sleep_data = json.loads(sleep_data.replace("'", "\""))
            
            score = sleep_data.get('sleep_score', 0)
            hours = sleep_data.get('sleep_hours', 0)
            disturbances = sleep_data.get('disturbances', 0)
            temp = sleep_data.get('temperature', 0)
            light = sleep_data.get('light_exposure', 'no')
            noise = sleep_data.get('noise_level', 'no')
            
            analysis = []
            
            # Find the appropriate score range
            score_range = None
            for range_str, info in sleep_advice["score_analysis"].items():
                low, high = map(int, range_str.split('-'))
                if low <= score <= high:
                    score_range = info
                    break
            
            if score_range:
                analysis.append(f"📊 Your sleep score is {score} - {score_range['rating']}")
                analysis.append(f"💡 {score_range['message']}")
                analysis.append(f"🌟 Tip: {score_range['tip']}")
            else:
                analysis.append(f"Your sleep score is {score}. Let's look at the details.")
            
            # Detailed analysis sections
            analysis.append("\n🔍 Detailed Analysis:")
            
            # Hours analysis
            if hours < 6:
                analysis.append(f"⏳ Sleep Duration: Only {hours} hours (very low) - Adults typically need 7-9 hours")
            elif hours < 7:
                analysis.append(f"⏳ Sleep Duration: {hours} hours (moderate) - Aim for at least 7 hours")
            else:
                analysis.append(f"⏳ Sleep Duration: {hours} hours (excellent) - Great job!")
            
            # Disturbances analysis
            if disturbances == 0:
                analysis.append("🌙 Disturbances: None reported - Perfect sleep environment!")
            elif disturbances <= 2:
                analysis.append(f"🌙 Disturbances: {disturbances} (mild) - Your sleep was slightly interrupted")
            elif disturbances <= 5:
                analysis.append(f"🌙 Disturbances: {disturbances} (moderate) - Consider ways to reduce interruptions")
            else:
                analysis.append(f"🌙 Disturbances: {disturbances} (severe) - This significantly impacts sleep quality")
            
            # Temperature analysis
            if 18 <= temp <= 24:
                analysis.append(f"🌡️ Temperature: {temp}°C (ideal) - Perfect range for sleep")
            else:
                analysis.append(f"🌡️ Temperature: {temp}°C (suboptimal) - Try to keep between 18-24°C")
            
            # Light exposure
            if light == 'yes':
                analysis.append("💡 Light Exposure: Yes (problematic) - Light disrupts melatonin production")
            else:
                analysis.append("💡 Light Exposure: No (good) - Darkness promotes better sleep")
            
            # Noise level
            if noise == 'yes':
                analysis.append("🔊 Noise Level: Yes (problematic) - Consider white noise or earplugs")
            else:
                analysis.append("🔊 Noise Level: No (good) - Quiet environments improve sleep quality")
            
            # Add personalized recommendations
            analysis.append("\n🎯 Personalized Recommendations:")
            
            if hours < 7:
                analysis.append("- Prioritize getting at least 7 hours of sleep")
            
            if disturbances > 2:
                analysis.append("- Identify sources of disturbances and eliminate them")
                if noise == 'yes':
                    analysis.append("  - Try white noise or earplugs to mask external sounds")
                if light == 'yes':
                    analysis.append("  - Use blackout curtains or a sleep mask")
            
            if temp < 18 or temp > 24:
                analysis.append(f"- Adjust room temperature closer to 21°C (currently {temp}°C)")
            
            # Add general tips
            analysis.append("\n💡 General Sleep Tips:")
            analysis.extend(random.sample(sleep_advice["general_tips"], 3))
            
            return "\n".join(analysis)
        except Exception as e:
            print(f"Error analyzing sleep data: {e}")
            return "Sorry, I had trouble analyzing your sleep data. Please try again."
    
    # Check for specific questions
    for question, info in sleep_advice["qa"].items():
        if question in user_message:
            response = info["answer"]
            if "followup" in info:
                response += "\n\n" + info["followup"]
            return response
    
    # Check for related terms if exact match not found
    related_responses = []
    for topic, info in sleep_advice["qa"].items():
        if topic in user_message or any(word in user_message for word in topic.split()):
            related_responses.append(f"About {topic.replace('_', ' ')}:\n{info['answer']}")
    
    if related_responses:
        return "\n\n".join(related_responses[:3])  # Return up to 3 related responses
    
    # Default response
    return ("I'm here to help with sleep-related questions. You can ask me about:\n"
            "- Ideal sleep duration\n- Best bedroom temperature\n- Reducing disturbances\n- Sleep tracking benefits\n"
            "- Naps\n- Insomnia\n- Caffeine and alcohol effects\n- Sleep positions\n- Melatonin\n"
            "- Sleep apnea\n- Dreams\n- Exercise timing\n- Mattress selection\n- Shift work tips\n"
            "- Jet lag\n- Pregnancy sleep\n- Aging and sleep\n\n"
            "Or ask me to 'analyze my sleep' after submitting your sleep data.")
def save_chat_message(user_id, message, response):
    """Save conversation to database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO chatbot_conversations 
            (user_id, message, response)
            VALUES (%s, %s, %s)
        """, (user_id, message, response))
        conn.commit()
    except mysql.connector.Error as err:
        print(f"❌ Error saving chat message: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()

# =============================================
# AUTHENTICATION FUNCTIONS
# =============================================
def create_user(username, password, email=None):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if username exists
        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        if cursor.fetchone():
            print(f"⚠️ Username {username} already exists")
            return False
        
        # Create new user
        cursor.execute(
            "INSERT INTO users (username, password, email) VALUES (%s, %s, %s)",
            (username, generate_password_hash(password), email)
        )
        conn.commit()
        print(f"✅ User {username} created successfully")
        return True
    except mysql.connector.Error as err:
        print(f"❌ Error creating user: {err}")
        return False
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()

def verify_user(username, password):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
        result = cursor.fetchone()
        return result and check_password_hash(result[0], password)
    except mysql.connector.Error as err:
        print(f"❌ Login error: {err}")
        return False
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()

def get_user_id(username):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        result = cursor.fetchone()
        return result[0] if result else None
    except mysql.connector.Error as err:
        print(f"❌ Error getting user ID: {err}")
        return None
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()

# =============================================
# SLEEP ANALYSIS FUNCTIONS (IMPROVED)
# =============================================
def analyze_sleep(data):
    sleep_score = 100
    
    # Score adjustments based on sleep quality factors
    if data['sleep_hours'] < 6:
        sleep_score -= 30
    elif data['sleep_hours'] < 7:
        sleep_score -= 15
        
    if data['disturbances'] > 2:
        sleep_score -= data['disturbances'] * 5
        
    if data['temperature'] < 18 or data['temperature'] > 24:
        sleep_score -= 10
        
    if data['light_exposure'] == 'yes':
        sleep_score -= 20
        
    if data['noise_level'] == 'yes':
        sleep_score -= 15
        
    return max(sleep_score, 0)  # Ensure score doesn't go below 0

def save_sleep_record(user_id, data, score):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO sleep_records 
            (user_id, sleep_hours, disturbances, temperature, 
             light_exposure, noise_level, sleep_score)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            user_id,
            data['sleep_hours'],
            data['disturbances'],
            data['temperature'],
            data['light_exposure'],
            data['noise_level'],
            score
        ))
        conn.commit()
        print("✅ Sleep record saved successfully")
    except mysql.connector.Error as err:
        print(f"❌ Error saving sleep record: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()

def get_user_records(user_id, limit=None):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT * FROM sleep_records 
            WHERE user_id = %s 
            ORDER BY record_date DESC
        """
        if limit:
            query += f" LIMIT {limit}"
        cursor.execute(query, (user_id,))
        return cursor.fetchall()
    except mysql.connector.Error as err:
        print(f"❌ Error getting records: {err}")
        return []
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()

# =============================================
# APP LAYOUT (IMPROVED)
# =============================================
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content'),
    dcc.Store(id='auth-status', storage_type='session', data='logged-out'),
    dcc.Store(id='current-user', storage_type='session'),
    dcc.Store(id='sleep-data-store', storage_type='session')  # Store sleep data for callbacks
])

# Login Page Layout
login_layout = html.Div([
    dbc.Container([
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H1("Sleep Hygiene Dashboard", className="text-center mb-4"),
                    html.P("Track and improve your sleep quality", className="text-center text-muted mb-5"),
                    
                    dbc.Tabs([
                        # Login Tab
                        dbc.Tab([
                            html.Div([
                                dbc.Input(id="login-username", placeholder="Username", 
                                         type="text", className="mb-3"),
                                dbc.Input(id="login-password", placeholder="Password", 
                                         type="password", className="mb-3"),
                                dbc.Button("Login", id="login-button", 
                                          color="primary", className="w-100 mb-3"),
                                html.Div(id="login-feedback")
                            ], className="p-4")
                        ], label="Login", tab_id="login"),
                        
                        # Signup Tab
                        dbc.Tab([
                            html.Div([
                                dbc.Input(id="signup-username", placeholder="Username", 
                                         type="text", className="mb-3"),
                                dbc.Input(id="signup-email", placeholder="Email (optional)", 
                                         type="email", className="mb-3"),
                                dbc.Input(id="signup-password", placeholder="Password", 
                                         type="password", className="mb-3"),
                                dbc.Input(id="signup-confirm", placeholder="Confirm Password", 
                                         type="password", className="mb-3"),
                                dbc.Button("Sign Up", id="signup-button", 
                                          color="success", className="w-100 mb-3"),
                                html.Div(id="signup-feedback")
                            ], className="p-4")
                        ], label="Sign Up", tab_id="signup")
                    ], id="auth-tabs", active_tab="login")
                ], className="auth-box")
            ], md=6, className="mx-auto")
        ], className="align-items-center", style={'height': '100vh'})
    ], fluid=True)
], style={'backgroundColor': '#f8f9fa', 'height': '100vh'})

# Dashboard Layout
def create_dashboard_layout(username):
    user_id = get_user_id(username)
    records = get_user_records(user_id)
    latest_record = records[0] if records else None
    
    return html.Div([
        # Navigation Bar
        dbc.Navbar(
            [
                html.A(
                    dbc.Row([
                        dbc.Col(html.I(className="fas fa-moon mr-2")),
                        dbc.Col(dbc.NavbarBrand("Sleep Dashboard")),
                    ], align="center", className="g-0"),
                    href="#", style={"textDecoration": "none"}
                ),
                dbc.Nav([
                    dbc.NavItem(dbc.NavLink("New Entry", href="#new-entry")),
                    dbc.NavItem(dbc.NavLink("History", href="#history")),
                    dbc.NavItem(dbc.NavLink("Trends", href="#trends")),
                    dbc.NavItem(dbc.NavLink(f"Welcome, {username}", disabled=True)),
                    dbc.NavItem(dbc.NavLink("Logout", id="logout-link", href="/logout")),
                ], className="ml-auto", navbar=True)
            ],
            color="primary",
            dark=True,
            sticky="top"
        ),
        
        # Main Content
        dbc.Container([
            dbc.Row([
                # Left Column (Input Form and Chatbot)
                dbc.Col([
                    # Input Form Card
                    dbc.Card([
                        dbc.CardHeader("New Sleep Entry", className="bg-primary text-white"),
                        dbc.CardBody([
                            dbc.Form([
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Label("Sleep Hours"),
                                        dbc.Input(id="sleep-hours", type="number", 
                                                 min=0, max=24, step=0.5, value=7.5),
                                    ], md=6),
                                    dbc.Col([
                                        dbc.Label("Disturbances"),
                                        dbc.Input(id="disturbances", type="number", 
                                                 min=0, max=20, value=0),
                                    ], md=6),
                                ], className="mb-3"),
                                
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Label("Room Temperature (°C)"),
                                        daq.Slider(
                                            id="temperature",
                                            min=10,
                                            max=30,
                                            value=21,
                                            marks={i: str(i) for i in range(10, 31, 5)},
                                            color="#007BFF"
                                        ),
                                    ], md=12),
                                ], className="mb-3"),
                                
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Label("Light Exposure During Sleep"),
                                        dbc.RadioItems(
                                            id="light-exposure",
                                            options=[
                                                {"label": "Yes", "value": "yes"},
                                                {"label": "No", "value": "no"},
                                            ],
                                            value="no",
                                            inline=True,
                                        ),
                                    ], md=6),
                                    dbc.Col([
                                        dbc.Label("Noise Disturbance"),
                                        dbc.RadioItems(
                                            id="noise-level",
                                            options=[
                                                {"label": "Yes", "value": "yes"},
                                                {"label": "No", "value": "no"},
                                            ],
                                            value="no",
                                            inline=True,
                                        ),
                                    ], md=6),
                                ], className="mb-4"),
                                
                                dbc.Button("Submit", id="submit-button", 
                                          color="primary", className="w-100"),
                            ]),
                        ]),
                    ], className="mb-4"),
                    
                    # Chatbot Card
                    dbc.Card([
                        dbc.CardHeader("Sleep Assistant", className="bg-info text-white"),
                        dbc.CardBody([
                            html.Div(id="chat-messages", style={
                                "height": "300px",
                                "overflowY": "scroll",
                                "marginBottom": "15px",
                                "border": "1px solid #eee",
                                "padding": "10px",
                                "borderRadius": "5px",
                                "backgroundColor": "#f8f9fa"
                            }),
                            dbc.InputGroup([
                                dbc.Input(id="chat-input", placeholder="Ask about sleep...", type="text",
                                         style={"flex": "1"}),
                                dbc.Button("Send", id="chat-send", color="primary"),
                            ], style={"width": "100%"}),
                        ]),
                    ]),
                ], md=4),
                
                # Right Column (Analysis and Visualizations)
                dbc.Col([
                    # Sleep Score Card
                    dbc.Card([
                        dbc.CardHeader("Sleep Score", className="bg-success text-white"),
                        dbc.CardBody([
                            html.Div(id="sleep-score-display", className="text-center"),
                            html.Div(id="recommendations", className="mt-3"),
                        ]),
                    ], className="mb-4"),
                    
                    # Sleep History Card
                    dbc.Card([
                        dbc.CardHeader("Sleep History", className="bg-info text-white"),
                        dbc.CardBody([
                            dcc.Graph(id="sleep-history-chart"),
                        ]),
                    ]),
                    
                    # Trends Card
                    dbc.Card([
                        dbc.CardHeader("Sleep Trends", className="bg-warning text-white"),
                        dbc.CardBody([
                            dcc.Graph(id="sleep-trends-chart"),
                        ]),
                    ], className="mt-4"),
                ], md=8),
            ]),
        ], fluid=True, className="mt-3"),
    ])

# =============================================
# CALLBACKS (IMPROVED)
# =============================================
# Route between login and dashboard
@callback(
    Output('page-content', 'children'),
    Output('auth-status', 'data', allow_duplicate=True),
    Output('current-user', 'data', allow_duplicate=True),
    Input('url', 'pathname'),
    State('auth-status', 'data'),
    State('current-user', 'data'),
    prevent_initial_call=True
)
def display_page(pathname, auth_status, current_user):
    if pathname == '/logout':
        return login_layout, 'logged-out', None
    
    if pathname == '/dashboard' or auth_status == 'logged-in':
        if current_user:
            return create_dashboard_layout(current_user), 'logged-in', current_user
    
    return login_layout, 'logged-out', None

# Handle authentication (login/signup)
@callback(
    Output('url', 'pathname', allow_duplicate=True),
    Output('auth-status', 'data', allow_duplicate=True),
    Output('current-user', 'data', allow_duplicate=True),
    Output('login-feedback', 'children'),
    Output('signup-feedback', 'children'),
    Input('login-button', 'n_clicks'),
    Input('signup-button', 'n_clicks'),
    State('login-username', 'value'),
    State('login-password', 'value'),
    State('signup-username', 'value'),
    State('signup-password', 'value'),
    State('signup-email', 'value'),
    State('signup-confirm', 'value'),
    prevent_initial_call=True
)
def handle_auth(login_clicks, signup_clicks, login_user, login_pass, 
               signup_user, signup_pass, signup_email, signup_confirm):
    ctx = dash.callback_context
    if not ctx.triggered:
        return no_update, no_update, no_update, no_update, no_update
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if trigger_id == 'login-button':
        if not login_user or not login_pass:
            return no_update, no_update, no_update, dbc.Alert("Please enter both username and password", color="danger"), no_update
        
        if verify_user(login_user, login_pass):
            return '/dashboard', 'logged-in', login_user, no_update, no_update
        else:
            return no_update, no_update, no_update, dbc.Alert("Invalid username or password", color="danger"), no_update
    
    elif trigger_id == 'signup-button':
        if not signup_user or not signup_pass:
            return no_update, no_update, no_update, no_update, dbc.Alert("Username and password are required", color="danger")
        
        if len(signup_pass) < 8:
            return no_update, no_update, no_update, no_update, dbc.Alert("Password must be at least 8 characters", color="danger")
        
        if signup_pass != signup_confirm:
            return no_update, no_update, no_update, no_update, dbc.Alert("Passwords do not match", color="danger")
        
        if create_user(signup_user, signup_pass, signup_email):
            return '/dashboard', 'logged-in', signup_user, no_update, no_update
        else:
            return no_update, no_update, no_update, no_update, dbc.Alert("Username already exists", color="danger")
    
    return no_update, no_update, no_update, no_update, no_update

# Handle sleep data submission
@callback(
    Output('sleep-score-display', 'children'),
    Output('recommendations', 'children'),
    Output('sleep-data-store', 'data'),
    Input('submit-button', 'n_clicks'),
    State('sleep-hours', 'value'),
    State('disturbances', 'value'),
    State('temperature', 'value'),
    State('light-exposure', 'value'),
    State('noise-level', 'value'),
    State('current-user', 'data'),
    prevent_initial_call=True
)
def analyze_and_display(n_clicks, hours, disturbances, temp, light, noise, username):
    if None in [hours, disturbances, temp, light, noise]:
        return "", dbc.Alert("Please fill all fields", color="danger"), no_update
    
    try:
        data = {
            'sleep_hours': float(hours),
            'disturbances': int(disturbances),
            'temperature': float(temp),
            'light_exposure': light,
            'noise_level': noise
        }
        
        score = analyze_sleep(data)
        user_id = get_user_id(username)
        if user_id:
            save_sleep_record(user_id, data, score)
        
        # Add score to data for chatbot
        sleep_data = data.copy()
        sleep_data['sleep_score'] = score
        
        # Create gauge
        gauge = daq.Gauge(
            id='sleep-score-gauge',
            label="Sleep Score",
            value=score,
            min=0,
            max=100,
            color={
                "gradient": True,
                "ranges": {
                    "red": [0, 50],
                    "yellow": [50, 80],
                    "green": [80, 100]
                }
            },
            size=200,
            className="mb-3"
        )
        
        # Create recommendations
        if score > 80:
            rec = dbc.Alert([
                html.H4("Excellent Sleep Quality", className="alert-heading"),
                html.P("Keep up the good habits! Your sleep environment and duration are optimal."),
            ], color="success")
        elif score > 50:
            rec = dbc.Alert([
                html.H4("Moderate Sleep Quality", className="alert-heading"),
                html.P("Consider these improvements:"),
                html.Ul([
                    html.Li("Aim for 7-9 hours of sleep"),
                    html.Li("Reduce disturbances in your sleep environment"),
                    html.Li("Maintain room temperature between 18-24°C"),
                    html.Li("Minimize light and noise exposure")
                ])
            ], color="warning")
        else:
            rec = dbc.Alert([
                html.H4("Poor Sleep Quality", className="alert-heading"),
                html.P("Immediate improvements needed:"),
                html.Ul([
                    html.Li("Increase sleep duration to at least 7 hours"),
                    html.Li("Identify and eliminate disturbance sources"),
                    html.Li("Adjust room temperature to optimal range"),
                    html.Li("Use blackout curtains and white noise if needed"),
                    html.Li("Consider a consistent bedtime routine")
                ])
            ], color="danger")
        
        return gauge, rec, sleep_data
    
    except ValueError:
        return "", dbc.Alert("Please enter valid numbers", color="danger"), no_update

# Chatbot interaction (FIXED)
# Chatbot interaction (FIXED)
@callback(
    Output('chat-messages', 'children'),
    Output('chat-input', 'value'),
    Input('chat-send', 'n_clicks'),
    State('chat-input', 'value'),
    State('current-user', 'data'),
    State('sleep-data-store', 'data'),
    State('chat-messages', 'children'),
    prevent_initial_call=True
)
def handle_chat(n_clicks, message, username, sleep_data, current_messages):
    if not message or not username:
        return no_update, ""
    
    # Get user ID
    user_id = get_user_id(username)
    
    # Generate response
    response = get_chatbot_response(message, username, sleep_data)
    
    # Save conversation
    if user_id:
        save_chat_message(user_id, message, response)
    
    # Create message bubbles
    user_bubble = dbc.Card([
        dbc.CardBody([
            html.P(message, className="mb-0", style={"whiteSpace": "pre-wrap"})
        ])
    ], className="mb-2 bg-light", style={"maxWidth": "75%", "marginLeft": "auto"})
    
    # Split response by newlines and create HTML with <br> tags
    response_lines = response.split('\n')
    response_content = []
    for line in response_lines:
        response_content.append(line)
        response_content.append(html.Br())
    response_content = response_content[:-1]  # Remove the last <br>
    
    bot_bubble = dbc.Card([
        dbc.CardBody([
            html.P(response_content, className="mb-0", style={"whiteSpace": "pre-wrap"})
        ])
    ], className="mb-2 bg-primary text-white", style={"maxWidth": "75%"})
    
    # Update chat messages
    if current_messages is None:
        current_messages = []
    
    new_messages = current_messages + [user_bubble, bot_bubble]
    
    return new_messages, ""

# Update history chart (IMPROVED)
@callback(
    Output('sleep-history-chart', 'figure'),
    Input('submit-button', 'n_clicks'),
    Input('sleep-data-store', 'data'),
    State('current-user', 'data'),
)
def update_history(n_clicks, sleep_data, username):
    user_id = get_user_id(username)
    records = get_user_records(user_id, limit=30)  # Get last 30 records
    
    if not records:
        return px.bar(title="No sleep records yet").update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
    
    df = pd.DataFrame(records)
    df['record_date'] = pd.to_datetime(df['record_date'])
    df = df.sort_values('record_date')
    
    fig = px.bar(
        df,
        x='record_date',
        y='sleep_score',
        title="Your Sleep Scores Over Time",
        labels={'sleep_score': 'Sleep Score', 'record_date': 'Date'},
        color='sleep_score',
        color_continuous_scale='RdYlGn',
        range_color=[0, 100],
        hover_data=['sleep_hours', 'disturbances', 'temperature']
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        yaxis_range=[0, 100],
        hovermode='x unified'
    )
    
    return fig

# Update trends chart (IMPROVED)
@callback(
    Output('sleep-trends-chart', 'figure'),
    Input('submit-button', 'n_clicks'),
    Input('sleep-data-store', 'data'),
    State('current-user', 'data'),
)
def update_trends(n_clicks, sleep_data, username):
    user_id = get_user_id(username)
    records = get_user_records(user_id, limit=30)  # Get last 30 records
    
    if not records or len(records) < 2:
        return px.line(title="Not enough data for trends").update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
    
    df = pd.DataFrame(records)
    df['record_date'] = pd.to_datetime(df['record_date'])
    df = df.sort_values('record_date')
    
    # Create figure with secondary y-axis
    fig = px.line(
        df,
        x='record_date',
        y=['sleep_hours'],
        title="Sleep Trends",
        labels={'value': 'Hours', 'record_date': 'Date', 'variable': 'Metric'},
        color_discrete_map={
            'sleep_hours': '#1f77b4'
        }
    )
    
    # Add sleep score as a separate trace
    fig.add_trace(px.line(
        df,
        x='record_date',
        y=['sleep_score'],
        color_discrete_map={
            'sleep_score': '#2ca02c'
        }
    ).data[0])
    
    # Update layout
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        yaxis=dict(title='Sleep Hours', range=[0, 10]),
        yaxis2=dict(title='Sleep Score', range=[0, 100], overlaying='y', side='right'),
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    # Update traces to use different y-axes
    fig.data[1].update(yaxis='y2')
    
    return fig

# =============================================
# RUN THE APP
# =============================================
if __name__ == '__main__':
    app.run(debug=True, port=8050)