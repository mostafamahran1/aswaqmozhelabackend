import logging
import os
import threading

from django.conf import settings
from django.db import close_old_connections, transaction

logger = logging.getLogger(__name__)

_READY = False
_UNAVAILABLE = False


def send_later(topics, title, body, data=None):
    """Queue the send until the database transaction has committed."""
    payload = dict(data or {})

    def _run():
        threading.Thread(
            target=send_to_topics,
            args=(list(topics), title, body, payload),
            daemon=True,
        ).start()

    transaction.on_commit(_run)


def send_to_topics(topics, title, body, data=None):
    """Send one notification to each topic. A missing key never breaks the shop."""
    try:
        try:
            _remember(topics, title, body, data)
        except Exception:
            logger.exception('Could not store notification')

        messaging = _messaging()
        if messaging is None:
            return False

        payload = {key: str(value) for key, value in (data or {}).items()}
        messages = [
            messaging.Message(
                topic=topic,
                notification=messaging.Notification(title=title, body=body),
                data=payload,
                android=messaging.AndroidConfig(
                    priority='high',
                    notification=messaging.AndroidNotification(
                        channel_id='aswaq_alerts',
                        sound='default',
                    ),
                ),
                apns=messaging.APNSConfig(
                    payload=messaging.APNSPayload(
                        aps=messaging.Aps(sound='default'),
                    ),
                ),
            )
            for topic in topics
        ]
        messaging.send_each(messages)
        return True
    except Exception:
        logger.exception('Could not send notification to %s', topics)
        return False
    finally:
        close_old_connections()


def _remember(topics, title, body, data):
    from .models import InboxNotice

    payload = {key: str(value) for key, value in (data or {}).items()}
    kind = (payload.get('type') or 'announcement')[:30]
    InboxNotice.objects.bulk_create([
        InboxNotice(
            audience=topic,
            title=title[:120],
            body=body,
            kind=kind,
            payload=payload,
        )
        for topic in topics
    ])


def _messaging():
    global _READY, _UNAVAILABLE
    if _UNAVAILABLE:
        return None
    import firebase_admin
    from firebase_admin import credentials, messaging

    if not _READY:
        path = os.environ.get(
            'FIREBASE_CREDENTIALS',
            settings.BASE_DIR / 'firebase-service-account.json',
        )
        if not os.path.exists(path):
            logger.warning('Firebase credentials file is missing at %s', path)
            _UNAVAILABLE = True
            return None
        firebase_admin.initialize_app(credentials.Certificate(str(path)))
        _READY = True
    return messaging
