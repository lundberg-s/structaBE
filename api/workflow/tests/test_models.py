from django.test import TestCase
from workflow.tests.factory import create_tenant, create_user, create_ticket, create_comment, create_attachment
from workflow.models import Ticket, Comment, Attachment

class TicketModelTests(TestCase):
    def setUp(self):
        self.tenant = create_tenant('TenantA')
        self.user = create_user(self.tenant, username='userA', password='passA')

    def test_create_ticket(self):
        ticket = create_ticket(self.tenant, self.user, title='Model Ticket')
        self.assertEqual(ticket.title, 'Model Ticket')
        self.assertEqual(ticket.tenant, self.tenant)
        self.assertEqual(ticket.created_by, self.user)

    def test_create_comment(self):
        ticket = create_ticket(self.tenant, self.user, title='Comment Ticket')
        comment = create_comment(ticket, self.user, content='A model comment')
        self.assertEqual(comment.content, 'A model comment')
        self.assertEqual(comment.work_item, ticket)
        self.assertEqual(comment.tenant, self.tenant)

    def test_create_attachment(self):
        ticket = create_ticket(self.tenant, self.user, title='Attachment Ticket')
        attachment = create_attachment(ticket, self.user, filename='test.txt', content=b'hello world')
        self.assertEqual(attachment.filename, 'test.txt')
        self.assertEqual(attachment.work_item, ticket)
        self.assertEqual(attachment.tenant, self.tenant) 