from http import HTTPStatus

import pytest
from pytest_django.asserts import assertFormError, assertRedirects

from .conftest import COMMENT_TEXT, NEW_COMMENT_TEXT, URL
from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, news, form_data):
    expected_count = Comment.objects.count()
    client.post(URL.detail, data=form_data)
    comments_count = Comment.objects.count()
    assert expected_count == comments_count


@pytest.mark.django_db
def test_user_can_create_comment(author_client, author, news, form_data):
    expected_count = Comment.objects.count() + 1
    response = author_client.post(URL.detail, data=form_data)
    comments_count = Comment.objects.count()
    new_comment = Comment.objects.get()
    assertRedirects(response, f'{URL.detail}#comments')
    assert expected_count == comments_count
    assert new_comment.text == form_data['text']
    assert new_comment.author == author
    assert new_comment.news == news


@pytest.mark.django_db
@pytest.mark.parametrize('word', BAD_WORDS)
def test_user_cant_use_bad_words(author_client, news, word):
    expected_count = Comment.objects.count()
    bad_words_data = {'text': f'Какой-то текст, {word}, еще текст'}
    response = author_client.post(URL.detail, data=bad_words_data)
    comments_count = Comment.objects.count()
    assertFormError(response, form='form', field='text', errors=WARNING)
    assert expected_count == comments_count


@pytest.mark.django_db
def test_author_can_delete_comment(author_client, comment, pk_news):
    expected_count = Comment.objects.count() - 1
    response = author_client.delete(URL.delete)
    comments_count = Comment.objects.count()
    assertRedirects(response, f'{URL.detail}#comments')
    assert expected_count == comments_count


@pytest.mark.django_db
def test_user_cant_delete_comment_of_another_user(admin_client, comment):
    expected_count = Comment.objects.count()
    response = admin_client.delete(URL.delete)
    comments_count = Comment.objects.count()
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert expected_count == comments_count


@pytest.mark.django_db
def test_author_can_edit_comment(
    author, author_client, comment, pk_news, form_data
):
    expected_count = Comment.objects.count()
    response = author_client.post(URL.edit, data=form_data)
    assertRedirects(response, f'{URL.detail}#comments')
    comment.refresh_from_db()
    comments_count = Comment.objects.count()
    assert expected_count == comments_count
    assert comment.text == NEW_COMMENT_TEXT
    assert comment.author == author


@pytest.mark.django_db
def test_user_cant_edit_comment_of_another_user(
    author, admin_client, comment, pk_news, form_data
):
    expected_count = Comment.objects.count()
    response = admin_client.post(URL.edit, data=form_data)
    comment.refresh_from_db()
    comments_count = Comment.objects.count()
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert expected_count == comments_count
    assert comment.text == COMMENT_TEXT
    assert comment.author == author
