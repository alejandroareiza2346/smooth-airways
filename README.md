# Smooth Airlines ✈️

A luxury private airline platform offering exclusive charter flights, VIP services, and premium travel experiences.

## Features

- Private charter flights booking
- VIP security and luxury ground transportation
- Exclusive hotel and restaurant reservations
- 24/7 Concierge service
- Smooth Black Card membership program
- Corporate and family travel services

## Tech Stack

### Backend
- Django 5.0
- Django REST Framework
- PostgreSQL
- Authentication
- Stripe Payment Integration



## Setup Instructions

### Backend Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
- Copy `.env.example` to `.env`
- Fill in required environment variables

4. Run migrations:
```bash
python manage.py migrate
```

5. Create superuser:
```bash
python manage.py createsuperuser
```

6. Run development server:
```bash
python manage.py runserver
```


2. Start development server:
```bash
npm run dev
```

## Environment Variables

Required environment variables:
- `SECRET_KEY`: Django secret key
- `DEBUG`: Set to True for development
- `DATABASE_URL`: PostgreSQL connection string
- `STRIPE_SECRET_KEY`: Stripe API secret key
- `STRIPE_PUBLISHABLE_KEY`: Stripe publishable key
- `AWS_ACCESS_KEY_ID`: AWS access key for file storage
- `AWS_SECRET_ACCESS_KEY`: AWS secret key
- `AWS_STORAGE_BUCKET_NAME`: S3 bucket name

## API Documentation

API documentation is available at `/api/docs/` when running the development server.

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is proprietary and confidential.

## Support

For support Alejandro.workspace@outlook.com 