# Coderr Backend

A RESTful backend for **Coderr**, a freelancer service marketplace.
It provides token-authenticated endpoints for business users to publish
service offers, for customers to order and review them, and for platform-wide
statistics, built with Django and the Django REST Framework.

👉 **[Live demo](https://coderr.benjaminblarr.de/)** ·
**[API documentation](https://coderr.benjaminblarr.de/api/schema/swagger-ui/)**

![Coderr API documentation](assets/preview.jpg)

The login page offers guest access for both user types, so the demo can be
explored without registering. The frontend is provided by the Developer
Akademie; everything behind `/api/` is this project.

---

## Features

- Token-based authentication (registration & login)
- Two user types with dedicated profiles: **business** and **customer**
- Offers, each with exactly three tiers (**basic**, **standard**, **premium**)
- Orders created from an offer tier as an immutable snapshot
- Reviews (at most one per business per customer)
- Order statistics (in-progress / completed counts) and platform base info
- Filtering, searching, ordering and pagination on the offers list
- Object-level permissions (owner / creator / business / customer rules)
- Auto-generated OpenAPI 3 documentation (Swagger UI & ReDoc) via drf-spectacular

---

## Tech Stack

**Backend**

<p align="left">
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg" height="40" alt="python logo" />
  <img width="12" />
  <img src="https://cdn.jsdelivr.net/gh/B-Blarr/B-Blarr@main/assets/django.svg" height="40" alt="django logo" />
  <img width="12" />
  <img src="https://cdn.jsdelivr.net/gh/B-Blarr/B-Blarr@main/assets/drf.svg?v=2" height="40" alt="django rest framework logo" />
</p>

**Infrastructure**

<p align="left">
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/linux/linux-original.svg" height="40" alt="linux logo" />
  <img width="12" />
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/nginx/nginx-original.svg" height="40" alt="nginx logo" />
  <img width="12" />
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/postgresql/postgresql-original.svg" height="40" alt="postgresql logo" />
</p>

| Component  | Version                                      |
| ---------- | -------------------------------------------- |
| Language   | Python 3.12+ (required by Django 6)          |
| Framework  | Django 6.0.6                                 |
| API        | Django REST Framework 3.17.1                 |
| Database   | PostgreSQL 16 with pgvector (Docker locally) |
| Auth       | DRF Token Authentication                     |
| API Docs   | drf-spectacular 0.30.0 (OpenAPI 3)           |
| Serving    | Gunicorn behind Nginx (Ubuntu 24.04)         |

---

## Project Structure

```
coderr_backend/
├── core/               # Project settings, root URL config, WSGI/ASGI
├── auth_app/           # Registration, login, profiles
│   └── api/            # serializers.py, views.py, urls.py, permissions.py
├── offers_app/         # Offers and offer details
│   └── api/            # serializers.py, views.py, urls.py, permissions.py, pagination.py
├── orders_app/         # Orders and order statistics
│   └── api/            # serializers.py, views.py, urls.py, permissions.py
├── reviews_app/        # Reviews
│   └── api/            # serializers.py, views.py, urls.py, permissions.py
├── base_app/           # Aggregated platform statistics (base-info)
│   └── api/            # views.py, urls.py
├── contact_app/        # Contact form of the portfolio site
├── assistant_app/      # Input filter and retrieval for the portfolio assistant
│   ├── api/            # serializers.py, views.py, urls.py
│   ├── knowledge/      # Knowledge base, one Markdown file per topic
│   └── management/     # build_index, evaluate_retrieval, evaluate_guard
├── embedding_service/  # Standalone FastAPI service that embeds texts
├── laya_service/       # Setup and smoke test for the Laya input filter
├── deploy/             # Deployment script and Nginx configuration
├── compose.yml         # Local PostgreSQL with pgvector
├── manage.py
└── requirements.txt
```

---

## Getting Started

### Prerequisites

- Python 3.12 or newer
- `pip` and `venv`
- Docker with Docker Compose, for the local PostgreSQL database

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/B-Blarr/Coderr-Backend.git
   cd Coderr-Backend
   ```

2. **Create and activate a virtual environment**

   ```bash
   python -m venv .venv
   ```

   Activate it. **Windows (PowerShell):**

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

   **macOS / Linux:**

   ```bash
   source .venv/bin/activate
   ```

3. **Install the dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up your environment file**, copy the provided template, then set
   your own secret key. The `.env` file itself is git-ignored.

   Windows (PowerShell):

   ```powershell
   Copy-Item .env.example .env
   ```

   macOS / Linux:

   ```bash
   cp .env.example .env
   ```

   Then open `.env` and replace the value with your own `SECRET_KEY`. You can
   generate one with:

   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

5. **Start the database**, PostgreSQL 16 with pgvector in Docker:

   ```bash
   docker compose up -d
   ```

   It listens on `127.0.0.1:5433` and matches the values in `.env.example`.
   Wait until `docker compose ps` shows the container as `healthy`.

6. **Apply the database migrations and create the cache table**

   ```bash
   python manage.py migrate
   python manage.py createcachetable
   ```

   The rate limits of the contact form and the portfolio assistant are
   counted in a database cache, so all Gunicorn workers share one count.
   `migrate` does not create that table; without it both endpoints fail.

7. **(Optional) Create an admin user** to use the Django admin at `/admin/`:

   ```bash
   python manage.py createsuperuser
   ```

8. **(Optional) Seed demo data**, six offers, five reviews and the guest
   accounts the frontend expects:

   ```bash
   python manage.py seed_demo
   ```

   The command is idempotent and runs in a transaction, so it can be repeated
   safely.

9. **Run the development server**

   ```bash
   python manage.py runserver
   ```

   The API is now available at `http://127.0.0.1:8000/`.

The project needs PostgreSQL: `settings.py` stops with an error when
`DB_NAME` is missing, because the portfolio assistant stores its vectors with
pgvector. Everything else defaults to development mode (`DEBUG=True`), and
production settings are switched on purely through the `.env` file.

---

## Tests

Run the full test suite:

```bash
python manage.py test
```

Measure test coverage (target: **≥ 95 %**):

```bash
coverage run --source=auth_app,offers_app,orders_app,reviews_app,base_app,assistant_app --omit='*/migrations/*,*/tests/*' manage.py test
coverage report
```

---

## Authentication

The API uses **token authentication**. Register or log in to receive a token,
then send it with every authenticated request in the `Authorization` header:

```
Authorization: Token <your-token>
```

Registration and login responses both return:

```json
{
  "token": "...",
  "username": "max",
  "email": "max@example.com",
  "user_id": 1
}
```

> **Note:** logging in is done with the `username`, not the email address.

---

## API Documentation

Interactive, auto-generated API documentation is available while the server is
running:

| View       | URL                            |
| ---------- | ------------------------------ |
| Swagger UI | `/api/schema/swagger-ui/`      |
| ReDoc      | `/api/schema/redoc/`           |
| Raw schema | `/api/schema/`                 |

---

## API Endpoints

Base path: `/api/`

### Authentication

| Method | Endpoint          | Description                | Auth |
| ------ | ----------------- | -------------------------- | ---- |
| POST   | `/registration/`  | Create a new user          | No   |
| POST   | `/login/`         | Log in and obtain a token  | No   |

### Profiles

| Method | Endpoint                  | Description                     | Permission     |
| ------ | ------------------------- | ------------------------------- | -------------- |
| GET    | `/profile/{pk}/`          | Profile detail                  | Authenticated  |
| PATCH  | `/profile/{pk}/`          | Update own profile              | Owner only     |
| GET    | `/profiles/business/`     | List all business profiles      | Authenticated  |
| GET    | `/profiles/customer/`     | List all customer profiles      | Authenticated  |

### Offers

| Method | Endpoint               | Description                              | Permission     |
| ------ | ---------------------- | ---------------------------------------- | -------------- |
| GET    | `/offers/`             | List offers (filter/search/order, paged) | Public         |
| POST   | `/offers/`             | Create an offer (exactly 3 details)      | Business only  |
| GET    | `/offers/{id}/`        | Offer detail                             | Authenticated  |
| PATCH  | `/offers/{id}/`        | Update an offer                          | Creator only   |
| DELETE | `/offers/{id}/`        | Delete an offer                          | Creator only   |
| GET    | `/offerdetails/{id}/`  | Single offer detail                      | Authenticated  |

### Orders

| Method | Endpoint                                    | Description                    | Permission        |
| ------ | ------------------------------------------- | ------------------------------ | ----------------- |
| GET    | `/orders/`                                  | List the user's orders         | Authenticated     |
| POST   | `/orders/`                                  | Create an order from a detail  | Customer only     |
| PATCH  | `/orders/{id}/`                             | Update the order status        | Business only     |
| DELETE | `/orders/{id}/`                             | Delete an order                | Admin / staff     |
| GET    | `/order-count/{business_user_id}/`          | Count of in-progress orders    | Authenticated     |
| GET    | `/completed-order-count/{business_user_id}/`| Count of completed orders      | Authenticated     |

### Reviews

| Method | Endpoint          | Description                          | Permission     |
| ------ | ----------------- | ------------------------------------ | -------------- |
| GET    | `/reviews/`       | List reviews (filter / order)        | Authenticated  |
| POST   | `/reviews/`       | Create a review (one per business)   | Customer only  |
| PATCH  | `/reviews/{id}/`  | Update a review                      | Creator only   |
| DELETE | `/reviews/{id}/`  | Delete a review                      | Creator only   |

### Base Info

| Method | Endpoint       | Description                    | Permission |
| ------ | -------------- | ------------------------------ | ---------- |
| GET    | `/base-info/`  | Platform-wide statistics       | Public     |

---

## Conventions & Notes

- **User model:** The project uses a custom user (`auth_app.User`, extending
  `AbstractUser`). Profile fields (`first_name`, `last_name`, `location`, `tel`,
  `description`, `working_hours`) live directly on the user.
- **User `type`:** one of `customer` or `business`.
- **Profile fields are never `null`:** missing values are returned as empty
  strings `""`.
- **Offer `offer_type`:** one of `basic`, `standard`, `premium`. Every offer has
  exactly three details, one per type.
- **Order `status`:** one of `in_progress`, `completed`, `cancelled`.
- **Orders are snapshots:** creating an order copies the chosen offer detail's
  fields (title, price, features, …); there is no foreign key back to the detail,
  so later changes to the offer do not affect existing orders.
- **Reviews:** a customer may leave at most one review per business user.
- **`average_rating`** in the base-info response is rounded to one decimal place.
- **Offers list query params:** `creator_id`, `min_price`, `max_delivery_time`,
  `search` (title/description), `ordering` (`updated_at` | `min_price`) and
  `page_size`. The response is paginated (`count`, `next`, `previous`, `results`).

---

## Portfolio Assistant

Besides the Coderr API, this backend serves the assistant on my portfolio
site: visitors ask questions about me and my projects, and the answer comes
from a knowledge base I maintain instead of being made up. The feature is
under construction and not live yet.

The pipeline, from the knowledge base to the answer:

1. `assistant_app/knowledge/*.md` holds the knowledge base, cut into sections
   at every `##` heading.
2. `python manage.py build_index` embeds every section through the
   [embedding service](embedding_service/README.md) and stores the vectors in
   PostgreSQL with pgvector.
3. `POST /api/assistant/` with `{"question": "...", "lang": "de"}` (`lang` is
   the language of the page, `de` or `en`) answers a pure greeting
   such as "Hallo" right away with `{"kind": "greeting"}`. Every other
   question goes to [Laya](laya_service/README.md), a small classifier for
   jailbreak attempts, which answers `403` if its score reaches
   `LAYA_THRESHOLD` (0.8). Then the five closest sections are searched, and
   only those with a cosine similarity of at least
   `ASSISTANT_MIN_SIMILARITY` (0.76) are kept. Without any, the answer is
   `{"kind": "off_topic"}` and no language model is called. Otherwise Claude
   writes the answer from these sections in the language of the page:
   `{"kind": "answer", "answer": "...", "answered": true, "sources": [...]}`.
   `answered` is false when the sections do not cover the question, so the
   page can point to the contact form.
4. `python manage.py evaluate_retrieval` checks a fixed list of questions, in
   German and English, against the sections they should find, and counts the
   questions on and off topic below the similarity threshold.
5. `python manage.py evaluate_guard` sends the same questions and a list of
   attacks through Laya and reports false alarms and missed attacks.
6. `python manage.py evaluate_answers` sends 33 fixed questions (on topic,
   off topic and attacks) through search and Claude, once per model profile,
   and prints every answer with its tokens, cost and time. Without `--run` it
   only shows a cost estimate, because every run costs real money.

Laya is a cheap pre-filter against obvious attacks, not a security boundary.
Measured with `evaluate_guard`, it blocks none of the 49 questions on topic
and catches 8 of 15 attacks; quiet attacks without typical jailbreak wording
get through. The threshold is a trade-off: a lower one also blocked genuine
questions about AI, which is worse for a portfolio than a missed attack,
because the knowledge base holds only public content.

Two throttles limit the questions: 20 per hour per client address, taken
from the `X-Real-IP` header that Nginx sets, and 200 per day for all clients
together, which caps the cost even when many addresses take part. An address
over its own limit does not use up the shared quota: the view stops at the
first throttle that refuses, while DRF by default asks every throttle.

The similarity threshold is a coarse filter as well. It stops 11 of 24
questions off topic and none of the 49 on topic, but only general knowledge
questions score that low. Realistic off-topic requests such as coding help
score higher than many genuine questions, so they are left to the language
model's instructions.

The model was chosen by measurement, not by name. Claude Haiku 4.5, Claude
Sonnet 5 and Sonnet 5 with thinking all resisted every one of the 14 attacks
in `evaluate_answers`, including the quiet ones Laya lets through; Haiku cost
a third and answered twice as fast. Three more rounds on Haiku fixed what the
answers showed: the answer language now comes from the page instead of being
guessed by the model, the prompt forbids praise that the sources do not
contain and promises on my behalf, and `temperature` 0 stopped
answers from varying between runs and mixing up details. The profile is set
with `ASSISTANT_LLM_PROFILE` (default `haiku`).

The endpoint fails closed. It answers `503` when Laya, the embedding service
or Claude does not respond, and unless `ASSISTANT_ENABLED=True` is set. Only
the Laya scores and the token counts of a request are logged, never its
text; the question itself is sent to Anthropic to be answered. Locally Laya and the
embedding service each run in their own terminal, see their READMEs.

---

## Deployment

The live instance runs on a VPS I set up and maintain myself: Ubuntu 24.04,
Nginx as the reverse proxy, Gunicorn serving Django over a Unix socket,
PostgreSQL as the database and TLS certificates from Let's Encrypt. Database
and media backups run nightly through a systemd timer.

The complete runbook is in [DEPLOYMENT.md](DEPLOYMENT.md): every step from an
empty server to the running site, the configuration files, and a section on
the mistakes that actually happened along the way.
