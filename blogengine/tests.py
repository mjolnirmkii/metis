import markdown2 as markdown
from django.test import TestCase, LiveServerTestCase, Client
from django.utils import timezone
from blogengine.models import Post
from django.contrib.flatpages.models import FlatPage
from django.contrib.sites.models import Site
from django.contrib.auth.models import User

# Create your tests here.
class PostTest(TestCase):

    def test_create_post(self):
        # Create an author
        author = User.objects.create_user('testuser', 'user@example.com', 'password')
        author.save()

        # Create the post
        post = Post()

        # Set the attributes
        post.title = 'Testing Blog Post'
        post.text = 'This is a test blog post generated in the test class'
        post.slug = 'my-first-post'
        post.pub_date = timezone.now()
        post.author = author

        # Save post
        post.save()

        # Retreive post from database via ORM
        all_posts = Post.objects.all()
        self.assertEquals(len(all_posts), 1)
        only_post = all_posts[0]
        self.assertEquals(only_post, post)

        # Check all attributes individually
        self.assertEquals(only_post.title, 'Testing Blog Post')
        self.assertEquals(only_post.text, 'This is a test blog post generated in the test class')
        self.assertEquals(only_post.slug, 'my-first-post')
        self.assertEquals(only_post.pub_date.day, post.pub_date.day)
        self.assertEquals(only_post.pub_date.month, post.pub_date.month)
        self.assertEquals(only_post.pub_date.year, post.pub_date.year)
        self.assertEquals(only_post.pub_date.hour, post.pub_date.hour)
        self.assertEquals(only_post.pub_date.minute, post.pub_date.minute)
        self.assertEquals(only_post.pub_date.second, post.pub_date.second)
        self.assertEquals(only_post.author.username, 'testuser')
        self.assertEquals(only_post.author.email, 'user@example.com')

class BaseAcceptanceTest(LiveServerTestCase):
    def set_up(self):
        self.client = Client()

class AdminTest(BaseAcceptanceTest):
    fixtures = ['users.json']

    def test_login(self):
        # Get login page
        response = self.client.get('/admin/', follow=True)

        # Check response code
        self.assertEquals(response.status_code, 200)

        # Check Log in is in response
        self.assertTrue('Log in' in response.content)

        # Log the user in
        self.client.login(username='bobsmith', password="password")

        # Check response code
        response = self.client.get('/admin/', follow=True)
        self.assertEquals(response.status_code, 200)

        # Check 'Log out' in response
        self.assertTrue('Log out' in response.content)

    def test_logout(self):
        # Log in
        self.client.login(username='bobsmith', password="password")

        # Check response code
        response = self.client.get('/admin/', follow=True)
        self.assertEquals(response.status_code, 200)

        # Check 'Log out' in response
        self.assertTrue('Log out' in response.content)

        # Log out
        self.client.logout()

        # Check response code
        response = self.client.get('/admin/', follow=True)
        self.assertEquals(response.status_code, 200)

        # Check 'Log in' in response
        self.assertTrue('Log in' in response.content)

    def test_create_post(self):
        # Log in
        self.client.login(username='bobsmith', password="password")

        # Check response code
        response = self.client.get('/admin/blogengine/post/add/', follow=True)
        self.assertEquals(response.status_code, 200)

        # Create the new post
        response = self.client.post('/admin/blogengine/post/add/', {
            'title': 'First Post',
            'text': 'This is the first post',
            'slug': 'my-first-post',
            'pub_date_0': '2015-01-01',
            'pub_date_1': '12:00:05'
        },
        follow=True
        )
        self.assertEquals(response.status_code, 200)

        # Check post added successfully
        self.assertTrue('added successfully' in response.content)

        # Check new post now in database
        all_posts = Post.objects.all()
        self.assertEquals(len(all_posts), 1)

    def test_edit_post(self):
        # Create author
        author = User.objects.create_user('testuser', 'user@example.com', 'password')
        author.save()

        # Create the post
        post = Post()
        post.title = 'First Post'
        post.text = 'This is the first post'
        post.slug = 'my-first-post'
        post.pub_date = timezone.now()
        post.author = author
        post.save()

        # Log in
        self.client.login(username='bobsmith', password="password")

        # Edit the post
        response = self.client.post('/admin/blogengine/post/' + str(post.pk) + '/', {
            'title': 'Second Post',
            'text': 'This is the second post',
            'slug': 'my-second-post',
            'pub_date_0': '2015-01-01',
            'pub_date_1': '12:00:05'
        },
        follow=True
        )
        self.assertEquals(response.status_code, 200)

        # Check that it changed
        self.assertTrue('changed successfully' in response.content)

        # Check edited post content in database
        all_posts = Post.objects.all()
        self.assertEquals(len(all_posts), 1)
        only_post = all_posts[0]
        self.assertEquals(only_post.title, 'Second Post')
        self.assertEquals(only_post.text, 'This is the second post')

    def test_delete_post(self):
        # Create author
        author = User.objects.create_user('testuser', 'user@example.com', 'password')
        author.save()

        # Create the post
        post = Post()
        post.title = 'My first post'
        post.text = 'This is my first blog post'
        post.pub_date = timezone.now()
        post.author = author
        post.save()

        # Check new post saved
        all_posts = Post.objects.all()
        self.assertEquals(len(all_posts), 1)

        # Log in
        self.client.login(username='bobsmith', password="password")

        # Delete the post
        response = self.client.post('/admin/blogengine/post/' + str(post.pk) + '/delete/', {
            'post': 'yes'
        }, follow=True)
        self.assertEquals(response.status_code, 200)

        # Check deleted successfully
        self.assertTrue('deleted successfully' in response.content)

        # Check post amended
        all_posts = Post.objects.all()
        self.assertEquals(len(all_posts), 0)

