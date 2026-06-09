# smooth-airways
**Engineering Lead: Alejandro Areiza Alzate**
**Technical Domain: Full-Stack Web Engineering / Payment Integration / Geospatial Systems**

---

## 1. Executive Summary and Architectural Vision

**Smooth Airlines** is a full-stack Django 5 platform for a luxury private aviation service — offering charter flight bookings, VIP ground services, exclusive concierge experiences, and a Smooth Black Card membership program. The system is architecturally distinct from the other airline projects in this portfolio: it integrates **Stripe** for live payment processing, **AWS S3** via `django-storages` + `boto3` for media asset storage, **Leaflet** interactive maps via `django-leaflet` for route visualization, and **geopy** for geodesic distance calculations between airports. PDF ticket and itinerary generation is handled by **WeasyPrint**, a CSS-based HTML-to-PDF renderer producing print-ready documents from Django templates. The API surface is fully documented via **Swagger/ReDoc** through `drf-yasg`. Brute-force and credential-stuffing attacks are mitigated at the authentication layer via `django-axes`. The system is organized into five domain applications (`accounts`, `bookings`, `flights`, `services`, `core`) under the `smooth_airlines` project configuration, with a dedicated `test_db.py` for database connectivity validation.

---

## 2. Requirement Analysis and Strategic Alignment

- **Functional:** Private charter flight search and booking with seat class and aircraft selection; Stripe payment integration for booking confirmation with webhook support for async payment events; VIP service catalog — luxury ground transportation, exclusive hotel and restaurant reservations, private security services; Smooth Black Card loyalty membership program with tier management; 24/7 concierge service request management; interactive route map visualization with Leaflet showing origin-destination geodesic paths; PDF ticket and itinerary generation via WeasyPrint; data import/export for operations management via `django-import-export`; Swagger/ReDoc auto-generated API documentation at `/api/docs/`; brute-force login protection via `django-axes`; social authentication via `django-allauth` + `dj-rest-auth`.
- **Non-Functional:** AWS S3 media storage for aircraft images, service photos, and member assets via `django-storages` + `boto3`; `django-imagekit` for server-side image processing and thumbnail generation; `django-money` for multi-currency price management with currency-aware arithmetic; PostgreSQL via `psycopg2-binary` and `dj-database-url`; WhiteNoise for static file serving; Gunicorn as WSGI server; Tailwind CSS via `django-tailwind` + `crispy-tailwind` for the frontend layer.
- **Strategic Goal:** A feature-complete luxury aviation platform demonstrating integration-heavy backend engineering — live payment processing, cloud media storage, geospatial route computation, PDF document generation, and API documentation — applicable to fintech, travel technology, and SaaS platform engineering roles.

---

## 3. Technical Stack and Infrastructure

- **Core Language:** Python 3.x (61.4%), HTML/Jinja2 templates (36.6%), CSS (2.0%)
- **Web Framework:** Django 5.0.1 — multi-app architecture, ORM, migrations, admin
- **API Layer:** Django REST Framework 3.14.0 + `drf-yasg` 1.21.10 — ViewSets, serializers, Swagger/ReDoc documentation generation
- **Authentication:** `django-allauth` ≥0.60.1 + `dj-rest-auth` 5.0.2 — social OAuth2 + standard auth; `django-axes` ≥6.3.0 — brute-force and credential-stuffing protection
- **Payment Processing:** Stripe ≥8.4.0 — live payment intents, charge confirmation, webhook event handling
- **Cloud Storage:** `django-storages` 1.14.2 + `boto3` 1.34.14 — AWS S3 for media asset storage (aircraft images, service photos, member assets)
- **Image Processing:** `django-imagekit` 5.0.0 — server-side image processing, thumbnail generation, format conversion
- **Geospatial:** `django-leaflet` 0.29.0 — interactive Leaflet map integration for route visualization; `geopy` 2.4.1 — geodesic distance calculation between airport coordinates
- **Document Generation:** WeasyPrint 60.2 — HTML/CSS-to-PDF rendering for tickets and itineraries
- **Currency Management:** `django-money` 3.4.0 — multi-currency price fields with currency-aware arithmetic
- **Data Operations:** `django-import-export` 3.3.3 — admin-level CSV/XLSX import/export for flights, bookings, and members
- **Frontend:** Tailwind CSS via `django-tailwind` ≥3.8.0, `crispy-tailwind` 0.5.0, `django-crispy-forms` 2.1, `django-bootstrap5` 23.4
- **Execution Environment:** PostgreSQL (production); Gunicorn + reverse proxy; AWS S3 for media; environment variables via `python-dotenv` + `django-environ`

