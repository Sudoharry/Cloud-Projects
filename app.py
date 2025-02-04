from flask import Flask, render_template, request
import graphviz
import sqlite3
import os

app = Flask(__name__)

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect("recommendations.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS recommendations 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  application_type TEXT, 
                  traffic TEXT, 
                  database_type TEXT, 
                  recommended_services TEXT, 
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

# Function to select AWS services based on user inputs
def select_services(application_type, traffic, database_type):
    services = []
    
    if application_type == "Microservices":
        services.append("EKS or ECS")
    elif application_type == "Serverless":
        services.append("AWS Lambda")
    else:
        services.append("EC2 or ECS")
    
    if traffic == "High":
        services.append("ALB + Auto Scaling + CloudFront")
    
    if database_type == "SQL":
        services.append("RDS or Aurora")
    elif database_type == "NoSQL":
        services.append("DynamoDB")
    
    return services

# Function to save recommendations
def save_recommendation(application_type, traffic, database_type, services):
    conn = sqlite3.connect("recommendations.db")
    c = conn.cursor()
    c.execute("INSERT INTO recommendations (application_type, traffic, database_type, recommended_services) VALUES (?, ?, ?, ?)", 
              (application_type, traffic, database_type, ", ".join(services)))
    conn.commit()
    conn.close()

# Function to get past recommendations
def get_recommendations():
    conn = sqlite3.connect("recommendations.db")
    c = conn.cursor()
    c.execute("SELECT * FROM recommendations ORDER BY timestamp DESC")
    records = c.fetchall()
    conn.close()
    return records

# Function to generate architecture diagram
def generate_diagram(services):
    try:
        dot = graphviz.Digraph(format='png')
        dot.attr(bgcolor='white')
        
        dot.node("User", "User", shape="ellipse", style="filled", fillcolor="lightblue")
        
        for service in services:
            dot.node(service, service, shape="box", style="filled", fillcolor="lightgray")
            dot.edge("User", service)
        
        filename = "static/aws_architecture"
        dot.render(filename)
        return filename + ".png"
    except Exception as e:
        print("Graphviz Error:", e)
        return None

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Get form inputs
        application_type = request.form.get("application_type")
        traffic = request.form.get("traffic")
        database_type = request.form.get("database_type")

        # Check for missing inputs
        if not application_type or not traffic or not database_type:
            past_recommendations = get_recommendations()  # Fetch past recommendations
            return render_template("index.html", error="All fields are required!", past_recommendations=past_recommendations)

        # Get recommended services
        services = select_services(application_type, traffic, database_type)

        # Save to database
        save_recommendation(application_type, traffic, database_type, services)

        # Generate diagram
        diagram_path = generate_diagram(services)

        return render_template("result.html", services=services, diagram=diagram_path, show_diagram=True)
    
    # Fetch past recommendations when loading the page
    past_recommendations = get_recommendations()
    return render_template("index.html", past_recommendations=past_recommendations)


if __name__ == "__main__":
    init_db()  # Ensure the database is set up before running the app
    app.run(host="0.0.0.0", port=5000, debug=True)
