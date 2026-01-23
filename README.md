# lost-and-found

📌 Project Title
Lost and Found Smart Matching System


📖 Problem Statement
People often lose personal belongings or get separated from people in public places.
There is no centralized digital system to report lost or found items or missing persons and efficiently match them.


🎯 Objective
To develop a web-based application where:
Users can report lost or found items/persons
The system automatically finds possible matches
Police can verify and close cases
Emergency cases (lost persons) get priority


🧰 Tech Stack (As taught in Internship)
Frontend
HTML
CSS
JavaScript
Bootstrap / Tailwind CSS

Backend
Python with Flask
REST APIs

Database
SQLite / MySQL / MongoDB

Tools
Git & GitHub
VS Code
Browser (Chrome)

👥 User Roles
End User
Volunteer
Police (Admin authority)
No separate super admin to keep the system simple.

⚙️ Core Features
User login & registration
Report lost items
Report found items
🚨 Emergency reporting for lost persons
Smart matching based on:
Description
Location
Date
Police verification
Case closure


#📁 Folder Structure(tentative)
project/
│
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
│
├── templates/
│   ├── login.html
│   ├── dashboard.html
│   ├── report_lost.html
│   ├── report_found.html
│   ├── report_lost_person.html
│   └── matches.html
│
├── app.py
├── database.db
├── requirements.txt
└── README.md



# 🗄️ Database Schema

## User Collection

| Field     | Type                           |
| --------- | ------------------------------ |
| userId    | String                         |
| name      | String                         |
| email     | String                         |
| password  | String                         |
| role      | Enum (USER, VOLUNTEER, POLICE) |
| createdAt | Date                           |

## Report Collection

| Field       | Type                                      |
| ----------- | ----------------------------------------- |
| reportId    | String                                    |
| userId      | String                                    |
| type        | Enum (LOST, FOUND)                        |
| category    | String                                    |
| title       | String                                    |
| description | String                                    |
| location    | String                                    |
| date        | Date                                      |
| isEmergency | Boolean                                   |
| status      | Enum (PENDING, MATCHED, VERIFIED, CLOSED) |

## Match Collection

| Field         | Type                               |
| ------------- | ---------------------------------- |
| matchId       | String                             |
| lostReportId  | String                             |
| foundReportId | String                             |
| matchScore    | Number                             |
| status        | Enum (PENDING, APPROVED, REJECTED) |

---

