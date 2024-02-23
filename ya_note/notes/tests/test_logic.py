from http import HTTPStatus

from django.urls import reverse
from notes.forms import WARNING
from notes.models import Note
from pytils.translit import slugify

from .core import ADD, DELETE, EDIT, LOGIN, SUCCESS, CustomTestCase


class TestLogic(CustomTestCase):

    @classmethod
    def setUpTestData(cls):
        return super().setUpTestData(client_form_content=True)

    def test_auth_user_can_create_note(self):
        url = reverse(ADD)
        response = self.author_client.post(url, data=self.form_data)
        self.assertRedirects(response, reverse(SUCCESS))
        self.assertEqual(Note.objects.count(), 2)
        new_note = Note.objects.get(slug=self.form_data['slug'])
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        url = reverse(ADD)
        login_url = reverse(LOGIN)
        expected_url = f'{login_url}?next={url}'
        response = self.client.post(url, data=self.form_data)
        self.assertRedirects(response, expected_url)
        self.assertEqual(Note.objects.count(), 1)

    def test_non_unique_slug_is_forbidden(self):
        url = reverse(ADD)
        self.form_data['slug'] = self.note.slug
        response = self.author_client.post(url, data=self.form_data)
        self.assertFormError(
            response, 'form', 'slug', errors=(self.note.slug + WARNING)
        )
        self.assertEqual(Note.objects.count(), 1)

    def test_title_to_empty_slug(self):
        url = reverse(ADD)
        del self.form_data['slug']
        response = self.author_client.post(url, data=self.form_data)
        self.assertRedirects(response, reverse(SUCCESS))
        self.assertEqual(Note.objects.count(), 2)
        new_note = Note.objects.last()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)

    def test_author_can_edit_note(self):
        url = reverse(EDIT, args=(self.note.slug,))
        response = self.author_client.post(url, data=self.form_data)
        self.assertRedirects(response, reverse(SUCCESS))
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.form_data['title'])
        self.assertEqual(self.note.text, self.form_data['text'])
        self.assertEqual(self.note.slug, self.form_data['slug'])

    def test_other_user_cant_edit_note(self):
        url = reverse('notes:edit', args=(self.note.slug,))
        response = self.reader_client.post(url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.get(id=self.note.id)
        self.assertEqual(self.note.title, note_from_db.title)
        self.assertEqual(self.note.text, note_from_db.text)
        self.assertEqual(self.note.slug, note_from_db.slug)

    def test_author_can_delete_note(self):
        url = reverse(DELETE, args=(self.note.slug,))
        response = self.author_client.post(url)
        self.assertRedirects(response, reverse(SUCCESS))
        assert Note.objects.count() == 0

    def test_other_user_cant_delete_note(self):
        url = reverse(DELETE, args=(self.note.slug,))
        response = self.reader_client.post(url)
        assert response.status_code == HTTPStatus.NOT_FOUND
        assert Note.objects.count() == 1
