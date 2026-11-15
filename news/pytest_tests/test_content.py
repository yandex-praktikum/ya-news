"""Тесты контента проекта."""

# news/pytest_tests/test_content.py
import pytest
from django.conf import settings
from django.urls import reverse

from news.forms import CommentForm

# Все тесты файла работают с базой — ставим маркер на весь модуль.
pytestmark = pytest.mark.django_db


def test_news_count(client, many_news):
    """1C. На главной странице ровно NEWS_COUNT_ON_HOME_PAGE новостей."""
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    news_count = object_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(client, many_news):
    """2C. Новости сортируются от новых к старым."""
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_comments_order(client, news, many_comments):
    """3C. Комментарии выводятся от старых к новым."""
    url = reverse('news:detail', args=(news.pk,))
    response = client.get(url)
    # Объект новости лежит в контексте под именем модели.
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    # Менять порядок сортировки не надо: старые должны идти первыми.
    assert all_timestamps == sorted(all_timestamps)


@pytest.mark.parametrize(
    'parametrized_client, form_in_context',
    (
        (pytest.lazy_fixture('client'), False),
        (pytest.lazy_fixture('author_client'), True),
    ),
)
def test_comment_form_availability(parametrized_client, form_in_context, news):
    """4C. Форма комментария доступна только авторизованному пользователю."""
    url = reverse('news:detail', args=(news.pk,))
    response = parametrized_client.get(url)
    assert ('form' in response.context) is form_in_context
    # Если форма есть в контексте — это именно CommentForm.
    if form_in_context:
        assert isinstance(response.context['form'], CommentForm)
