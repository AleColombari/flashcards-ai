# Flashcards AI
#### Video Demo:
#### Description: 
Flashcards AI is a web application designed to help students learn faster and more effectively by transforming raw educational content into interactive flashcards using artificial intelligence.

This project was created as my final submission for CS50's Introduction to Computer Science. I chose to build this app in response to a personal and widely shared need in my community(students): a simple and efficient way to study class materials through active recall.

The goal of Flashcards AI is to support better study habits by converting class notes into flashcards—tools proven to boost memory and understanding through active recall and spaced repetition. Users can paste any educational text into a single input box, and the app automatically generates flashcards in the following format:

Front: A concise summary or key concept extracted from the input.

Back: A multiple-choice question (MCQ) with four options and a clearly identified correct answer.

This interactive structure promotes both review and self-assessment, helping learners reinforce comprehension and retention.

Technologies Used
Python (Flask) – Backend server logic, routing, and session management.

SQLite – Lightweight relational database for storing users, folders, and flashcards.

HTML/CSS (Jinja2 templates) – Dynamic, responsive frontend rendering.

JavaScript (minimal) – Enables interactive behaviors, such as flipping flashcards.

Google Gemini API – Generates AI-based summaries and MCQs.

How It Works
After registration and login, users are taken to a unified dashboard with two main sections:

Flashcard Generation
A form allows users to paste raw educational text and optionally select a folder (or default to “New Flashcards”). Upon submission, the AI generates both a front-side summary and a back-side MCQ.

Folder Sidebar
Displayed on the right, this section lists all user-created folders. It allows users to view, rename, create, or delete folders. Flashcards are organized by folder for easier management.

Flashcard Viewer
When viewing a folder, users can:

Flip flashcards by clicking on them.

Navigate between cards using Previous/Next buttons.

Delete flashcards as needed.

File Structure
app.py – Main application logic, route handling, and AI integration.

helpers.py – Login decorators, “new folder” creation logic, and DB helper functions.

flashcards.db – SQLite database storing all persistent app data.

templates/ – HTML templates:

layout.html: Base layout with header and nav.

index.html: Landing page with login form.

register.html: User registration form.

dashboard.html: Flashcard generator and folder manager.

folder_view.html: Flashcard viewer with navigation.

static/style.css – Custom styling for layout, typography, and responsiveness.

.env – Securely stores the API key (excluded from version control).

Key Design Decisions
Folder System
Flashcards are organized into folders per user to prevent clutter and support long-term study management.

Card Flip UX
A simple flip interaction toggles between summary and question, creating a smooth and intuitive study experience.

AI Formatting
"< pre >" blocks and custom CSS preserve formatting and improve readability of AI-generated MCQs.

Flash Messaging
Informational alerts (success, error, etc.) are displayed as flash messages that auto-dismiss after 3 seconds, providing clean user feedback.

AI Provider Choice
After comparing OpenAI and Gemini APIs, I chose Gemini 1.5 Flash for its low token costs and lack of credit card requirement.

Dashboard Simplicity
All major functionality—generation, navigation, and folder control—is consolidated into a single dashboard, mirroring modern productivity apps.

Reflections
During development, I faced several technical challenges, including scroll and sidebar positioning, responsive layout management, and API rate limitations. I prioritized user experience and usability, often revisiting earlier designs to simplify and improve the interface.

I'm proud of how this project bridges static note-taking and interactive learning through AI. While there’s room to expand—such as adding flashcard editing, user preferences, or AI parameter tuning—the current version already delivers practical value for students.

Final Notes
This project represents my strongest work to date, combining backend logic, frontend design, and AI integration into a cohesive and functional product. It was both a technical and creative endeavor, and I’m excited to showcase Flashcards AI as my final project for CS50.

