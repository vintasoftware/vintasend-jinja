from typing import TYPE_CHECKING

from jinja2 import Environment
from vintasend.exceptions import (
    NotificationBodyTemplateRenderingError,
    NotificationPreheaderTemplateRenderingError,
    NotificationSubjectTemplateRenderingError,
)
from vintasend.services.dataclasses import Notification
from vintasend.services.notification_template_renderers.base_templated_email_renderer import (
    BaseTemplatedEmailRenderer,
    TemplatedEmail,
)


if TYPE_CHECKING:
    from vintasend.services.notification_service import NotificationContextDict


class JinjaTemplatedEmailRenderer(BaseTemplatedEmailRenderer):
    def __init__(self, environment: Environment):
        self.env = environment

    def render(
        self, notification: Notification, context: "NotificationContextDict"
    ) -> TemplatedEmail:
        subject_template_str = notification.subject_template
        body_template_str = notification.body_template
        preheader_template_str = notification.preheader_template

        try:
            preheader_template = self.env.get_template(
                preheader_template_str,
            )
            context["private_preheader"] = preheader_template.render(**context)
        except Exception as e:  # noqa: BLE001
            raise NotificationPreheaderTemplateRenderingError(
                "Failed to render preheader template"
            ) from e

        try:
            subject_template = self.env.get_template(
                subject_template_str,
            )
            subject = subject_template.render(**context)
        except Exception as e:  # noqa: BLE001
            raise NotificationSubjectTemplateRenderingError(
                "Failed to render subject template"
            ) from e

        try:
            body_template = self.env.get_template(
                body_template_str,
            )
            body = body_template.render(**context)
        except Exception as e:  # noqa: BLE001
            raise NotificationBodyTemplateRenderingError("Failed to render body template") from e

        return TemplatedEmail(subject=subject, body=body)
