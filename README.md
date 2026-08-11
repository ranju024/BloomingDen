
# BloomingDen

BloomingDen is a Django-based plant marketplace where users can browse plants, purchase products, sell plants, manage listings, communicate with buyers and sellers, and manage orders.

The project was built as a full-stack academic and portfolio project using Django.

## Features

- User registration and authentication
- Buyer and seller roles
- Vendor/shop profiles
- Product catalog
- Product categories
- Multiple product images
- Product search and filtering
- Shopping cart
- Checkout system
- Cash on Delivery
- eSewa sandbox payment integration
- Buyer order management
- Seller order management
- Order status updates
- Seller product management
- Plant marketplace listings
- Buyer-seller conversations
- Image lightbox for product images
- Django admin panel

## Tech Stack

- Python
- Django
- SQLite
- HTML
- CSS
- JavaScript
- eSewa Sandbox API
- WhiteNoise

## Project Structure

```text
BloomingDen/
├── bloomingden/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── catalog/
│   ├── models.py
│   ├── forms.py
│   ├── urls.py
│   ├── decorators.py
│   ├── context_processors.py
│   ├── views/
│   ├── templates/
│   ├── static/
│   └── migrations/
│
├── manage.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```



## Setup

Clone the repository:

    git clone https://github.com/ranju024/BloomingDen.git
    cd BloomingDen

Create and activate a virtual environment:    python -m venv venv

Windows:    venv\Scripts\activate

Linux/macOS:    source venv/bin/activate

Install dependencies:    pip install -r requirements.txt

Create a `.env` file using `.env.example` and add your environment variables.

cd ./bloomingden

Run migrations:    python manage.py migrate

Create an admin account:    python manage.py createsuperuser

Start the development server:    python manage.py runserver

## eSewa

BloomingDen currently uses eSewa's sandbox environment for testing. Live eSewa payments require a registered merchant account and production credentials.

## Project Status

This project was built as an academic and portfolio project and is currently being prepared for deployment. 

And, it is a work in progress.
