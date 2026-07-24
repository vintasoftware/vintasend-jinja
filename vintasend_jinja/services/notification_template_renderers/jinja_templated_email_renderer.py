from typing import TYPE_CHECKING

from jinja2 import Environment
from vintasend.exceptions import (
    NotificationBodyTemplateRenderingError,
    NotificationPreheaderTemplateRenderingError,
    NotificationSubjectTemplateRenderingError,
)
from vintasend.services.dataclasses import Notification, OneOffNotification
from vintasend.services.notification_template_renderers.base_templated_email_renderer import (
    BaseTemplatedEmailRenderer,
    EmailTemplateContent,
    TemplatedEmail,
)


if TYPE_CHECKING:
    from vintasend.services.dataclasses import NotificationContextDict


class JinjaTemplatedEmailRenderer(BaseTemplatedEmailRenderer):
    def __init__(self, environment: Environment):
        self.env = environment

    def render(
        self,
        notification: "Notification | OneOffNotification",
        context: "NotificationContextDict",
        **kwargs,
    ) -> TemplatedEmail:
        return self._render_from_templates(
            notification=notification,
            subject_template=notification.subject_template,
            body_template=notification.body_template,
            preheader_template=notification.preheader_template,
            context=context,
        )

    def render_from_template_content(
        self,
        notification: "Notification | OneOffNotification",
        template_content: EmailTemplateContent,
        context: "NotificationContextDict",
        **kwargs,
    ) -> TemplatedEmail:
        """Render from supplied template content instead of the notification's stored templates.

        Used to reproduce a past render (a preview or audit) from an older subject/body/preheader
        pair -- typically paired with a notification's stored ``context_used`` -- without touching
        the notification's currently configured templates. The context is used verbatim; no
        context generation happens here.
        """
        return self._render_from_templates(
            notification=notification,
            subject_template=template_content.subject_template,
            body_template=template_content.body_template,
            preheader_template=template_content.preheader_template or "",
            context=context,
        )

    def _render_from_templates(
        self,
        notification: "Notification | OneOffNotification",
        subject_template: str,
        body_template: str,
        preheader_template: str,
        context: "NotificationContextDict",
    ) -> TemplatedEmail:
        rendered_preheader: str | None = None
        if preheader_template:
            try:
                preheader = self.env.get_template(preheader_template).render(**context)
            except Exception as e:  # noqa: BLE001
                raise NotificationPreheaderTemplateRenderingError(
                    "Failed to render preheader template"
                ) from e
            context["private_preheader"] = preheader
            rendered_preheader = preheader

        try:
            subject = self.env.get_template(subject_template).render(**context)
        except Exception as e:  # noqa: BLE001
            raise NotificationSubjectTemplateRenderingError(
                "Failed to render subject template"
            ) from e

        try:
            body = self.env.get_template(body_template).render(**context)
        except Exception as e:  # noqa: BLE001
            raise NotificationBodyTemplateRenderingError("Failed to render body template") from e

        return TemplatedEmail(subject=subject, body=body, preheader=rendered_preheader)