class PostViewTest(BaseAcceptanceTest):
    def test_index(self):
        # Create author
        author = User.objects.create_user('tsetuser', 'user@example.com', 'password')
        author.save()

        # Create the post
        post = Post()
        post.title = 'First Post'
        post.text = 'This is [my first blog post](http://127.0.0.1:8080/)'
        post.slug = 'my-first-post'
        post.pub_date = timezone.now()
        post.author = author
        post.save()

        # Check the post saved
        all_posts = Post.objects.all()
        self.assertEquals(len(all_posts), 1)

        # Get index page of site
        response = self.client.get('/', follow=True)
        self.assertEquals(response.status_code, 200)

        # Check for post title in response
        self.assertTrue(post.title in response.content)

        # Check for post text in response
        self.assertTrue(markdown.markdown(post.text) in response.content)

        # Check for the post date in response
        self.assertTrue(str(post.pub_date.year) in response.content)
        self.assertTrue(post.pub_date.strftime('%b') in response.content)
        self.assertTrue(str(post.pub_date.day) in response.content)

        # Check markdown link is correct html mark up
        self.assertTrue('<a href="http://127.0.0.1:8080/">my first blog post</a>' in response.content)

    def test_post_page(self):
        # Create author
        author = User.objects.create_user('testuser', 'user@example.com', 'password')
        author.save()

        # Create the post
        post = Post()
        post.title = 'First Post'
        post.text = 'This is [my first post](http://127.0.0.1:8080/)'
        post.slug = 'my-first-post'
        post.pub_date = timezone.now()
        post.author = author
        post.save()

        # Check post saved
        all_posts = Post.objects.all()
        self.assertEquals(len(all_posts), 1)
        only_post = all_posts[0]
        self.assertEquals(only_post, post)

        # Get post URL
        post_url = only_post.get_absolute_url()

        # Fetch post
        response = self.client.get(post_url)
        self.assertEquals(response.status_code, 200)

        # Check the post title
        self.assertTrue(post.title in response.content)

        # Check post text
        self.assertTrue(markdown.markdown(post.text) in response.content)

        # Check post date
        self.assertTrue(str(post.pub_date.year) in response.content)
        self.assertTrue(post.pub_date.strftime('%b') in response.content)
        self.assertTrue(str(post.pub_date.day) in response.content)

        # Check markdown link is proper html mark up
        self.assertTrue('<a href="http://127.0.0.1:8080/">my first post</a>' in response.content)

class FlatPageViewTest(BaseAcceptanceTest):
    def test_create_flat_page(self):
        # Create flat page
        page = FlatPage()
        page.url = '/about/'
        page.title = 'About Me'
        page.content = 'All about me'
        page.save()

        # Add site
        page.sites.add(Site.objects.all()[0])
        page.save()

        # Check new page saved
        all_pages = FlatPage.objects.all()
        self.assertEquals(len(all_pages), 1)
        only_page = all_pages[0]
        self.assertEquals(only_page, page)

        # Check page data
        self.assertEquals(only_page.url, '/about/')
        self.assertEquals(only_page.title, 'About Me')
        self.assertEquals(only_page.content, 'All about me')

        # Get URL
        page_url = only_page.get_absolute_url()

        # Get page
        response = self.client.get(page_url, follow=True)
        self.assertEquals(response.status_code, 200)

        # Check title and content in response
        self.assertTrue('About Me' in response.content)
        self.assertTrue('All about me' in response.content)
