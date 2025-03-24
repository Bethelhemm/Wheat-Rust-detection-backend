# AI-Powered Wheat Rust Detection Backend

## Project Overview
This is the backend service for the AI-powered wheat rust detection mobile application. The backend is built using **Django** and containerized with **Docker**. It handles user authentication, API endpoints, and interactions with the machine learning model hosted in a separate GitHub repository.

## Features
- **User Authentication:** Secure login and registration using Django's authentication system.
- **API Endpoints:** For handling image uploads, retrieving disease analysis results, and fetching treatment recommendations.
- **Voice Query Support:** Enabling users to record and post voice queries in the community forum.
- **Dockerized Setup:** Simplifying deployment with a containerized environment.

## Technologies Used
- **Backend Framework:** Django (Django Rest Framework for APIs)
- **Database:** PostgreSQL
- **Containerization:** Docker & Docker Compose
- **Authentication:** JWT-based authentication using `djangorestframework-simplejwt`
- **Storage:** Cloud-based storage for images (e.g., AWS S3, Google Cloud Storage) [To be configured]

## Setup Instructions

### Prerequisites
Ensure you have the following installed on your system:
- Python (>=3.9)
- Docker & Docker Compose
- PostgreSQL

### 1. Clone the Repository
```sh
git clone <repo-url>
cd <repo-directory>
```

### 2. Set Up Environment Variables
Create a `.env` file in the root directory and define the following:
```env
SECRET_KEY=your-secret-key
DEBUG=True
DATABASE_URL=postgres://user:password@db:5432/database_name
ALLOWED_HOSTS=*
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

### 3. Build and Run with Docker
```sh
docker-compose up --build
```
This will start the Django backend and PostgreSQL database.

### 4. Run Migrations
Once the container is running, apply database migrations:
```sh
docker exec -it <container_id> python manage.py migrate
```

### 5. Create a Superuser (Optional)
To access the Django admin panel, create a superuser:
```sh
docker exec -it <container_id> python manage.py createsuperuser
```
Follow the prompts to set up credentials.

### 6. Access the API
- The API will be available at `http://localhost:8000/api/`
- Swagger documentation (if enabled) can be accessed at `http://localhost:8000/swagger/`

## API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register/` | Register a new user |
| POST | `/api/auth/login/` | Authenticate a user and receive a token |
| POST | `/api/image/upload/` | Upload an image for disease analysis |
| GET  | `/api/recommendations/` | Fetch treatment recommendations |

## Future Enhancements
- Integrating image processing pipeline with the ML model
- Deploying backend to cloud infrastructure
- Implementing role-based access control (RBAC)

## Contributors
- Bethelhem Gebeyehu
