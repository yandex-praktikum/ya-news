"""Тесты логики проекта."""

# news/pytest_tests/test_logic.py
from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


def test_anonymous_user_cant_create_comment(client, form_data, news):
    """1L. Анонимный пользователь не может создать комментарий."""
    url = reverse('news:detail', args=(news.pk,))
    response = client.post(url, data=form_data)
    # Анонима отправляет на страницу логина с параметром next.
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    # Комментарий при этом не создан.
    assert Comment.objects.count() == 0


def test_user_can_create_comment(author_client, author, form_data, news):
    """2L. Залогиненный пользователь может оставить комментарий."""
    url = reverse('news:detail', args=(news.pk,))
    url_to_comments = url + '#comments'
    response = author_client.post(url, data=form_data)
    # Редирект ведёт на страницу новости, к блоку комментариев.
    assertRedirects(response, url_to_comments)
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.news == news
    assert comment.author == author


@pytest.mark.parametrize('bad_word', BAD_WORDS)
def test_user_cant_use_bad_words(author_client, bad_word, news):
    """3L. В комментариях нельзя использовать запрещённые слова."""
    bad_words_data = {'text': f'Какой-то текст, {bad_word}, ещё текст'}
    url = reverse('news:detail', args=(news.pk,))
    response = author_client.post(url, data=bad_words_data)
    # Достаём форму из контекста и передаём её объект первым аргументом.
    assertFormError(response.context['form'], 'text', errors=WARNING)
    assert Comment.objects.count() == 0


def test_author_can_edit_comment(author_client, form_data, news, comment):
    """4L. Автор может редактировать свой комментарий."""
    url = reverse('news:edit', args=(comment.pk,))
    url_to_comments = reverse('news:detail', args=(news.pk,)) + '#comments'
    response = author_client.post(url, data=form_data)
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == form_data['text']


def test_other_user_cant_edit_comment(not_author_client, form_data, comment):
    """5L. Редактировать чужой комментарий нельзя."""
    url = reverse('news:edit', args=(comment.pk,))
    response = not_author_client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    # Текст комментария в базе остался прежним.
    comment.refresh_from_db()
    assert comment.text == 'Текст комментария'


def test_author_can_delete_comment(author_client, news, comment):
    """6L. Автор может удалить свой комментарий."""
    url = reverse('news:delete', args=(comment.pk,))
    url_to_comments = reverse('news:detail', args=(news.pk,)) + '#comments'
    response = author_client.post(url)
    assertRedirects(response, url_to_comments)
    assert Comment.objects.count() == 0


def test_other_user_cant_delete_comment(not_author_client, comment):
    """7L. Удалить чужой комментарий нельзя."""
    url = reverse('news:delete', args=(comment.pk,))
    response = not_author_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
