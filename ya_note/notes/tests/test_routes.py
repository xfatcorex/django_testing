from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from http import HTTPStatus

from notes.models import Note


User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Пётр')
        cls.another_author = User.objects.create(username='Павел')
        cls.note = Note.objects.create(title='Заголовок',
                                       author=cls.author,
                                       slug='slug-text',
                                       text='Текст заметки')

    def test_pages_for_auth_user(self):
        urls = (
            'notes:add',
            'notes:list',
            'notes:success',
        )
        self.client.force_login(self.author)
        for name in urls:
            with self.subTest():
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_note_edit_delete_for_author_only(self):
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.another_author, HTTPStatus.NOT_FOUND),
        )
        urls = (
            'notes:edit',
            'notes:detail',
            'notes:delete',
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in urls:
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_home_and_auth_pages_for_anonymous_user(self):
        urls = (
            'notes:home',
            'users:login',
            'users:signup',
            'users:logout',
        )
        for name in urls:
            with self.subTest():
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_redirect(self):
        login_url = reverse('users:login')
        urls = (
            ('notes:add', None),
            ('notes:list', None),
            ('notes:success', None),
            ('notes:edit', (self.note.slug,)),
            ('notes:detail', (self.note.slug,)),
            ('notes:delete', (self.note.slug,))
        )
        for name, args in urls:
            with self.subTest():
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
