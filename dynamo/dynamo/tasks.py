from celery import shared_task
from celery.utils.log import get_task_logger

from templated_email import send_templated_mail

from dynamo import settings

logger = get_task_logger(__name__)

"""
WRITTEN BY TOM
"""


@shared_task()
def send_email(mail_props) -> bool:
    """
    System's main email sender functionality. Is a Celery task called using
    .delay() in order to queue it (for example, send_email.delay()
    """
    logger.info("Sending email...")

    # First, check if all required arguments were passed in before starting
    if (
            "template" not in mail_props
            or "recipients" not in mail_props
            or "additional_context" not in mail_props
    ):
        logger.info(
            "Email couldn't be sent - it appears to either be missing "
            "required arguments, or contains invalid ones."
        )
        return False

    # Base context, the same for all emails
    base_context = {
        "contact_url": settings.SITE_DOMAIN,
        "site_base_url": settings.SITE_DOMAIN,
        "site_protocol": settings.SITE_PROTOCOL,
    }

    # Get the template name & recipients
    template = mail_props["template"]
    recipients = mail_props["recipients"]
    additional_context = mail_props["additional_context"]

    send_templated_mail(
        template_name=template,
        from_email=settings.DEFAULT_SYSTEM_FROM_EMAIL,
        recipient_list=recipients,
        context={**base_context, **additional_context},
    )

    #  Log what happened in case of any issues
    logger.info(
        f"Email sent successfully to {recipients}, "
        f"using the additional context: "
        f"{additional_context}, "
        f"and the {template} template."
    )

    return True
