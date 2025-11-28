"""Tests User Views (Homepage, Feed, Follows/Unfollows, Login/Logout, etc)."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from users.models import UserFollows

User = get_user_model()


FEED_NAME = "reviews:feed"


class RegistrationViewTests(TestCase):
    """View-level tests for the registration flow (US01)."""

    def test_register_get_renders_form(self):
        """GET /register/ renders the registration page with required fields."""
        url = reverse("users:register")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Inscrivez-vous")
        # field presence (basic smoke)
        self.assertContains(resp, "password1")
        self.assertContains(resp, "password2")

    def test_register_post_success_redirects_with_qs(self):
        """POST valid data to /register/ creates a user and redirects to home with query params."""
        url = reverse("users:register")
        data = {
            "username": "eve",
            "password1": "StrongPassw0rd!",
            "password2": "StrongPassw0rd!",
        }
        resp = self.client.post(url, data, follow=False)
        self.assertEqual(resp.status_code, 302)
        location = resp["Location"]
        self.assertTrue(location.startswith(reverse("home")))
        self.assertIn("registered=1", location)
        self.assertIn("u=eve", location)
        self.assertTrue(User.objects.filter(username="eve").exists())

    def test_register_get_renders_template(self):
        """GET /register/ renders the registration page with required fields."""
        resp = self.client.get(reverse("users:register"))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "registration/register.html")
        self.assertIn("form", resp.context)

    def test_register_post_valid_redirects_with_querystring(self):
        """POST valid data to /register/ creates a user and redirects to home."""
        resp = self.client.post(
            reverse("users:register"),
            data={
                "username": "charlie",
                "password1": "StrongPassw0rd!",
                "password2": "StrongPassw0rd!",
            },
            follow=False,
        )
        self.assertEqual(resp.status_code, 302)
        # /?registered=1&u=charlie
        self.assertIn("?registered=1&u=charlie", resp.headers["Location"])

        # user actually created
        self.assertTrue(User.objects.filter(username="charlie").exists())

    def test_register_post_invalid_stays_on_page_and_shows_form(self):
        """Tests invalid form behavior for registration."""
        # password mismatch → invalid branch
        resp = self.client.post(
            reverse("users:register"),
            data={
                "username": "dana",
                "password1": "StrongPassw0rd!",
                "password2": "NotTheSame123!",
            },
            follow=True,
        )
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "registration/register.html")
        self.assertIn("form", resp.context)
        self.assertFalse(User.objects.filter(username="dana").exists())

    def test_register_post_duplicate_username_is_invalid(self):
        """Tests registration form invalidation to avoid duplicate usernames."""
        User.objects.create_user(username="alex", password="x")
        resp = self.client.post(
            reverse("users:register"),
            data={
                "username": "alex",  # already taken
                "password1": "StrongPassw0rd!",
                "password2": "StrongPassw0rd!",
            },
            follow=True,
        )
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "registration/register.html")
        self.assertIn("form", resp.context)


class HomeViewTests(TestCase):
    """Homepage behavior in US02: login form processes authentication."""

    def test_home_processes_login_and_redirects(self):
        """POST valid credentials logs user in and redirects to feed."""
        User.objects.create_user(username="gina", password="P@ssw0rd!!")
        url = reverse("home")
        resp = self.client.post(url, {"username": "gina", "password": "P@ssw0rd!!"})
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse(FEED_NAME), resp.url)


class HomeViewLoginTests(TestCase):
    """View-level tests for login functionality (US02)."""

    def setUp(self):
        """Temporarily sets up a User Object to test login."""
        self.user = User.objects.create_user(
            username="ivy",
            password="StrongPassw0rd!"
        )
        self.url = reverse("home")

    def test_get_home_renders_login_form(self):
        """GET / renders homepage with login form fields."""
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Connectez-vous")
        self.assertContains(resp, "id=\"id_username\"")
        self.assertContains(resp, "id=\"id_password\"")

    def test_inputs_have_aria_labels(self):
        """Login form inputs should include ARIA labels for accessibility."""
        resp = self.client.get(self.url)
        html = resp.content.decode()

        # accept both escaped and unescaped forms
        self.assertTrue(
            'aria-label="Nom d&#x27;utilisateur"' in html or 'aria-label="Nom d\'utilisateur"' in html,
            "Missing aria-label for username input"
        )
        self.assertIn('aria-label="Mot de passe"', html)

    def test_post_valid_login_redirects_to_feed(self):
        """Valid credentials authenticate user and redirect to /feed."""
        data = {"username": "ivy", "password": "StrongPassw0rd!", "remember_me": True}
        resp = self.client.post(self.url, data)
        # Redirect after login
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse(FEED_NAME), resp.url)

    def test_post_invalid_login_stays_on_page_with_error(self):
        """Invalid credentials re-render homepage and show error message."""
        data = {"username": "ivy", "password": "wrongpass"}
        resp = self.client.post(self.url, data)
        self.assertEqual(resp.status_code, 200)
        # Non-field error message from messages framework or form
        self.assertContains(resp, "correct username and password")
        self.assertTrue(resp.wsgi_request.user.is_anonymous)

    def test_session_expires_on_browser_close_if_remember_me_unchecked(self):
        """When 'remember_me' is unchecked, session should expire on browser close."""
        data = {"username": "ivy", "password": "StrongPassw0rd!"}
        resp = self.client.post(self.url, data, follow=True)
        session = resp.wsgi_request.session
        print("Expire on browser close:", session.get_expire_at_browser_close())
        self.assertTrue(
            session.get_expire_at_browser_close(),
            "Expected session to expire at browser close, but it does not."
        )

    def test_session_persists_if_remember_me_checked(self):
        """Checked 'remember_me' sets a 2-week session expiry."""
        data = {"username": "ivy", "password": "StrongPassw0rd!", "remember_me": True}
        resp = self.client.post(self.url, data, follow=True)
        session = resp.wsgi_request.session
        expiry = session.get_expiry_age()
        self.assertEqual(expiry, 1209600, f"Expected 1209600, got {expiry}")


class LogoutFlowTests(TestCase):
    """Class tests for Logging out a User."""

    def setUp(self):
        """Temporarily sets up a User Object to test logout."""
        self.user = User.objects.create_user(username="zoe", password="StrongPassw0rd!")
        self.home_url = reverse("home")
        self.logout_url = reverse("logout")

    def test_post_logout_redirects_home_with_logout_qs_and_logs_out(self):
        """POST logout redirects to home page."""
        self.client.login(username="zoe", password="StrongPassw0rd!")
        resp = self.client.post(self.logout_url, follow=False)
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp["Location"].startswith(self.home_url))
        self.assertIn("logout=1", resp["Location"])

        resp2 = self.client.get(resp["Location"])
        self.assertEqual(resp2.status_code, 200)
        self.assertTrue(resp2.wsgi_request.user.is_anonymous)

    def test_get_logout_also_redirects_home_with_qs(self):
        """GET logout redirects to home page."""
        self.client.login(username="zoe", password="StrongPassw0rd!")
        resp = self.client.get(self.logout_url, follow=False)
        self.assertEqual(resp.status_code, 302)
        self.assertIn("logout=1", resp["Location"])


class HeaderRenderingTests(TestCase):
    """Class tests for Header Rendering (showing Header Menu when user logs in)."""

    def setUp(self):
        """Set up the testing conditions with urls needed."""
        self.home_url = reverse("home")
        self.feed_url = reverse(FEED_NAME)
        self.posts_url = reverse("users:my_posts")
        self.follows_url = reverse("users:my_follows")

    def test_anonymous_header_has_no_auth_nav_elements(self):
        """Tests main functionalities of header menu when user is not logged in."""
        resp = self.client.get(self.home_url)
        html = resp.content.decode("utf-8")
        self.assertNotIn('id="burgerBtn"', html)
        self.assertNotIn('id="mobileOverlay"', html)
        self.assertNotIn('id="mobileMenu"', html)
        self.assertIn("LITReview", html)

    def test_authenticated_header_has_burger_overlay_drawer_and_nav_links(self):
        """Tests main functionalities of header menu when user is logged in."""
        User.objects.create_user(username="yan", password="StrongPassw0rd!")
        self.client.login(username="yan", password="StrongPassw0rd!")
        resp = self.client.get(self.home_url)
        html = resp.content.decode("utf-8")

        self.assertIn('id="burgerBtn"', html)
        self.assertIn('id="mobileOverlay"', html)
        self.assertIn('id="mobileMenu"', html)

        self.assertIn(self.feed_url, html)
        self.assertIn(self.posts_url, html)
        self.assertIn(self.follows_url, html)
        self.assertIn(reverse("logout"), html)


class ReviewsAccessTests(TestCase):
    """Class tests for Reviews Access."""

    def setUp(self):
        """Set up the testing conditions with urls needed."""
        self.feed_url = reverse(FEED_NAME)

    def test_feed_requires_login(self):
        """Tests access to feed page if user is not logged in."""
        resp = self.client.get(self.feed_url, follow=False)
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse("home"), resp["Location"])

    def test_feed_renders_when_logged_in(self):
        """Tests user access to feed page if user is logged in."""
        User.objects.create_user(username="kim", password="StrongPassw0rd!")
        self.client.login(username="kim", password="StrongPassw0rd!")
        resp = self.client.get(self.feed_url)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Flux", resp.content)


class MyFollowsViewTests(TestCase):
    """Tests for the `my_follows` view (listing and creating follow relations)."""

    def setUp(self):
        """Create two users and log `alice` in before each test."""
        self.user = User.objects.create_user(
            username="alice",
            password="password123",
            email="alice@example.com",
        )
        self.other = User.objects.create_user(
            username="bob",
            password="password123",
            email="bob@example.com",
        )
        self.client.login(username="alice", password="password123")
        self.url = reverse("users:my_follows")

    def test_my_follows_get_displays_following_and_followers(self):
        """GET should populate following_list and followers_list in the context."""
        # alice -> bob
        UserFollows.objects.create(user=self.user, followed_user=self.other)
        # bob -> alice
        UserFollows.objects.create(user=self.other, followed_user=self.user)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/pages/follows.html")

        following_list = list(response.context["following_list"])
        followers_list = list(response.context["followers_list"])

        self.assertIn(self.other, following_list)
        self.assertIn(self.other, followers_list)

    def test_my_follows_post_with_empty_username_shows_error(self):
        """POST with an empty username must not create a follow relation."""
        initial_count = UserFollows.objects.count()

        response = self.client.post(self.url, {"username": ""})

        # redirect_with_toast redirects back to the page with a querystring
        self.assertEqual(response.status_code, 302)
        self.assertIn(self.url, response["Location"])
        self.assertEqual(UserFollows.objects.count(), initial_count)

    def test_my_follows_post_with_nonexistent_user_shows_error(self):
        """POST with an unknown username must not create a follow relation."""
        initial_count = UserFollows.objects.count()

        response = self.client.post(self.url, {"username": "does_not_exist"})

        self.assertEqual(response.status_code, 302)
        self.assertIn(self.url, response["Location"])
        self.assertEqual(UserFollows.objects.count(), initial_count)

    def test_my_follows_post_cannot_follow_self(self):
        """POST with own username should be rejected and not create a relation."""
        initial_count = UserFollows.objects.count()

        response = self.client.post(self.url, {"username": self.user.username})

        self.assertEqual(response.status_code, 302)
        self.assertIn(self.url, response["Location"])
        self.assertEqual(UserFollows.objects.count(), initial_count)

    def test_my_follows_post_existing_follow_shows_info(self):
        """POST for an already-followed user must not create a duplicate row."""
        UserFollows.objects.create(user=self.user, followed_user=self.other)
        initial_count = UserFollows.objects.count()

        response = self.client.post(self.url, {"username": self.other.username})

        self.assertEqual(response.status_code, 302)
        self.assertIn(self.url, response["Location"])
        # No duplicate relation created
        self.assertEqual(UserFollows.objects.count(), initial_count)

    def test_my_follows_post_creates_follow_when_valid(self):
        """POST with a valid new username must create a follow relation."""
        initial_count = UserFollows.objects.count()

        response = self.client.post(self.url, {"username": self.other.username})

        self.assertEqual(response.status_code, 302)
        self.assertIn(self.url, response["Location"])
        self.assertEqual(UserFollows.objects.count(), initial_count + 1)

        self.assertTrue(
            UserFollows.objects.filter(
                user=self.user,
                followed_user=self.other,
            ).exists()
        )


class UnfollowUserViewTests(TestCase):
    """Tests for the unfollow_user view (removing follow relations)."""

    def setUp(self):
        """Create a logged-in user and a second user as an unfollow target."""
        self.user = User.objects.create_user(
            username="charlie",
            password="password123",
            email="charlie@example.com",
        )
        self.other = User.objects.create_user(
            username="diana",
            password="password123",
            email="diana@example.com",
        )
        self.client.login(username="charlie", password="password123")
        self.my_follows_url = reverse("users:my_follows")

    def _unfollow_url(self, user_id):
        """Use a helper to build the unfollow_user URL for a given user id."""
        return reverse("users:unfollow", args=[user_id])

    def test_unfollow_user_get_redirects_to_my_follows(self):
        """GET requests should redirect back to the my_follows page."""
        response = self.client.get(self._unfollow_url(self.other.id))
        self.assertEqual(response.status_code, 302)
        self.assertIn(self.my_follows_url, response["Location"])

    def test_unfollow_user_post_for_nonexistent_user_shows_error(self):
        """POST for a non-existent user should redirect with an error toast."""
        response = self.client.post(self._unfollow_url(9999))

        self.assertEqual(response.status_code, 302)
        self.assertIn(self.my_follows_url, response["Location"])

    def test_unfollow_user_post_when_not_following_shows_error(self):
        """POST when no follow relation exists should redirect with an error."""
        # target exists, but there is no UserFollows row
        response = self.client.post(self._unfollow_url(self.other.id))

        self.assertEqual(response.status_code, 302)
        self.assertIn(self.my_follows_url, response["Location"])

    def test_unfollow_user_post_deletes_relation_and_redirects(self):
        """POST should delete the follow relation and redirect to my_follows."""
        relation = UserFollows.objects.create(
            user=self.user,
            followed_user=self.other,
        )
        self.assertTrue(
            UserFollows.objects.filter(pk=relation.pk).exists()
        )

        response = self.client.post(self._unfollow_url(self.other.id))

        self.assertEqual(response.status_code, 302)
        self.assertIn(self.my_follows_url, response["Location"])
        self.assertFalse(
            UserFollows.objects.filter(pk=relation.pk).exists()
        )
