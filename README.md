# Dot Course

Dot Course is an advanced E-Learning platform that provides a seamless online learning experience with interactive features.

## Features

- Search for courses by name, content, description, or instructor.
- Purchase courses, access video content, and track progress.
- Solve MCQs after watching videos and receive certificates upon course completion.
- Video content is converted to HLS format for optimized streaming.
- Background tasks such as video processing and progress tracking are managed using Celery and Redis.
- Customized admin panel for instructors to easily upload and manage course content.
- Secure authentication and user management.

## Tech Stack

Dot Course leverages various open-source technologies:

- **Frontend:** Bootstrap 5 for UI components.
- **Backend:** Django for server-side logic.
- **Database:** PostgreSQL (previously SQLite3).
- **Asynchronous Tasks:** Celery and Redis for background job processing.
- **AJAX Requests:** HTMX for dynamic interactions.
- **Docker:** Containerized deployment using Docker and Docker Compose.

## Installation & Setup

Dot Course requires [Docker](https://www.docker.com/) to run.

### Running with Docker

1. Clone the repository:
   ```sh
   git clone https://github.com/YousefSedik/Dot-Courses.git
   cd Dot-Course
   ```
2. Create a `.env` file in the root directory and configure the following variables:
   ```sh
   SECRET_KEY='your-secret-key'
   DEBUG='False'
   EMAIL_HOST_USER='your-email@example.com'
   EMAIL_HOST_PASSWORD='your-email-password'
   EMAIL_HOST='smtp.example.com'
   EMAIL_PORT=587
   EMAIL_USE_TLS='True'
   STRIPE_PUBLISHABLE_KEY='your-stripe-key'
   STRIPE_SECRET_KEY='your-stripe-secret-key'
   ```
3. Run the application using Docker Compose:
   ```sh
   docker-compose up --build
   ```

## Screenshots

### Home Page
![Home Page](project-images/Home%20Page.png)

### About Course Page
![About Course View](project-images/About%20Course%20View.png)

### Cart Page
![Cart View](project-images/Cart%20View%20.png)


### Corrected MCQs
![Solving MCQs](project-images/Corrected%20.png)

### Solving MCQs
![Solving MCQs](project-images/Solving%20MCQs%202%20.png)

### Course Content Page
![View Course Content](project-images/Course%20View.png)

---
Dot Course is open source and available on [GitHub](https://github.com/YousefSedik/Dot-Courses). Contributions are welcome!
