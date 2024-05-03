from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from http import HTTPStatus
from pytest_django.asserts import assertRedirects
from pytils.translit import slugify

from notes.models import Note
from notes.forms import WARNING

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
        cls.form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст заметки',
            'slug': 'new-slug'
        }

    def test_author_user_can_create_note(self):
        self.client.force_login(self.author)
        notes_quantity = Note.objects.count()
        url = reverse('notes:add')
        response = self.client.post(url, data=self.form_data)
        assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), notes_quantity + 1)
        new_note = Note.objects.last()
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_non_auth_user_cant_create_note(self):
        notes_quantity = Note.objects.count()
        url = reverse('notes:add')
        response = self.client.post(url, data=self.form_data)
        login_url = reverse('users:login')
        expected_url = f'{login_url}?next={url}'
        self.assertRedirects(response, expected_url)
        self.assertEqual(Note.objects.count(), notes_quantity)

    def test_non_unique_slug(self):
        self.client.force_login(self.author)
        url = reverse('notes:add')
        self.form_data['slug'] = self.note.slug
        response = self.client.post(url, data=self.form_data)
        self.assertFormError(response, 'form', 'slug',
                             errors=(self.note.slug + WARNING))

    def test_empty_slug(self):
        notes_quantity = Note.objects.count()
        self.client.force_login(self.author)
        url = reverse('notes:add')
        self.form_data.pop('slug')
        response = self.client.post(url, self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), notes_quantity + 1)
        new_note = Note.objects.last()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)

    def test_author_can_edit_note(self):
        notes_quantity = Note.objects.count()
        self.client.force_login(self.author)
        url = reverse('notes:edit', args=(self.note.slug,))
        response = self.client.post(url, self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), notes_quantity)
        new_note = Note.objects.last()
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])

    def test_non_author_cant_edit_note(self):
        self.client.force_login(self.another_author)
        url = reverse('notes:edit', args=(self.note.slug,))
        response = self.client.post(url, self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.last()
        self.assertEqual(self.note.title, note_from_db.title)
        self.assertEqual(self.note.text, note_from_db.text)
        self.assertEqual(self.note.slug, note_from_db.slug)

    def test_author_can_delete_note(self):
        notes_quantity = Note.objects.count()
        self.client.force_login(self.author)
        url = reverse('notes:delete', args=(self.note.slug,))
        response = self.client.post(url)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertNotIn(self.note.slug, Note.objects.all())
        self.assertEqual(Note.objects.count(), notes_quantity - 1)

    def test_non_author_can_delete_note(self):
        notes_quantity = Note.objects.count()
        self.client.force_login(self.another_author)
        url = reverse('notes:delete', args=(self.note.slug,))
        response = self.client.post(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), notes_quantity)
