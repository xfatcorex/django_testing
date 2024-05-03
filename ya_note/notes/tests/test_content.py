from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestContent(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Пётр')
        cls.another_author = User.objects.create(username='Павел')
        cls.note = Note.objects.create(
            title='Заголовок',
            author=cls.author,
            slug='slug-text',
            text='Текст заметки')

    def test_author_note_in_list_and_another_author_note_not_in(self):
        users = (
            (self.author, True),
            (self.another_author, False),
        )
        for user, note_in_list in users:
            self.client.force_login(user)
            with self.subTest():
                url = reverse('notes:list')
                response = self.client.get(url)
                object_list = response.context.get('object_list')
                self.assertIsNotNone(object_list)
                self.assertEqual(self.note in object_list, note_in_list)

    def test_form_on_edit_and_add_note_pages(self):
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
        )
        self.client.force_login(self.author)
        for name, args in urls:
            with self.subTest():
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual('form' in response.context, True)
