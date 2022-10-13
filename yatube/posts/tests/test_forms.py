from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from ..models import Group, Post
User = get_user_model()


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title=('Заголовок для тестовой группы'),
            slug='slug',
            description='Тестовое описание'
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='auth')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )

    def test_create_post(self):
        count_posts = Post.objects.count()
        form_data = {
            'text': 'Данные из формы',
            'group': self.group.pk
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertTrue(Post.objects.filter(
                        text='Данные из формы',
                        group=self.group.pk,
                        author=self.user
                        ).exists())
        self.assertEqual(Post.objects.count(), count_posts + 1)
        self.assertRedirects(response, reverse('posts:profile',
                             kwargs={'username': 'auth'}))
        
        self.assertEqual(self.user.username, 'auth')
        self.assertEqual(self.group.title, 'Заголовок для тестовой группы')

    def test_create_post_not_authorized(self):
        form_data = {
            'text': 'Данные из формы',
            'group': self.group.pk
        }
        self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertFalse(Post.objects.filter(
                         text='Данные из формы'
                         ).exists())

    def test_edit_post(self):
        form_data = {
            'text': 'Данные из формы',
            'group': self.group.pk
        }
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        post_2 = Post.objects.get(id=self.group.pk)
        self.client.get(f'/posts/{post_2.id}/edit/')
        form_data = {
            'text': 'Измененный текст',
            'group': self.group.pk
        }
        response_edit = self.authorized_client.post(
            reverse('posts:post_edit',
                    kwargs={
                        'post_id': post_2.id
                    }),
            data=form_data,
            follow=True,
        )
        post_2 = Post.objects.get(id=self.group.pk)
        self.assertEqual(response_edit.status_code, 200)
        self.assertEqual(post_2.text, 'Измененный текст')
