"""Management command that fills the database with demo data."""

from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from auth_app.models import User
from offers_app.models import Offer, OfferDetail
from reviews_app.models import Review

BUSINESS_USERS = [
    {
        "username": "kevin",
        "password": "asdasd24",
        "first_name": "Kevin",
        "last_name": "Anbieter",
        "email": "kevin@example.com",
        "location": "Berlin",
        "tel": "030 1234567",
        "working_hours": "9 - 17",
        "description": (
            "Fullstack-Entwickler mit Fokus auf Django und Angular."
        ),
    },
    {
        "username": "lisa_design",
        "password": "demo-lisa-2026",
        "first_name": "Lisa",
        "last_name": "Hoffmann",
        "email": "lisa@example.com",
        "location": "Hamburg",
        "tel": "040 9876543",
        "working_hours": "10 - 18",
        "description": (
            "UI/UX Designerin. Ich gestalte Interfaces, die sich von "
            "selbst erklären."
        ),
    },
    {
        "username": "thomas_ops",
        "password": "demo-thomas-2026",
        "first_name": "Thomas",
        "last_name": "Berger",
        "email": "thomas@example.com",
        "location": "München",
        "tel": "089 4567890",
        "working_hours": "8 - 16",
        "description": (
            "DevOps Engineer. Container, Pipelines und Monitoring für "
            "kleine Teams."
        ),
    },
]

CUSTOMER_USERS = [
    {
        "username": "andrey",
        "password": "asdasd",
        "first_name": "Andrey",
        "last_name": "Kunde",
        "email": "andrey@example.com",
        "location": "Hamburg",
        "tel": "040 123456",
        "description": "Gastzugang Kundensicht.",
    },
    {
        "username": "maria_k",
        "password": "demo-maria-2026",
        "first_name": "Maria",
        "last_name": "Klein",
        "email": "maria@example.com",
        "location": "Köln",
        "tel": "0221 555444",
        "description": (
            "Gründerin, sucht Unterstützung beim Webauftritt."
        ),
    },
]


def build_tiers(prices, features, days=(14, 9, 5), revisions=(1, 3, 5)):
    """Return the three pricing tiers of an offer as dictionaries.

    Args:
        prices: Tuple of basic, standard and premium price strings.
        features: Tuple of three feature lists, one per tier.
        days: Delivery time in days per tier.
        revisions: Number of included revisions per tier.

    Returns:
        A list of three dictionaries ready for OfferDetail.
    """
    types = ("basic", "standard", "premium")
    titles = ("Basic", "Standard", "Premium")
    return [
        {
            "title": titles[index],
            "offer_type": types[index],
            "price": Decimal(prices[index]),
            "delivery_time_in_days": days[index],
            "revisions": revisions[index],
            "features": features[index],
        }
        for index in range(3)
    ]


