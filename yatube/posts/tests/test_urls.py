from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from ..models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(
            username='auth'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая запись',
        )
        cls.group = Group.objects.create(
            title=('Тестовый заголовок'),
            slug='slug',
            description='Тестовое описание'
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.get(username='auth')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_public_pages(self):
        postURLTests = PostURLTests()
        postid = postURLTests.post.pk
        url_names = [
            '/',
            '/group/slug/',
            '/profile/auth/',
            '/posts/' + str(postid) + '/',

        ]
        for adress in url_names:
            with self.subTest():
                response = self.guest_client.get(adress)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_for_authorized(self):
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_for_authorized(self):
        response = self.authorized_client.get('/posts/1/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template(self):
        postURLTests = PostURLTests()
        postid = postURLTests.post.pk
        templates_url_names = {
            'posts/index.html': '/',
            'posts/group_list.html': '/group/slug/',
            'posts/create_post.html': '/create/',
            'posts/profile.html': '/profile/auth/',
            'posts/post_detail.html': '/posts/' + str(postid) + '/',

        }
        for template, url in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_page_404(self):
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
