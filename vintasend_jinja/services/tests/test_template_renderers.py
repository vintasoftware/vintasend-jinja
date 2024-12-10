import uuid
from unittest import TestCase

from jinja2 import Environment, FileSystemLoader, select_autoescape
from vintasend.constants import NotificationStatus, NotificationTypes
from vintasend.services.dataclasses import Notification

from vintasend_jinja.services.notification_template_renderers.jinja_templated_email_renderer import (
    JinjaTemplatedEmailRenderer,
)


class JinjaTemplatedEmailRendererTestCase(TestCase):
    def create_notification(self) -> Notification:
        return Notification(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            notification_type=NotificationTypes.EMAIL.value,
            title="Test Notification",
            body_template="vintasend_jinja/emails/test/test_templated_email_body.html",
            context_name="test_context",
            context_kwargs={},
            send_after=None,
            subject_template="vintasend_jinja/emails/test/test_templated_email_subject.txt",
            preheader_template="vintasend_jinja/emails/test/test_templated_email_preheader.html",
            status=NotificationStatus.PENDING_SEND.value,
        )

    def create_notification_context(self, notification: Notification):
        return {
            "test_subject": "this_is_my_test_subject_string",
            "test_preheader": "this_is_my_test_preheader_string",
            "test_body": "this_is_my_test_body_string",
        }

    def test_render(self):
        renderer = JinjaTemplatedEmailRenderer(environment=Environment(
            loader=FileSystemLoader(["vintasend_jinja/templates"]),
            autoescape=select_autoescape()
        ))
        notification = self.create_notification()
        context = self.create_notification_context(notification)
        email = renderer.render(notification, context)
        assert "this_is_my_test_subject_string" in email.subject
        assert "this_is_my_test_preheader_string" in email.body
        assert "this_is_my_test_body_string" in email.body