OFFERS = [
    {
        "owner": "kevin",
        "title": "Django REST API nach deinen Anforderungen",
        "description": (
            "Ich baue dir eine saubere REST-Schnittstelle mit Django und "
            "dem Django REST Framework. Inklusive Authentifizierung, "
            "Tests und einer OpenAPI-Dokumentation, mit der dein "
            "Frontend-Team direkt arbeiten kann."
        ),
        "details": build_tiers(
            ("290", "690", "1450"),
            (
                ["3 Endpunkte", "Token-Authentifizierung",
                 "Kurzdokumentation"],
                ["8 Endpunkte", "Rollen und Berechtigungen", "Unit-Tests",
                 "OpenAPI-Dokumentation"],
                ["Unbegrenzte Endpunkte", "Rollen und Berechtigungen",
                 "Testabdeckung über 90 Prozent", "Deployment-Anleitung",
                 "Zwei Wochen Support"],
            ),
        ),
    },
    {
        "owner": "kevin",
        "title": "Fullstack Web-App mit Angular und Django",
        "description": (
            "Von der Datenbank bis zum Interface. Ich setze deine Idee "
            "als vollständige Anwendung um, responsive und mit "
            "durchdachter Nutzerführung."
        ),
        "details": build_tiers(
            ("540", "1190", "2400"),
            (
                ["Bis 3 Seiten", "Responsive Layout", "Kontaktformular"],
                ["Bis 8 Seiten", "Nutzerverwaltung", "Adminbereich",
                 "Responsive Layout"],
                ["Unbegrenzte Seiten", "Nutzerverwaltung", "Adminbereich",
                 "Automatisiertes Deployment", "Vier Wochen Support"],
            ),
            days=(21, 14, 10),
        ),
    },
    {
        "owner": "lisa_design",
        "title": "UI/UX Design für Web-Anwendungen",
        "description": (
            "Ich entwerfe Interfaces, die Nutzer ohne Erklärung "
            "verstehen. Du bekommst klickbare Prototypen und ein "
            "Designsystem, das deine Entwickler direkt umsetzen können."
        ),
        "details": build_tiers(
            ("220", "580", "1290"),
            (
                ["3 Screens", "Wireframes", "Eine Korrekturrunde"],
                ["8 Screens", "Klickbarer Prototyp", "Designsystem",
                 "Drei Korrekturrunden"],
                ["Unbegrenzte Screens", "Klickbarer Prototyp",
                 "Vollständiges Designsystem",
                 "Nutzertest mit fünf Personen", "Übergabe-Workshop"],
            ),
            days=(10, 7, 5),
        ),
    },
    {
        "owner": "lisa_design",
        "title": "Logo und Markenauftritt",
        "description": (
            "Ein Logo ist erst fertig, wenn es auf dem Handy genauso "
            "funktioniert wie auf einem Messestand. Du bekommst alle "
            "Formate und eine kurze Anleitung zur Verwendung."
        ),
        "details": build_tiers(
            ("150", "390", "820"),
            (
                ["Zwei Entwürfe", "Logo als PNG und SVG"],
                ["Vier Entwürfe", "Alle Dateiformate",
                 "Farb- und Schriftpalette"],
                ["Sechs Entwürfe", "Alle Dateiformate", "Markenhandbuch",
                 "Visitenkarte und Briefkopf"],
            ),
            days=(7, 5, 4),
        ),
    },
    {
        "owner": "thomas_ops",
        "title": "Docker-Setup und CI/CD-Pipeline",
        "description": (
            "Dein Projekt läuft bei jedem im Team gleich und wird per "
            "Knopfdruck ausgerollt. Ich richte Container, Pipeline und "
            "die nötigen Prüfschritte ein."
        ),
        "details": build_tiers(
            ("320", "740", "1580"),
            (
                ["Dockerfile", "Compose-Datei für die Entwicklung"],
                ["Dockerfile", "Compose-Setup", "GitHub-Actions-Pipeline",
                 "Automatische Tests"],
                ["Vollständiges Container-Setup",
                 "Pipeline mit Staging und Live", "Monitoring und Alarme",
                 "Notfall-Rollback", "Einweisung für das Team"],
            ),
            days=(12, 8, 6),
        ),
    },
    {
        "owner": "thomas_ops",
        "title": "Server-Deployment für Django-Projekte",
        "description": (
            "Ich bringe deine Django-Anwendung auf einen eigenen Server: "
            "Gunicorn, Nginx, PostgreSQL, HTTPS und automatische "
            "Backups. Danach weißt du, wo du hinschauen musst, wenn "
            "etwas nicht läuft."
        ),
        "details": build_tiers(
            ("260", "620", "1240"),
            (
                ["Grundinstallation", "HTTPS-Zertifikat"],
                ["Grundinstallation", "PostgreSQL", "HTTPS",
                 "Systemdienste mit Autostart"],
                ["Komplettes Setup", "Automatische Backups", "Monitoring",
                 "Runbook für den Betrieb", "Zwei Wochen Support"],
            ),
            days=(9, 6, 4),
        ),
    },
]

