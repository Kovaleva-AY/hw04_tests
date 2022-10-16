from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from ..models import Group, Post
from ..forms import PostForm
from django.urls import reverse
User = get_user_model()


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post = Post.objects.create(
            author=User.objects.create_user(username='test_name1'),
            text='Тестовая запись для создания 1 поста',
            group=Group.objects.create(
                title='Заголовок для 1 тестовой группы',
                slug='test_slug1'))
        cls.group = Group.objects.create(
            title=('Заголовок для тестовой группы'),
            slug='slug',
            description='Тестовое описание'
        )
    
        cls.form = PostForm()

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='auth')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.form_data = {
            'text': 'Данные из формы',
            'group': self.group.pk
        }
       

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


    def test_create_post_not_authorized(self):
        form_data = {
            'text': 'Текст',
            'group': 'Группа'
        }
        self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertFalse(Post.objects.filter(
                        text='Текст'
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
        self.client.get('/posts/1/edit/')
        form_data = {
            'text': 'Измененный текст',
            'group': self.group.pk
        }
        response_edit = self.authorized_client.post(
            reverse('posts:post_edit',
                    kwargs={
                        'post_id': self.group.pk
                    }),
            data=form_data,
            follow=True,
        )
        post_2 = Post.objects.get(id=self.group.id)
        self.assertEqual(response_edit.status_code, 200)
        self.assertEqual(post_2.text, 'Измененный текст')

    def test_reddirect_guest_client(self):
        form_data = {'text': 'Текст записанный в форму'}
        response = self.guest_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response,
                             f'/auth/login/?next=/posts/{self.post.id}/edit/')

    def test_no_edit_post(self):
        posts_count = Post.objects.count()
        form_data = {'text': 'Текст записанный в форму',
                     'group': self.group.id}
        response = self.guest_client.post(reverse('posts:post_create'),
                                          data=form_data,
                                          follow=True)
        
        self.assertEqual(response.status_code, HTTPStatus.OK)
        error_name2 = 'Поcт добавлен в базу данных по ошибке'
        self.assertNotEqual(Post.objects.count(),
                            posts_count + 1,
                            error_name2)
