import markdown2 as markdown
import feedparser
from django.test import TestCase, LiveServerTestCase, Client
from django.utils import timezone
from blogengine.models import Post, Category, Tag
from django.contrib.flatpages.models import FlatPage
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
import factory.django

# Create your tests here.
class SiteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Site
        django_get_or_create = (
            'name',
            'domain'
        )

    name = 'example.com'
    domain = 'example.com'

class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category
        django_get_or_create = (
            'name',
            'description',
            'slug'
        )

    name = 'security'
    description = 'System or data security'
    slug = 'security'

class TagFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Tag
        django_get_or_create = (
            'name',
            'description',
            'slug'
        )

    name = 'security'
    description = 'System or data security'
    slug = 'security'

class AuthorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ('username', 'email', 'password')

    username = 'testuser'
    email = 'user@example.com'
    password = 'password'

class FlatPageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = FlatPage
        django_get_or_create = (
            'url',
            'title',
            'content'
        )

    url = '/about/'
    title = 'About Me'
    content = 'All about me'

class PostFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Post
        django_get_or_create = (
            'title',
            'text',
            'slug',
            'pub_date'
        )

    title = 'First Post'
    text = 'My first blog post'
    slug = 'my-first-post'
    pub_date = timezone.now()
    author = factory.SubFactory(AuthorFactory)
    site = factory.SubFactory(SiteFactory)
    category = factory.SubFactory(CategoryFactory)

