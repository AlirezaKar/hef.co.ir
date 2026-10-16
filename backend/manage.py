#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

    # Force English language for management commands (keeps web UI in Persian)
    os.environ['DJANGO_LANGUAGE'] = 'en'

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    # Override LANGUAGE_CODE for CLI commands only
    from django.conf import settings
    settings.LANGUAGE_CODE = 'en'

    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
