import pytest

from datetime import timedelta
from django.conf import settings
from django.test.client import Client
from django.utils import timezone

from news.forms import BAD_WORDS
from news.models import Comment, News

COMMENT_QUANTITY = 5


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def non_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def non_author_client(non_author):
    client = Client()
    client.force_login(non_author)
    return client


@pytest.fixture
def news():
    return (News.objects.create(
        title='Заголовок',
        text='Текст')
    )


@pytest.fixture
def news_id_for_args(news):
    return (news.id,)


@pytest.fixture
def comment(author, news):
    return (Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария')
    )


@pytest.fixture
def comment_id_for_args(comment):
    return (comment.id,)


@pytest.fixture
def all_news():
    now = timezone.now()
    return (News.objects.bulk_create(
        News(title=f'Новость {index}',
             text='Текст новости',
             date=now - timedelta(days=index))
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1))
    )


@pytest.fixture
def all_comments(news, author):
    now = timezone.now()
    return (Comment.objects.bulk_create(
        Comment(
            news=news,
            author=author,
            text=f'Текст комментария {index}',
            created=now + timedelta(days=index)
        )
        for index in range(COMMENT_QUANTITY))
    )


@pytest.fixture
def form_data():
    return {'text': 'Еще текст комментария'}


@pytest.fixture
def bad_word_form_data():
    return {'text': f'Текст комментария {BAD_WORDS[0]}'}