---

## 4. Engineering Logic and Implementation

**Stripe Payment Integration:** Booking confirmation triggers a Stripe `PaymentIntent` creation via the Stripe Python SDK. The client receives the `client_secret` for front-end confirmation using Stripe.js. Asynchronous payment events (successful charge, payment failure, refund) are delivered via Stripe webhooks to a dedicated endpoint that verifies the webhook signature using the `STRIPE_WEBHOOK_SECRET` and updates the booking status accordingly — ensuring payment state consistency even when the user closes the browser before the redirect completes.

**Geospatial Route Pipeline:** The `flights` application stores origin and destination airports with latitude/longitude coordinates. `geopy`'s `geodesic` distance function calculates the great-circle distance between airport pairs for display and pricing purposes. `django-leaflet` renders an interactive Leaflet map on booking detail pages, drawing the geodesic route arc between origin and destination using the airport coordinates — giving passengers a visual representation of their charter route.

**PDF Ticket Generation (WeasyPrint):** Upon booking confirmation, a Django template is rendered to HTML with the full booking context (passenger details, flight schedule, aircraft type, seat assignment, QR booking reference) and passed to WeasyPrint's HTML-to-PDF pipeline. WeasyPrint interprets CSS print stylesheets — including custom fonts, page margins, and print media queries — producing a layout-accurate PDF without requiring a headless browser. The generated PDF is served as a downloadable response or stored to S3 for retrieval.

**AWS S3 Media Storage:** `django-storages` replaces Django's default `FileSystemStorage` with an S3-backed implementation. All `ImageField` and `FileField` uploads (aircraft photos, service imagery, member profile pictures) are streamed directly to the configured S3 bucket. `django-imagekit` generates optimized thumbnails from source images at upload time, storing the processed versions alongside originals in S3.

**Brute-Force Protection (`django-axes`):** `django-axes` monitors failed authentication attempts per IP address and per username. After a configurable threshold of failures, the IP or account is locked for a configurable cooldown period. Lock events are logged to the `axes_accessattempt` table with timestamp, IP, user agent, and attempted username — providing a security event log auditable through the Django admin.

**API Documentation (`drf-yasg`):** All DRF ViewSets and APIViews are introspected by `drf-yasg` to generate a complete OpenAPI 2.0 specification at startup. Swagger UI is served at `/api/docs/` and ReDoc at `/api/redoc/`, providing interactive documentation with request/response schema exploration and live API testing from the browser — without maintaining a separate documentation file.

- **Data Structures:** Django model instances with `MoneyField` (django-money) for currency-aware pricing; `ImageSpecField` (django-imagekit) for lazy thumbnail generation; geopy `Distance` objects for geodesic calculations; Stripe `PaymentIntent` objects for payment state management.

---

## 5. Quality Assurance and Systematic Testing

- **Analytical Testing:** `test_db.py` validates PostgreSQL database connectivity and ORM availability before the development server is started — catching misconfigured `DATABASE_URL` values early; `drf-yasg` schema generation serves as a structural test of all API endpoints, failing at startup if any ViewSet has serializer configuration errors.
- **Constructive Testing:** Full booking flow validated end-to-end: charter flight search → seat selection → Stripe PaymentIntent creation → payment confirmation → booking status update via webhook → PDF ticket generation → S3 storage → ticket download; Leaflet map rendering validated across origin-destination pairs with geodesic arc computation; `django-axes` lockout behavior validated against repeated failed login attempts.
- **Edge Case Handlers:** Stripe webhook signature verification failure — webhook endpoint returns `400` and logs the event without updating booking state, preventing replay attacks; S3 upload failure — image field save raises a structured `IOError`, booking creation is rolled back within a database transaction; WeasyPrint rendering failure — structured error response returned, booking confirmation displayed in HTML without PDF attachment; `django-axes` IP lockout — locked IPs receive `403` with a cooldown message, legitimate users can request an unlock via the admin interface.

---

## 6. Security Governance and Compliance

