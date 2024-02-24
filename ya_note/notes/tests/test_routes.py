from http import HTTPStatus

from django.contrib.auth import get_user, get_user_model
from django.urls import reverse

from notes.tests.core import (ADD, DELETE, DETAIL, EDIT, HOME, LIST, LOGIN,
                              LOGOUT, SIGNUP, SUCCESS, SetUpTestData)

User = get_user_model()


class TestRoutes(SetUpTestData):

    def test_pages_availability_for_anonymous_user(self):
        urls = (
            HOME,
            LOGIN,
            LOGOUT,
            SIGNUP,
        )
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_auth_user(self):
        urls = (
            LIST,
            SUCCESS,
            ADD,
        )
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_different_users(self):
        users_statuses = (
            (self.author_client, HTTPStatus.OK),
            (self.reader_client, HTTPStatus.NOT_FOUND),
        )
        urls = (
            DETAIL,
            EDIT,
            DELETE,
        )
        for user, status in users_statuses:
            for name in urls:
                with self.subTest(user=get_user(user), name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = user.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirects(self):
        login_url = reverse(LOGIN)
        urls = (
            (LIST, None),
            (SUCCESS, None),
            (ADD, None),
            (DETAIL, (self.note.slug,)),
            (EDIT, (self.note.slug,)),
            (DELETE, (self.note.slug,)),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
