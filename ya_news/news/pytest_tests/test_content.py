from datetime import date

import pytest
from django.conf import settings
from django.utils import timezone

from .conftest import URL


@pytest.mark.django_db
def test_news_count_order(client, news_list):
    response = client.get(URL.home)
    object_list = list(response.context['object_list'])
    assert isinstance(object_list[0].date, date)
    assert object_list == sorted(
        object_list, key=lambda x: x.date, reverse=True
    )


@pytest.mark.django_db
def test_news_count_on_home_page(client, news_list):
    response = client.get(URL.home)
    object_list = list(response.context['object_list'])
    assert len(object_list) == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_comments_order(client, news, comments_list):
    response = client.get(URL.detail)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = list(news.comment_set.all())
    assert isinstance(all_comments[0].created, timezone.datetime)
    assert all_comments == sorted(all_comments, key=lambda x: x.created)


@pytest.mark.django_db
def test_client_has_form(client, admin_client, news):
    response = client.get(URL.detail)
    admin_response = admin_client.get(URL.detail)
    assert ('form' in admin_response.context)
    assert ('form' not in response.context)
