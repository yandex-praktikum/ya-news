"""Фикстуры news."""

# news/pytest_tests/conftest.py
from datetime import timedelta

import pytest
from django.conf import settings
from django.test.client import Client
from django.utils import timezone

from news.models import Comment, News


@pytest.fixture
def author(db, django_user_model):
    """Создаём автора."""
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(db, django_user_model):
    """Создаём обычного пользователя."""
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    """Клиент, залогиненный под автором."""
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    """Клиент, залогиненный под не-автором."""
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news(db):
    """Создаём новость."""
    return News.objects.create(
        title='Заголовок',
        text='Текст новости',
    )


@pytest.fixture
def comment(news, author):
    """Создаём комментарий к новости от имени автора."""
    return Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария',
    )


@pytest.fixture
def many_news(db):
    """Создаём новостей на одну больше, чем влезает на главную."""
    today = timezone.now()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index),
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(all_news)


@pytest.fixture
def many_comments(news, author):
    """Создаём десять комментариев с разными временными метками."""
    now = timezone.now()
    for index in range(10):
        comment = Comment.objects.create(
            news=news, author=author, text=f'Текст {index}',
        )
        # Сдвигаем время создания, чтобы даты различались.
        comment.created = now + timedelta(days=index)
        comment.save()


@pytest.fixture
def form_data():
    """Данные для POST-запросов: текст комментария, отличный от фикстурного."""
    return {'text': 'Новый текст комментария'}
