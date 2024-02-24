from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from notes.models import Note

User = get_user_model()


HOME = 'notes:home'
LOGIN = 'users:login'
LOGOUT = 'users:logout'
SIGNUP = 'users:signup'
LIST = 'notes:list'
SUCCESS = 'notes:success'
ADD = 'notes:add'
DETAIL = 'notes:detail'
EDIT = 'notes:edit'
DELETE = 'notes:delete'


class SetUpTestData(TestCase):

    @classmethod
    def setUpTestData(cls, client_form_content=False):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель простой')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='note-slug',
            author=cls.author,
        )
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug'
        }
