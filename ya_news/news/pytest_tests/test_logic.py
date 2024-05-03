import pytest

from django.urls import reverse
from http import HTTPStatus
from pytest_django.asserts import assertFormError, assertRedirects

from news.models import Comment
from news.forms import WARNING

pytestmark = pytest.mark.django_db


@pytestmark
def test_form_for_anonymous_user(form_data, client, news_id_for_args):
    comments_quantity = Comment.objects.count()
    url = reverse('news:detail', args=news_id_for_args)
    client.post(url, data=form_data)
    assert comments_quantity == Comment.objects.count()


def test_form_for_auth_user(
        form_data,
        author_client,
        author,
        news,
        news_id_for_args
):
    comments_quantity = Comment.objects.count()
    url = reverse('news:detail', args=news_id_for_args)
    response = author_client.post(url, data=form_data)
    assertRedirects(response, f'{url}#comments')
    assert comments_quantity < Comment.objects.count()
    comment = Comment.objects.last()
    assert comment.text == form_data['text']
    assert comment.news == news
    assert comment.author == author


def test_author_cant_use_bad_words(
        author_client,
        bad_word_form_data,
        news_id_for_args
):
    comments_quantity = Comment.objects.count()
    url = reverse('news:detail', args=news_id_for_args)
    response = author_client.post(url, data=bad_word_form_data)
    assertFormError(response, 'form', 'text', errors=WARNING)
    assert comments_quantity == Comment.objects.count()


@pytestmark
def test_auth_user_can_delete_comment(
    news_id_for_args,
    author_client,
    comment_id_for_args,
):
    comments_quantity = Comment.objects.count()
    url = reverse('news:delete', args=comment_id_for_args)
    comments_url = reverse('news:detail', args=news_id_for_args)
    response = author_client.delete(url)
    assertRedirects(response, comments_url + '#comments')
    assert comments_quantity > Comment.objects.count()
    assert comment_id_for_args not in Comment.objects.all()


def test_non_author_cant_delete_comment(
    non_author_client,
    comment_id_for_args
):
    comments_quantity = Comment.objects.count()
    url = reverse('news:delete', args=comment_id_for_args)
    response = non_author_client.delete(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert comments_quantity == Comment.objects.count()


def test_author_can_edit_comment(
        author_client,
        news_id_for_args,
        form_data,
        comment_id_for_args,
        author,
        news
):
    comments_quantity = Comment.objects.count()
    url = reverse('news:edit', args=comment_id_for_args)
    response = author_client.post(url, data=form_data)
    comments_url = reverse('news:detail', args=news_id_for_args)
    assertRedirects(response, comments_url + '#comments')
    new_comment = Comment.objects.last()
    assert comments_quantity == Comment.objects.count()
    assert new_comment.text == form_data['text']
    assert new_comment.author == author
    assert new_comment.news == news


def test_non_author_cant_edit_comment(
        non_author_client,
        form_data,
        comment
):
    url = reverse('news:edit', args=(comment.id,))
    response = non_author_client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    comment_from_db = Comment.objects.last()
    assert comment.text == comment_from_db.text
