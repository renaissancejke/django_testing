from django.contrib.auth import get_user_model
from django.urls import reverse

from notes.forms import NoteForm
from notes.tests.core import ADD, EDIT, LIST, SetUpTestData

User = get_user_model()


class TestRoutes(SetUpTestData):

    def test_notes_list_for_different_users(self):
        users_statuses = (
            (self.author_client, True),
            (self.reader_client, False),
        )
        for user, note_in_list in users_statuses:
            with self.subTest():
                url = reverse(LIST)
                response = user.get(url)
                self.assertIs((self.note in response.context['object_list']),
                              note_in_list)

    def test_pages_contains_form(self):
        urls = (
            (ADD, None),
            (EDIT, (self.note.slug,)),
        )
        for name, args in urls:
            with self.subTest():
                url = reverse(name, args=args)
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
