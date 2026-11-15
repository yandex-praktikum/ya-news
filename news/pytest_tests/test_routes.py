"""Тесты для тестирования маршрутов проекта."""

# news/tests/test_routes.py
from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects
from pytest_lazyfixture import lazy_fixture as lf


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    ('news:home', 'users:login', 'users:signup')
)
def test_pages_availability_for_anonymous_user(client, name):
    """1R. Доступность публичных страниц для анонимного пользователя."""
    url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


def test_logout_availability_for_anonymous_user(client):
    """2R. Страница логаута отвечает анонимному пользователю."""
    url = reverse('users:logout')
    response = client.post(url)
    assert response.status_code == HTTPStatus.OK


def test_detail_page_availability_for_anonymous_user(client, news):
    """3R. Страница новости доступна любому пользователю без логина."""
    url = reverse('news:detail', args=(news.pk,))
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    # Чужому пользователю страницы комментариев недоступны — 404,
    # автору — 200.
    [
        (lf('not_author_client'), HTTPStatus.NOT_FOUND),
        (lf('author_client'), HTTPStatus.OK)
    ],
)
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_comment_pages_availability_for_different_users(
        parametrized_client, name, comment, expected_status
):
    """4R. Доступ автора к своим комментариям (200), к чужим (404)."""
    url = reverse(name, args=(comment.pk,))
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_redirects(client, name, comment):
    """5R. Редирект анонимного пользователя со страниц комментариев."""
    login_url = reverse('users:login')
    url = reverse(name, args=(comment.pk,))
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