class PostTest(TestCase):
    def test_create_category(self):
        # Create a category
        category = CategoryFactory()

        # Check for category in db
        all_categories = Category.objects.all()
        self.assertEquals(len(all_categories), 1)
        only_category = all_categories[0]
        self.assertEquals(only_category, category)

        # Check category data
        self.assertEquals(only_category.name, 'security')
        self.assertEquals(only_category.description, 'System or data security')
        self.assertEquals(only_category.slug, 'security')

    def test_create_tag(self):
        # Create tag
        tag = TagFactory()

        # Check for tag in db
        all_tags = Tag.objects.all()
        self.assertEquals(len(all_tags), 1)
        only_tag = all_tags[0]
        self.assertEquals(only_tag, tag)

        # Check attributes
        self.assertEquals(only_tag.name, 'security')
        self.assertEquals(only_tag.description, 'System or data security')
        self.assertEquals(only_tag.slug, 'security')

    def test_create_post(self):
        # Create tag
        tag = TagFactory()

        # Create the post
        post = PostFactory()

        # Add tag to post
        post.tags.add(tag)
        post.save()

        # Retreive post from database via ORM
        all_posts = Post.objects.all()
        self.assertEquals(len(all_posts), 1)
        only_post = all_posts[0]
        self.assertEquals(only_post, post)

        # Check all attributes individually
        self.assertEquals(only_post.title, 'First Post')
        self.assertEquals(only_post.text, 'My first blog post')
        self.assertEquals(only_post.slug, 'my-first-post')
        self.assertEquals(only_post.pub_date.day, post.pub_date.day)
        self.assertEquals(only_post.pub_date.month, post.pub_date.month)
        self.assertEquals(only_post.pub_date.year, post.pub_date.year)
        self.assertEquals(only_post.pub_date.hour, post.pub_date.hour)
        self.assertEquals(only_post.pub_date.minute, post.pub_date.minute)
        self.assertEquals(only_post.pub_date.second, post.pub_date.second)
        self.assertEquals(only_post.author.username, 'testuser')
        self.assertEquals(only_post.author.email, 'user@example.com')
        self.assertEquals(only_post.site.name, 'example.com')
        self.assertEquals(only_post.site.domain, 'example.com')
        self.assertEquals(only_post.category.name, 'security')
        self.assertEquals(only_post.category.description, 'System or data security')

        # Check tags
        post_tags = only_post.tags.all()
        self.assertEquals(len(post_tags), 1)
        only_post_tag = post_tags[0]
        self.assertEquals(only_post_tag, tag)
        self.assertEquals(only_post_tag.name, 'security')
        self.assertEquals(only_post_tag.description, 'System or data security')

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

    def test_create_tag(self):
        # log in
        self.client.login(username='bobsmith', password="password")

        # Check response code
        response = self.client.post('/admin/blogengine/tag/add/', follow=True)
        self.assertEquals(response.status_code, 200)

        # Create new tag
        response = self.client.post('/admin/blogengine/tag/add/', {
            'name': 'security',
            'description': 'System or data security'
            },
            follow=True
        )
        self.assertEquals(response.status_code, 200)

        # Check tag added
        self.assertTrue('added successfully' in response.content)

        # Check tag is in db
        all_tags = Tag.objects.all()
        self.assertEquals(len(all_tags), 1)

    def test_edit_tag(self):
        # Create tag
        tag = TagFactory()

        # log in
        self.client.login(username='bobsmith', password='password')

        # Edit tag
        response = self.client.post('/admin/blogengine/tag/' + str(tag.pk) + '/', {
            'name': 'cryptography',
            'description': 'Cryptography and encryption'
            },
            follow=True
        )
        self.assertEquals(response.status_code, 200)

        # Check change
        self.assertTrue('changed successfully' in response.content)

        # Check tag changes
        all_tags = Tag.objects.all()
        self.assertEquals(len(all_tags), 1)
        only_tag = all_tags[0]
        self.assertEquals(only_tag.name, 'cryptography')
        self.assertEquals(only_tag.description, 'Cryptography and encryption')

    def test_delete_tag(self):
        # Create tag
        tag = TagFactory()

        # Log in
        self.client.login(username='bobsmith', password='password')

        # Delete tag
        response = self.client.post('/admin/blogengine/tag/'+ str(tag.pk) +'/delete/', {
            'post': 'yes'
            },
            follow=True
        )
        self.assertEquals(response.status_code, 200)

        # Check deleted
        self.assertTrue('deleted successfully' in response.content)

        # Check tag deleted
        all_tags = Tag.objects.all()
        self.assertEquals(len(all_tags), 0)

    def test_create_category(self):
        # Log in
        self.client.login(username='bobsmith', password='password')

        # Check response code
        response = self.client.get('/admin/blogengine/category/add/', follow=True)
        self.assertEquals(response.status_code, 200)

        # Create new category
        response = self.client.post('/admin/blogengine/category/add/', {
            'name': 'security',
            'description': 'System or data security'
            },
            follow=True
        )
        self.assertEquals(response.status_code, 200)

        # Check category was added
        self.assertTrue('added successfully' in response.content)

        # Check category in db
        all_categories = Category.objects.all()
        self.assertEquals(len(all_categories), 1)

    def test_edit_category(self):
        # Create category
        category = CategoryFactory()

        # Log in
        self.client.login(username='bobsmith', password='password')

        # Edit category
        response = self.client.post('/admin/blogengine/category/' + str(category.pk) + '/', {
            'name': 'cryptography',
            'description': 'Cryptography and encryption'
            },
            follow=True
        )
        self.assertEquals(response.status_code, 200)

        # Check change
        self.assertTrue('changed successfully' in response.content)

        # Check category data
        all_categories = Category.objects.all()
        self.assertEquals(len(all_categories), 1)
        only_category = all_categories[0]
        self.assertEquals(only_category.name, 'cryptography')
        self.assertEquals(only_category.description, 'Cryptography and encryption')

    def test_delete_category(self):
        # Create category
        category = CategoryFactory()

        # Log in
        self.client.login(username='bobsmith', password="password")

        # Delete the category
        response = self.client.post('/admin/blogengine/category/' + str(category.pk) + '/delete/', {
            'post': 'yes'
        }, follow=True)
        self.assertEquals(response.status_code, 200)

        # Check deleted successfully
        self.assertTrue('deleted successfully' in response.content)

        # Check category deleted
        all_categories = Category.objects.all()
        self.assertEquals(len(all_categories), 0)

    def test_create_post(self):
        # Create category
        category = CategoryFactory()

        # Create tag
        tag = TagFactory()

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
            'pub_date_1': '12:00:05',
            'site': '1',
            'category': str(category.pk),
            'tags': str(tag.pk)
            },
            follow=True
        )
        self.assertEquals(response.status_code, 200)

        # Check post added successfully
        self.assertTrue('added successfully' in response.content)

        # Check new post now in database
        all_posts = Post.objects.all()
        self.assertEquals(len(all_posts), 1)

    def test_create_post_without_tag(self):
        # Create category
        category = CategoryFactory()

        # Log in
        self.client.login(username='bobsmith', password='password')

        # Check response code
        response = self.client.get('/admin/blogengine/post/add/')
        self.assertEquals(response.status_code, 200)

        # Create new post
        response = self.client.post('/admin/blogengine/post/add/', {
            'title': 'First Post',
            'text': 'My first blog post',
            'pub_date_0': '2015-01-01',
            'pub_date_1': '12:00:05',
            'slug': 'my-first-post',
            'site': '1',
            'category': str(category.pk)
            },
            follow=True
        )
        self.assertEquals(response.status_code, 200)

        # Check post
        self.assertTrue('added successfully' in response.content)

        # Check post in db
        all_posts = Post.objects.all()
        self.assertEquals(len(all_posts), 1)

    def test_edit_post(self):
        # Create tag
        tag = TagFactory()

        # Create the post
        post = PostFactory()

        # Add tags
        post.tags.add(tag)
        post.save()

        # Log in
        self.client.login(username='bobsmith', password="password")

        # Edit the post
        response = self.client.post('/admin/blogengine/post/' + str(post.pk) + '/', {
            'title': 'Second Post',
            'text': 'This is the second post',
            'slug': 'my-second-post',
            'pub_date_0': '2015-01-01',
            'pub_date_1': '12:00:05',
            'site': '1',
            'category': str(post.category.pk),
            'tags': str(tag.pk)
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
        # Create tag
        tag = TagFactory()

        # Create the post
        post = PostFactory()

        # Add tags
        post.tags.add(tag)
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
        # Create category
        category = CategoryFactory()

        # Create tag
        tag = TagFactory()

        # Create author
        author = AuthorFactory()

        # Create site
        site = SiteFactory()

        # Create the post
        post = Post()
        post.title = 'First Post'
        post.text = 'This is [my first blog post](http://127.0.0.1:8080/)'
        post.slug = 'my-first-post'
        post.pub_date = timezone.now()
        post.author = author
        post.site = site
        post.category = category
        post.save()
        post.tags.add(tag)

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

        # Check the post category is in the response
        self.assertTrue(post.category.name in response.content)

        # Check post tag in response
        post_tag = all_posts[0].tags.all()[0]
        self.assertTrue(post_tag.name in response.content)

        # Check for the post date in response
        self.assertTrue(str(post.pub_date.year) in response.content)
        self.assertTrue(post.pub_date.strftime('%b') in response.content)
        self.assertTrue(str(post.pub_date.day) in response.content)

        # Check markdown link is correct html mark up
        self.assertTrue('<a href="http://127.0.0.1:8080/">my first blog post</a>' in response.content)

    def test_post_page(self):
        # Create category
        category = CategoryFactory()

        # Create tag
        tag = TagFactory()

        # Create author
        author = AuthorFactory()

        # Create Site
        site = SiteFactory()

        # Create the post
        post = Post()
        post.title = 'First Post'
        post.text = 'This is [my first post](http://127.0.0.1:8080/)'
        post.slug = 'my-first-post'
        post.pub_date = timezone.now()
        post.author = author
        post.site = site
        post.category = category
        post.save()
        post.tags.add(tag)
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

        # Check the post category is in the response
        self.assertTrue(post.category.name in response.content)

        # Check post tag in response
        post_tag = all_posts[0].tags.all()[0]
        self.assertTrue(post_tag.name in response.content)

        # Check post text
        self.assertTrue(markdown.markdown(post.text) in response.content)

        # Check post date
        self.assertTrue(str(post.pub_date.year) in response.content)
        self.assertTrue(post.pub_date.strftime('%b') in response.content)
        self.assertTrue(str(post.pub_date.day) in response.content)

        # Check markdown link is proper html mark up
        self.assertTrue('<a href="http://127.0.0.1:8080/">my first post</a>' in response.content)

    def test_category_page(self):
        # Create category
        category = CategoryFactory()

        # Create author
        author = AuthorFactory()

        # Create site
        site = SiteFactory()

        # Create the post
        post = Post()
        post.title = 'My first post'
        post.text = 'This is [my first blog post](http://127.0.0.1:8000/)'
        post.slug = 'my-first-post'
        post.pub_date = timezone.now()
        post.author = author
        post.site = site
        post.category = category
        post.save()

        # Check new post saved
        all_posts = Post.objects.all()
        self.assertEquals(len(all_posts), 1)
        only_post = all_posts[0]
        self.assertEquals(only_post, post)

        # Get the category URL
        category_url = post.category.get_absolute_url()

        # Fetch the category
        response = self.client.get(category_url, follow=True)
        self.assertEquals(response.status_code, 200)

        # Check the category name is in the response
        self.assertTrue(post.category.name in response.content)

        # Check the post text is in the response
        self.assertTrue(markdown.markdown(post.text) in response.content)

        # Check the post date is in the response
        self.assertTrue(str(post.pub_date.year) in response.content)
        self.assertTrue(post.pub_date.strftime('%b') in response.content)
        self.assertTrue(str(post.pub_date.day) in response.content)

        # Check the link is marked up properly
        self.assertTrue('<a href="http://127.0.0.1:8000/">my first blog post</a>' in response.content)

    def test_tag_page(self):
        # Create tag
        tag = TagFactory()

        # Create the author
        author = AuthorFactory()

        # Create the site
        site = SiteFactory()

        # Create the post
        post = Post()
        post.title = 'My first post'
        post.text = 'This is [my first blog post](http://127.0.0.1:8000/)'
        post.slug = 'my-first-post'
        post.pub_date = timezone.now()
        post.author = author
        post.site = site
        post.save()
        post.tags.add(tag)

        # Check new post saved
        all_posts = Post.objects.all()
        self.assertEquals(len(all_posts), 1)
        only_post = all_posts[0]
        self.assertEquals(only_post, post)

        # Get the tag URL
        tag_url = post.tags.all()[0].get_absolute_url()

        # Fetch the tag
        response = self.client.get(tag_url)
        self.assertEquals(response.status_code, 200)

        # Check the tag name is in the response
        self.assertTrue(post.tags.all()[0].name in response.content)

        # Check the post text is in the response
        self.assertTrue(markdown.markdown(post.text) in response.content)

        # Check the post date is in the response
        self.assertTrue(str(post.pub_date.year) in response.content)
        self.assertTrue(post.pub_date.strftime('%b') in response.content)
        self.assertTrue(str(post.pub_date.day) in response.content)

        # Check the link is marked up properly
        self.assertTrue('<a href="http://127.0.0.1:8000/">my first blog post</a>' in response.content)

    def test_nonexistent_category_page(self):
        category_url = '/category/blah/'
        response = self.client.get(category_url)
        self.assertEquals(response.status_code, 200)
        self.assertTrue('No posts found' in response.content)

    def test_nonexistent_tag_page(self):
        tag_url = '/tag/blah/'
        response = self.client.get(tag_url)
        self.assertEquals(response.status_code, 200)
        self.assertTrue('No posts found' in response.content)

class FeedTest(BaseAcceptanceTest):
    def test_all_post_feed(self):
        # Create category
        category = CategoryFactory()

        # Create tag
        tag = TagFactory()

        # Create author
        author = AuthorFactory()

        # Create site
        site = SiteFactory()

        # Create post
        post = Post()
        post.title = 'First Post'
        post.text = 'My *First* blog post'
        post.slug = 'my-first-post'
        post.pub_date = timezone.now()
        post.author = author
        post.site = site
        post.category = category

        # Save post
        post.save()

        # Add tag to post
        post.tags.add(tag)
        post.save()

        # Check for post
        all_posts = Post.objects.all()
        self.assertEquals(len(all_posts), 1)
        only_post = all_posts[0]
        self.assertEquals(only_post, post)

        # Get feed
        response = self.client.get('/feeds/posts/', follow=True)
        self.assertEquals(response.status_code, 200)

        # Parse feed
        feed = feedparser.parse(response.content)

        # Check length
        self.assertEquals(len(feed.entries), 1)

        # Check post is correct
        feed_post = feed.entries[0]
        self.assertEquals(feed_post.title, post.title)
        self.assertTrue('My <em>First</em> blog post' in feed_post.description)

class FlatPageViewTest(BaseAcceptanceTest):
    def test_create_flat_page(self):
        # Create flat page
        page = FlatPageFactory()

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
