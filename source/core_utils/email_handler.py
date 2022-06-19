import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def send_email(
    emails_to,
    subject,
    text,
    cc=None,
    html=None,
    reply_to=None,
    attachment_name=None,
    attachment_path=None,
    attachment=None,
    raise_exception=False,
    from_email=settings.MAILGUN_DEFAULT_FROM_EMAIL,
):
    try:
        data = {
            "from": f"Janio <{from_email}>",
            "to": emails_to,
            "subject": subject,
            "text": text,
        }

        if cc is not None:
            data["cc"] = cc

        if html is not None:
            data["html"] = html

        if reply_to is not None:
            data["h:Reply-To"] = reply_to

        if attachment_name is not None:
            with open(attachment_path, "rb") as attachment_file:
                attachment_data = (attachment_name, attachment_file)
                res = requests.post(
                    settings.MAILGUN_GENERAL_URL,
                    auth=("api", settings.MAILGUN_SECRET_KEY),
                    data=data,
                    files={"attachment": attachment_data},
                )
        elif attachment:
            res = requests.post(
                settings.MAILGUN_GENERAL_URL,
                auth=("api", settings.MAILGUN_SECRET_KEY),
                data=data,
                files={
                    "attachment": attachment
                },  # attachment must be tuple of (file_name, file_data)
            )
        else:
            res = requests.post(
                settings.MAILGUN_GENERAL_URL,
                auth=("api", settings.MAILGUN_SECRET_KEY),
                data=data,
            )
        return res

    except Exception as e:
        logger.error(e)
        if raise_exception:
            raise e
