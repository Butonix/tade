from functools import lru_cache
import datetime
import typing
from email.utils import make_msgid
from django.utils.functional import cached_property
from django.apps import AppConfig
from django.conf import settings
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe


class TadeAppConfig(AppConfig):
    name = "tade"  # python path
    label = "tade"  # python identifier
    verbose_name = "tade"  # full human readable name, override this

    subtitle = "is a community about human curiosity and interests."

    BANNED_USERNAMES = [
        "admin",
        "administrator",
        "contact",
        "fraud",
        "guest",
        "help",
        "hostmaster",
        "tade",
        "Cher",
        "mailer-daemon",
        "moderator",
        "moderators",
        "nobody",
        "postmaster",
        "root",
        "security",
        "support",
        "sysop",
        "webmaster",
        "enable",
        "new",
        "signup",
    ]

    # days old accounts are considered new for
    NEW_USER_DAYS = 70

    # minimum karma required to be able to add/change Tag objects
    MIN_KARMA_TO_EDIT_TAGS = 5

    # minimum karma required to be able to offer title/tag suggestions
    MIN_KARMA_TO_SUGGEST = 10

    # minimum karma required to be able to flag comments
    MIN_KARMA_TO_FLAG = 50

    # minimum karma required to be able to submit new stories
    MIN_KARMA_TO_SUBMIT_STORIES = -4

    # minimum karma required to process invitation requests
    MIN_KARMA_FOR_INVITATION_REQUESTS = MIN_KARMA_TO_FLAG

    # proportion of posts authored by user to consider as heavy self promoter
    HEAVY_SELF_PROMOTER_PROPORTION = 0.51

    # minimum number of submitted stories before checking self promotion
    MIN_STORIES_CHECK_SELF_PROMOTION = 2

    WEB_PROTOCOL = "http"  # Used when generating URLs, replace with "https" if needed

    DEFAULT_FROM_EMAIL = settings.DEFAULT_FROM_EMAIL
    DIGEST_SUBJECT = f"[{verbose_name}] digest for"
    INVITATION_SUBJECT = f"Your invitation to {verbose_name}"
    INVITATION_BODY = "Visit the following url to complete your registration:"
    INVITATION_FROM = DEFAULT_FROM_EMAIL
    NOTIFICATION_FROM = DEFAULT_FROM_EMAIL

    MAILING_LIST_ID = verbose_name
    MAILING_LIST_ADDRESS = None  # If None, will be MAILING_LIST_ID@config.get_domain()
    MAILING_LIST_FROM = (
        None  # If None, poster's username@domain.tld will be used as From address
    )

    STORIES_PER_PAGE = 20

    FTS_DATABASE_NAME = "fts"
    FTS_DATABASE_FILENAME = "fts.db"
    FTS_COMMENTS_TABLE_NAME = "fts5_comments"
    FTS_STORIES_TABLE_NAME = "fts5_stories"

    MENTION_TOKENIZER_NAME = "mention_tokenizer"

    SEND_WEBMENTIONS = True

    FORMAT_QUOTED_MESSAGES = True
    DETECT_USERNAME_MENTIONS_IN_COMMENTS = True
    MAILING_LIST = True

    SHOW_GIT_REPOSITORY_IN_ABOUT_PAGE = True
    SHOW_GIT_COMMIT_IN_FOOTER = True

    ALLOW_INVITATION_REQUESTS = True

    ALLOW_REGISTRATIONS = True

    REQUIRE_VOUCH_FOR_PARTICIPATION = True

    DISALLOW_REPOSTS_PERIOD: typing.Optional[datetime.timedelta] = datetime.timedelta(
        weeks=1
    )

    ENABLE_KARMA = True

    VISIBLE_KARMA = False

    @cached_property
    def post_ranking(self) -> "tade.voting.PostRanking":
        # from tade.voting import TemporalRanking
        # return TemporalRanking()
        from tade.voting import KarmaRanking

        return KarmaRanking()

    @property
    def html_label(self):
        """Override this to change HTML label used in static html"""
        return mark_safe("<strong><code>[tade]</code></strong>")

    @property
    def html_subtitle(self):
        """Override this to change HTML subtitle used in static html"""
        return mark_safe(
            "is a community about everything that piques your curiosity and interest"
        )

    @property
    def html_signup_request_info(self):
        ret = f"""You will need an invitation from an existing user to join. You can ask someone you know, or on <a href="{reverse_lazy('about')}">IRC</a>"""
        if TadeAppConfig.ALLOW_INVITATION_REQUESTS:
            ret += " or submit an invitation request here. Members of the community can review your request and send you an invite."
        else:
            ret += "."
        return mark_safe(ret)

    def ready(self):
        import tade.notifications
        import tade.webmention
        import tade.mail
        import tade.jobs
        import tade.flatpages

    @staticmethod
    @lru_cache(maxsize=None)
    def get_domain():
        from .models import Site

        return Site.objects.get_current().domain

    @staticmethod
    def make_msgid():
        domain = TadeAppConfig.get_domain()
        return make_msgid(domain=domain)

    @staticmethod
    @lru_cache(maxsize=None)
    def mailing_list_address() -> str:
        if TadeAppConfig.MAILING_LIST_ADDRESS:
            return TadeAppConfig.MAILING_LIST_ADDRESS
        return f"{TadeAppConfig.MAILING_LIST_ID}@{TadeAppConfig.get_domain()}"