- **Payment Security:** Stripe payment processing uses server-side `PaymentIntent` creation with client-side confirmation — card data never passes through the Django application. Webhook authenticity is verified using `stripe.Webhook.construct_event()` with the `STRIPE_WEBHOOK_SECRET` signature before any booking state mutation occurs.
- **Brute-Force Mitigation:** `django-axes` enforces per-IP and per-username login attempt limits. All lock events are logged with full request context (IP, user agent, timestamp, attempted username) — providing a security event trail aligned with ISO 27001 A.9.4 (System and Application Access Control) requirements.
- **Cloud Storage Security:** AWS S3 bucket access is controlled via IAM credentials (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`) stored exclusively in environment variables. Bucket policy should enforce private ACL on all uploaded objects — presigned URLs generated by `django-storages` provide time-limited access to private media assets.
- **Secret Management:** All sensitive credentials (`SECRET_KEY`, `DATABASE_URL`, `STRIPE_SECRET_KEY`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `STRIPE_WEBHOOK_SECRET`) managed via `python-dotenv` / `django-environ` from `.env`. The `.env` file is listed in `.gitignore` — **however, a `.env` file is currently present in the repository root and should be removed immediately** to prevent credential exposure.
- **OWASP Alignment:** Mitigates A07 (Identification and Authentication Failures) via `django-axes` brute-force protection and `django-allauth` verified authentication; A02 (Cryptographic Failures) via Stripe's PCI-DSS compliant payment flow and webhook signature verification; A05 (Security Misconfiguration) via environment variable secret isolation; A03 (Injection) via Django ORM parameterized queries throughout all domain applications.

---

## 7. Deployment and Initialization

**Prerequisites:** Python 3.x, PostgreSQL, Node.js (for Tailwind CSS compilation), AWS account (for S3 media storage), Stripe account

```bash
# Clone the repository
git clone https://github.com/alejandroareiza2346/smooth-airways.git

cd smooth-airways

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows

# Install Python dependencies
pip install -r requirements.txt

# Configure environment variables
# Copy .env.example to .env and fill in:
# SECRET_KEY=
# DEBUG=True
# DATABASE_URL=postgresql://user:password@localhost:5432/smooth_airways
# STRIPE_SECRET_KEY=sk_test_...
# STRIPE_PUBLISHABLE_KEY=pk_test_...
# STRIPE_WEBHOOK_SECRET=whsec_...
# AWS_ACCESS_KEY_ID=
# AWS_SECRET_ACCESS_KEY=
# AWS_STORAGE_BUCKET_NAME=

# Run database migrations
python manage.py migrate

# Validate database connectivity
python test_db.py

# Install Tailwind CSS dependencies
python manage.py tailwind install

# Build Tailwind CSS
python manage.py tailwind build

# Collect static files
python manage.py collectstatic --noinput

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

**API Documentation:** Available at `http://localhost:8000/api/docs/` (Swagger UI) and `http://localhost:8000/api/redoc/` (ReDoc) when the development server is running.

**Stripe webhook (local development):**

```bash
# Install Stripe CLI and forward webhooks to local server
stripe listen --forward-to localhost:8000/api/stripe/webhook/
```

---

## 8. Repository Structure

```
smooth-airways/
├── accounts/                   # User accounts, authentication, Smooth Black Card membership
├── bookings/                   # Charter flight booking, Stripe payment, PDF ticket generation
├── core/                       # Project-level views, base templates, shared utilities
├── flights/                    # Flight catalog, aircraft, airport coordinates, Leaflet route maps
├── services/                   # VIP services — ground transport, hotels, restaurants, concierge
├── smooth_airlines/            # Django project configuration, root URL routing, settings
├── .env                        # Environment variables (remove from repo — see Security section)
├── .gitignore
├── .hintrc                     # webhint accessibility/compatibility linting
├── manage.py                   # Django management CLI
├── requirements.txt            # 34 Python dependencies
├── test_db.py                  # PostgreSQL connectivity validation script
└── README.md                   # Project documentation
```

---

## 9. Professional Background

Project designed and developed by **Alejandro Areiza Alzate**, Computer Engineering student at Universidad Autónoma Latinoamericana (UNAULA), Medellín, and GitHub Developer Program member.

- **LinkedIn:** [Alejandro A. Areiza](https://www.linkedin.com/in/alejandroareizaa/)
- **Research (ORCID):** [0009-0002-2116-6918](https://orcid.org/0009-0002-2116-6918)
- **Certifications:** Microsoft Learn Level 6 — 26,950 XP (Azure Identity, Network Security & SQL Security); Cisco; Google; IBM; OWASP Top 10

---

## 10. License

Distributed under the **MIT License**. See `LICENSE` for full terms.
