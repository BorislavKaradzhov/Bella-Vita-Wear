# Bella Vita Wear 🛍️

Bella Vita Wear is an e-commerce platform built with Django. It features a robust product catalog, an interactive customer review system with object-level security, asynchronous background task processing, and a RESTful API endpoint.

## 💻 Cloud-deployed Version

The cloud-deployed version is available at https://bellavitawear.onrender.com

### User accounts
* Superuser: bernie Password: H@pp!CaT9
* Content Manager: jen_content Password: De$igN75@
* Fulfillment Team: john_warehouse Password: MoveBoxes$$
* Standard customer: shopper Password: Shop1234@

## 🚀 Key Features

* **Product Catalog & Checkout:** Browse designs, filter categories, and securely process orders. An order status cannot be reverted from 'Fulfilled' to 'Pending', and cannot be changed after marked 'Cancelled'.  
* **Full CRUD Review System:** Customers can read, write, update, and delete their own product reviews, secured by Django's `UserPassesTestMixin`. When an order is marked 'Fulfilled', the customer can leave a review by going to the design detail page.
* **Asynchronous Processing:** Utilizes Celery for automated background tasks, such as calculating customer loyalty discounts upon order fulfillment. After every three fulfilled orders for a customer, Celery issues an automatic 50% discount code, emails the automatic discount email (prints on Celery terminal for development purposes), and automatically applies it to the customer's next order. Prints Welcome email on the local terminal upon successful user registration.
* **RESTful API:** Provides a JSON endpoint (`/api/designs/`) for fetching product catalog data, and (`/api/designs/<slug>/`) that returns JSON details for a single design.
* **Role-Based Access Control:** Distinct permissions for Customers, Fulfillment Staff, and Administrators. Distinct navbar and links permissions for different groups and users.
* **Cloud Media Management:** Seamless image upload and delivery via Cloudinary.
* **Custom Error Handling:** Beautifully styled, user-friendly 404 (Not Found) and 500 (Server Error) pages.

## 🛠️ Technology Stack

* **Backend:** Python 3.10+, Django 4.2/5.0+
* **Database:** PostgreSQL (Local & Production)
* **Background Tasks:** Celery, Redis (Local message broker)
* **Frontend:** HTML5, CSS3, Bootstrap 5
* **Media Storage:** Cloudinary
* **Deployment & Hosting:** Gunicorn, WhiteNoise, Render

---

## 💻 Local Setup & Installation

Follow these steps to get the project running on your local development machine.

### Prerequisites
* Python 3.10 or higher
* PostgreSQL installed and running locally
* Redis server installed and running locally (for Celery tasks)

1. **Clone the repository:**
    ```bash
    git clone https://github.com/BorislavKaradzhov/Bella-Vita-Wear.git
    cd bellavitawear

2. **Create and activate a virtual environment:**

First, copy the .env.template file:
#### If using Windows Command Prompt:
    copy .env.example .env    

#### Otherwise, please use:
    cp .env.example .env
    
Then: 
#### Windows:
    python -m venv venv
    venv\Scripts\activate
#### macOS/Linux:
    python3 -m venv venv
    source venv/bin/activate

3. **Install dependencies:**
    ```bash
    pip install -r requirements.txt

4. **Set Up the Database:**

Ensure PostgreSQL is running and set up your database using the credentials provided in the <code>.env.example</code> file. Connect to the database.
   Add your info to the bottom of the .env in the root directory:
    # Cloudinary (Required for media uploads)
    CLOUD_NAME=your_cloud_name
    CLOUD_API_KEY=your_api_key
    CLOUD_API_SECRET=your_api_secret

5. **Apply Migrations:**
    ```bash
    python manage.py makemigrations
    python manage.py migrate

6. **Create a Superuser to access the admin panel:**
    ```bash
    python manage.py createsuperuser
    
Follow the prompts to set up the superuser credentials.
   
7. **Run the Server Terminal 1 (Django Server):**
    ```bash
    python manage.py runserver
   
8.  **Run the Server Terminal 2 (Celery Worker):**
    ```bash
    celery -A BellaVitaWear worker -l info
   
9.  **Navigate to <code>http://127.0.0.1:8000/</code> in your browser.**

## 🛠️ Django site admin
**Navigate to <code>http://127.0.0.1:8000/admin/</code> in your browser.**

***To log in, please use the previously created credentials:***

-------

☁️ Deployment Strategy
This application is configured for seamless deployment on Render.com. It utilizes dynamic environment variable checking to instantly switch from local development settings to production infrastructure.

Production Features:

Gunicorn: Serves the WSGI application securely.

WhiteNoise: Compresses and caches static files (CSS/JS) for high-performance delivery.

dj-database-url: Automatically parses the cloud provider's PostgreSQL credentials.

Eager Task Execution: Celery is configured via CELERY_TASK_ALWAYS_EAGER = True to process background tasks directly in memory, bypassing the need for a separate paid Redis broker in the cloud.

Deployment Steps (Render)

Connect your GitHub repository to Render and create a Web Service.

Set the Build Command to ./build.sh.

Set the Start Command to gunicorn BellaVitaWear.wsgi:application.

Provide the following Environment Variables in the Render dashboard:

DATABASE_URL (From a Render PostgreSQL instance)

SECRET_KEY (A secure, randomized string)

CLOUD_NAME, CLOUD_API_KEY, CLOUD_API_SECRET (From Cloudinary)

PYTHON_VERSION (e.g., 3.10.0)


------

📡 API Documentation
The application exposes a RESTful API for consuming the design catalog.

Endpoint: GET /api/designs/
Endpoint: GET /api/designs/<slug>


Response Format (JSON):

[
  {
    "id": 1,
    "title": "Classic Red Hoodie",
    "category": "Hoodies",
    "price": "45.00",
    "image_url": "[https://res.cloudinary.com/](https://res.cloudinary.com/)..."
  }
]