REVIEWS = [
    {
        "business": "kevin",
        "reviewer": "andrey",
        "rating": 5,
        "description": (
            "Sehr strukturierte Arbeit. Die Schnittstelle war genau so "
            "dokumentiert wie abgesprochen, und mein Frontend-Entwickler "
            "konnte ohne Rückfragen starten."
        ),
    },
    {
        "business": "kevin",
        "reviewer": "maria_k",
        "rating": 4,
        "description": (
            "Fachlich stark und zuverlässig. Die Rückmeldungen kamen "
            "manchmal erst am Folgetag, das Ergebnis stimmt aber."
        ),
    },
    {
        "business": "lisa_design",
        "reviewer": "andrey",
        "rating": 5,
        "description": (
            "Hat aus einer vagen Idee ein klares Konzept gemacht. Der "
            "Prototyp hat uns intern viele Diskussionen erspart."
        ),
    },
    {
        "business": "lisa_design",
        "reviewer": "maria_k",
        "rating": 5,
        "description": (
            "Das Designsystem war eine echte Erleichterung. Wir "
            "gestalten neue Seiten jetzt selbst, ohne dass es "
            "auseinanderfällt."
        ),
    },
    {
        "business": "thomas_ops",
        "reviewer": "maria_k",
        "rating": 4,
        "description": (
            "Deployment läuft seit Wochen stabil. Die Einweisung hätte "
            "etwas ausführlicher sein können."
        ),
    },
]


class Command(BaseCommand):
    """Create demo users, offers and reviews for a fresh installation."""

    help = (
        "Fill the database with demo users, offers and reviews. "
        "Running it repeatedly updates the existing records instead of "
        "creating duplicates."
    )

    @transaction.atomic
    def handle(self, *args, **options):
        """Run the whole seeding process inside one transaction."""
        users = {}
        users.update(self._seed_users(BUSINESS_USERS, "business"))
        users.update(self._seed_users(CUSTOMER_USERS, "customer"))
        self._seed_offers(users)
        self._seed_reviews(users)
        self._report_totals()

    def _seed_users(self, entries, user_type):
        """Create or update the given users and return them by username."""
        created_users = {}
        for entry in entries:
            data = dict(entry)
            password = data.pop("password")
            data["type"] = user_type
            user, created = User.objects.get_or_create(
                username=data["username"], defaults=data,
            )
            for field, value in data.items():
                setattr(user, field, value)
            user.set_password(password)
            user.save()
            created_users[user.username] = user
            self._log(created, f"{user.username} ({user_type})")
        return created_users

    def _seed_offers(self, users):
        """Create or update all offers including their pricing tiers."""
        for entry in OFFERS:
            offer, created = Offer.objects.get_or_create(
                user=users[entry["owner"]],
                title=entry["title"],
                defaults={"description": entry["description"]},
            )
            offer.description = entry["description"]
            offer.save()
            for detail in entry["details"]:
                OfferDetail.objects.update_or_create(
                    offer=offer,
                    offer_type=detail["offer_type"],
                    defaults=detail,
                )
            self._log(created, f"Angebot: {offer.title}")

    def _seed_reviews(self, users):
        """Create or update all reviews."""
        for entry in REVIEWS:
            review, created = Review.objects.get_or_create(
                business_user=users[entry["business"]],
                reviewer=users[entry["reviewer"]],
                defaults={
                    "rating": entry["rating"],
                    "description": entry["description"],
                },
            )
            review.rating = entry["rating"]
            review.description = entry["description"]
            review.save()
            label = (
                f"Bewertung: {entry['reviewer']} -> {entry['business']} "
                f"({entry['rating']}/5)"
            )
            self._log(created, label)

    def _log(self, created, label):
        """Write one status line, green when a record was created."""
        prefix = "angelegt     " if created else "aktualisiert "
        style = self.style.SUCCESS if created else self.style.WARNING
        self.stdout.write(style(prefix) + label)

    def _report_totals(self):
        """Write the resulting record counts."""
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Fertig."))
        self.stdout.write(f"  Nutzer:      {User.objects.count()}")
        self.stdout.write(f"  Angebote:    {Offer.objects.count()}")
        self.stdout.write(f"  Pakete:      {OfferDetail.objects.count()}")
        self.stdout.write(f"  Bewertungen: {Review.objects.count()}")
