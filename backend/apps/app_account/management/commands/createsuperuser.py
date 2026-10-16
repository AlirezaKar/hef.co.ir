"""
Custom createsuperuser command.

Overrides Django's built-in to:
  - require only username and password (email, phone, etc. are optional)
  - use English for all prompts and messages
"""

from django.contrib.auth.management.commands import createsuperuser as _base
from django.core.exceptions import ValidationError
from django.db import DatabaseError


class Command(_base.Command):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def handle(self, *args, **options):
        database = options["database"]
        user_data = {}
        username_field = self.UserModel.USERNAME_FIELD  # "username"

        # ── username (required) ────────────────────────────────
        default_username = options.get(username_field)
        if default_username:
            username = default_username
        else:
            while True:
                username = input("Username: ").strip()
                if not username:
                    self.stderr.write("Error: This field cannot be blank.")
                    continue
                break

        user_data[username_field] = username

        # ── password (required) ────────────────────────────────
        password = None
        if not options["interactive"]:
            password = options.get("password")

        if password is None:
            while True:
                import getpass

                password = getpass.getpass()
                password2 = getpass.getpass("Password (again): ")
                if password != password2:
                    self.stderr.write("Error: Your passwords didn't match.")
                    password = None
                    continue
                if not password:
                    self.stderr.write("Error: Blank passwords aren't allowed.")
                    continue
                break

        user = self.UserModel(**user_data)
        user.set_password(password)

        # ── optional fields (only set when running non-interactively) ──
        if not options["interactive"]:
            for field_name in ("email", "phone_number", "first_name", "last_name"):
                if options.get(field_name):
                    setattr(user, field_name, options[field_name])

        try:
            user.save()
        except DatabaseError as e:
            self.stderr.write("Error: %s" % str(e))
            return

        self.stdout.write(
            self.style.SUCCESS(
                f'Superuser "{username}" created successfully.'
            )
        )
