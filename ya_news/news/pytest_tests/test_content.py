import pytest

from django.conf import settings
from django.urls import reverse

pytestmark = pytest.mark.django_db


@pytestmark
def test_news_count_and_ordering(client, all_news):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context.get('object_list')
    assert object_list is not None
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytestmark
def test_comment_ordering(all_comments, news_id_for_args, client):
    url = reverse('news:detail', args=news_id_for_args)
    response = client.get(url)
    assert 'news' in response.context
    news = response.context.get('news')
    all_news_comments = news.comment_set.all()
    all_date = [comment.created for comment in all_news_comments]
    sorted_date = sorted(all_date)
    assert all_date == sorted_date


@pytest.mark.parametrize(
    'user, expected_status', (
        (pytest.lazy_fixture('author_client'), True),
        (pytest.lazy_fixture('client'), False)
    )
)
@pytestmark
def test_form_available_for_anonymous_and_auth_user(
    user,
    news_id_for_args,
    expected_status
):
    url = reverse('news:detail', args=news_id_for_args)
    response = user.get(url)
    assert ('form' in response.context) == expected_status
