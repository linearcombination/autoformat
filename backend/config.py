"""This module provides configuration values used by the application."""
import logging
from collections.abc import Mapping, Sequence
from logging import config as lc
from typing import Optional, final

import yaml
from pydantic import field_validator, AnyHttpUrl, EmailStr, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

HtmlContent = str


@final
class Settings(BaseSettings):
    """
    BaseSettings subclasses like this one allow values of constants to
    be overridden by environment variables like those defined in env
    files, e.g., ../../.env or by system level environment variables
    (which have higher priority).
    """

    REPO_URL_DICT_KEY: str = "../download-scripture?repo_url"
    ALT_REPO_URL_DICT_KEY: str = "/download-scripture?repo_url"

    # The location where the JSON data file that we use to lookup
    # location of resources is located.
    TRANSLATIONS_JSON_LOCATION: HttpUrl
    # The jsonpath format string for the resource's git repo for a given language, resource type, and book.
    RESOURCE_DOWNLOAD_FORMAT_JSONPATH: str = "$[?code='{}'].contents[?code='{}'].subcontents[?code='{}'].links[?format='Download'].url"
    # All resource types.
    # The jsonpath format string for resource types for a given language.
    # jsonpath for all resource codes.
    # jsonpath format string for all resource codes for a given language.
    RESOURCE_CODES_FOR_LANG_JSONPATH: str = (
        "$[?code='{}'].contents[*].subcontents[*].code"
    )
    # The jsonpath format string for individual USFM files (per bible book) for a given language, resource type, and book.
    INDIVIDUAL_USFM_URL_JSONPATH: str = "$[?code='{}'].contents[?code='{}'].subcontents[?code='{}'].links[?format='usfm'].url"
    # The jsonpath format string for resource URL for a given lanaguage and resource type.
    RESOURCE_URL_LEVEL1_JSONPATH: str = (
        "$[?code='{}'].contents[?code='{}'].links[?format='zip'].url"
    )
    # The jsonpath format string for a given language's name.
    RESOURCE_LANG_NAME_JSONPATH: str = "$[?code='{}'].name"
    # The jsonpath format string to the resource type's name for a given language and resource type.
    RESOURCE_TYPE_NAME_JSONPATH: str = "$[?code='{}'].contents[?code='{}'].name"
    # The jsonpath format string for a zip URL for a given language and resource code.
    RESOURCE_URL_LEVEL2_JSONPATH: str = (
        "$[?code='{}'].contents[*].subcontents[?code='{}'].links[?format='zip'].url"
    )
    LTR_DIRECTION_HTML: str = "<div style='direction: ltr;'>"
    RTL_DIRECTION_HTML: str = "<div style='direction: rtl;'>"

    END_OF_CHAPTER_HTML: str = '<div class="end-of-chapter"></div>'
    LANGUAGE_FMT_STR: str = "<h1 style='text-align: center'>Language: {}</h1>"
    RESOURCE_TYPE_NAME_FMT_STR: str = "<h1>{}</h1>"
    TN_VERSE_NOTES_ENCLOSING_DIV_FMT_STR: str = "<div style='column-count: 2;'>{}</div>"
    TQ_HEADING_AND_QUESTIONS_FMT_STR: str = (
        "<h3>{}</h3>\n<div style='column-count: 2;'>{}</div>"
    )
    HTML_ROW_BEGIN: HtmlContent = HtmlContent("<div class='row'>")
    HTML_ROW_END: HtmlContent = HtmlContent("</div>")
    HTML_COLUMN_BEGIN: HtmlContent = HtmlContent("<div class='column'>")
    HTML_COLUMN_END: HtmlContent = HtmlContent("</div>")
    HTML_COLUMN_LEFT_BEGIN: HtmlContent = HtmlContent("<div class='column-left'>")
    HTML_COLUMN_RIGHT_BEGIN: HtmlContent = HtmlContent("<div class='column-right'>")
    BOOK_NAME_FMT_STR: str = "<h2 style='text-align: center;'>{}</h2>"
    BOOK_FMT_STR: str = "<h2 style='text-align: center;'>{}</h2>"
    # TODO Should this be center aligned too?
    BOOK_AS_GROUPER_FMT_STR: str = "<h1>{}</h1>"
    CHAPTER_HEADER_FMT_STR: str = '<h2 class="c-num" id="{}-{}-ch-{}">Chapter {}</h2>'
    UNORDERED_LIST_BEGIN_STR: HtmlContent = HtmlContent("<ul>")
    UNORDERED_LIST_END_STR: HtmlContent = HtmlContent("</ul>")
    TRANSLATION_WORD_LIST_ITEM_FMT_STR: HtmlContent = HtmlContent(
        '<li><a href="#{}-{}">{}</a></li>'
    )
    TRANSLATION_WORD_VERSE_SECTION_HEADER_STR: HtmlContent = HtmlContent(
        "<h4>Uses:</h4>"
    )
    TRANSLATION_WORD_VERSE_REF_ITEM_FMT_STR: str = (
        '<li><a href="#{}-{}-ch-{}-v-{}">{} {}:{}</a></li>'
    )
    FOOTNOTES_HEADING: HtmlContent = HtmlContent("<h4>Footnotes</h4>")
    OPENING_H3_FMT_STR: str = "<h3>{}"
    OPENING_H3_WITH_ID_FMT_STR: str = '<h3 id="{}-{}">{}'
    TRANSLATION_WORD_ANCHOR_LINK_FMT_STR: str = "[{}](#{}-{})"
    TRANSLATION_WORD_PREFIX_ANCHOR_LINK_FMT_STR: str = "({}: [{}](#{}-{}))"
    TRANSLATION_WORD_PREFIX_FMT_STR: str = "({}: {})"
    # TRANSLATION_NOTE_ANCHOR_LINK_FMT_STR: str = "[{}](#{}-{}-tn-ch-{}-v-{})"
    TRANSLATION_NOTE_ANCHOR_LINK_FMT_STR: str = "[{}](#{}-{}-ch-{}-v-{})"
    VERSE_ANCHOR_ID_FMT_STR: str = 'id="(.+?)-ch-(.+?)-v-(.+?)"'
    VERSE_ANCHOR_ID_SUBSTITUTION_FMT_STR: str = r"id='{}-\1-ch-\2-v-\3'"

    USFM_RESOURCE_TYPES: Sequence[str] = [
        "ayt",
        "cuv",
        "f10",
        "nav",
        "reg",
        # "udb", # 2023-06-20 Content team doesn't want this used.
        # "udb-wa", # 2022-05-12 - Content team doesn't want this used.
        "ugnt",
        # "uhb", # parser blows on: AttributeError: 'SingleHTMLRenderer' object has no attribute 'renderCAS'
        "ulb",
        "usfm",
    ]
    # f10 for fr, and udb for many other languages are secondary USFM types,
    # meaning: for those languages that have them those same languages have
    # a primary USFM type such as ulb (there can be other primary USFM types
    # besides ulb such as cuv, reg, nav, etc.). For v1, we only allow use of
    # a primary USFM type since v1 has a requirement that the user is not to
    # choose resource types in the UI, so we use this next list to manage
    # that when we automatically choose the reesource types (from the USFM
    # and TN resource types that translations.json lists as available) for
    # the GL languages and books chosen.
    EN_USFM_RESOURCE_TYPES: Sequence[str] = ["ulb-wa"]
    TN_RESOURCE_TYPES: Sequence[str] = ["tn"]
    EN_TN_RESOURCE_TYPES: Sequence[str] = ["tn-wa"]
    TQ_RESOURCE_TYPES: Sequence[str] = ["tq"]
    EN_TQ_RESOURCE_TYPES: Sequence[str] = ["tq-wa"]
    TW_RESOURCE_TYPES: Sequence[str] = ["tw"]
    EN_TW_RESOURCE_TYPES: Sequence[str] = ["tw-wa"]
    BC_RESOURCE_TYPES: Sequence[str] = ["bc-wa"]
    # List of language codes for which there is a content issue
    # such that a complete document request cannot
    # be formed. E.g., hu doesn't have any resource types or book
    # codes in translations.json. E.g., abz's content has unresolved
    # git merge markers in source that were accidentally committed.
    # TODO Test to see which of these languages can be added back now
    # that several content defect handling features have been added.
    LANG_CODE_FILTER_LIST: Sequence[str] = [
        "acq",
        "gaj-x-ymnk",
        "fa",
        "hr",
        "hu",
        # "id",  # Was on this list because of licensing issues
        "kbt",
        "kip",
        "lus",
        "mor",
        "mve",
        "pmy",  # Currently doesn't provide USFM, but might soon
        "sr-Latn",
        "tig",
        "tem",
    ]
    GATEWAY_LANGUAGES: Sequence[str] = [
        "am",
        "arb",
        "as",
        "bn",
        "pt-br",
        "my",
        "ceb",
        "zh",
        "en",
        "fr",
        "gu",
        "ha",
        "hi",
        "ilo",
        "id",
        "kn",
        "km",
        "lo",
        "es-419",
        "plt",
        "ml",
        "mr",
        "ne",
        "or",
        "pmy",
        "fa",
        "pa",
        "ru",
        "sw",
        "tl",
        "ta",
        "te",
        "th",
        "tpi",
        "ur",
        "ur-deva",
        "vi",
    ]

    # fmt: off
    BC_ARTICLE_URL_FMT_STR: str = "https://content.bibletranslationtools.org/WycliffeAssociates/en_bc/src/branch/master/{}"
    # fmt: on

    OXML_LANGUAGE_LIST: list[str] = [
        "ar-SA",
        "bg-BG",
        "zh-CN",
        "zh-TW",
        "hr-HR",
        "cs-CZ",
        "da-DK",
        "nl-NL",
        "en-US",
        "et-EE",
        "fi-FI",
        "fr-FR",
        "de-DE",
        "el-GR",
        "he-IL",
        "hi-IN",
        "hu-HU",
        "id-ID",
        "it-IT",
        "ja-JP",
        "kk-KZ",
        "ko-KR",
        "lv-LV",
        "lt-LT",
        "ms-MY",
        "nb-NO",
        "pl-PL",
        "pt-BR",
        "pt-PT",
        "ro-RO",
        "ru-RU",
        "sr-latn-RS",
        "sk-SK",
        "sl-SI",
        "es-ES",
        "sv-SE",
        "th-TH",
        "tr-TR",
        "uk-UA",
        "vi-VN",
    ]
    OXML_LANGUAGE_LIST_LOWERCASE: list[str] = [
        language.lower() for language in OXML_LANGUAGE_LIST
    ]
    OXML_LANGUAGE_LIST_LOWERCASE_SPLIT: list[str] = [
        language for language in OXML_LANGUAGE_LIST_LOWERCASE if "-" in language
    ]

    def logger(self, name: str) -> logging.Logger:
        """
        Return a Logger for scope named by name, e.g., module, that can be
        used for logging.
        """
        with open(self.LOGGING_CONFIG_FILE_PATH, "r") as fin:
            logging_config = yaml.safe_load(fin.read())
            lc.dictConfig(logging_config)
        return logging.getLogger(name)

    def api_test_url(self) -> str:
        """Non-secure local URL for running the Fastapi server for testing."""
        return "http://{}:{}".format(self.API_TEST_BASE_URL, self.API_LOCAL_PORT)

    API_TEST_BASE_URL: str = "http://localhost"

    API_LOCAL_PORT: int

    USE_GIT_CLI: bool = False

    LOGGING_CONFIG_FILE_PATH: str = "backend/logging_config.yaml"

    # Location where resource assets will be downloaded.
    RESOURCE_ASSETS_DIR: str = "working/temp"

    # Location where generated PDFs will be written to.
    DOCUMENT_OUTPUT_DIR: str = "working/output"

    # Location where generated PDFs will be written to.
    DOCUMENT_SERVE_DIR: str = "document_output"

    # For options see https://wkhtmltopdf.org/usage/wkhtmltopdf.txt

    # Return the message to show to user on successful generation of
    # PDF.
    SUCCESS_MESSAGE: str = "Success! Please retrieve your generated document using a GET REST request to /pdf/{document_request_key} or /epub/{document_request_key} or /docx/{document_request_key} (depending on whether you requested PDF, ePub, or Docx result) where document_request_key is the finished_document_request_key in this payload."

    BACKEND_CORS_ORIGINS: list[str]

    # Return the file names, excluding suffix, of files that do not
    # contain content but which may be in the same directory or
    # subdirectories of a resource's acquired files.

    ENGLISH_GIT_REPO_MAP: Mapping[str, str] = {
        "ulb-wa": "https://content.bibletranslationtools.org/WycliffeAssociates/en_ulb",
        "udb-wa": "https://content.bibletranslationtools.org/WycliffeAssociates/en_udb",
        "tn-wa": "https://content.bibletranslationtools.org/WycliffeAssociates/en_tn",
        "tw-wa": "https://content.bibletranslationtools.org/WycliffeAssociates/en_tw",
        "tq-wa": "https://content.bibletranslationtools.org/WycliffeAssociates/en_tq",
        "bc-wa": "https://content.bibletranslationtools.org/WycliffeAssociates/en_bc",
    }
    ID_GIT_REPO_MAP: Mapping[str, str] = {
        "ayt": "https://content.bibletranslationtools.org/WA-Catalog/id_ayt",
        "tn": "https://content.bibletranslationtools.org/WA-Catalog/id_tn",
        "tq": "https://content.bibletranslationtools.org/WA-Catalog/id_tq",
        "tw": "https://content.bibletranslationtools.org/WA-Catalog/id_tw",
    }

    ENGLISH_RESOURCE_TYPE_MAP: Mapping[str, str] = {
        "ulb-wa": "Unlocked Literal Bible (ULB)",
        # "udb-wa": "Unlocked Dynamic Bible (UDB)",
        "tn-wa": "ULB Translation Notes",
        "tq-wa": "ULB Translation Questions",
        "tw-wa": "ULB Translation Words",
        "bc-wa": "Bible Commentary",
    }

    ID_LANGUAGE_NAME: str = "Bahasa Indonesian"
    ID_RESOURCE_TYPE_MAP: Mapping[str, str] = {
        "ayt": "Bahasa Indonesian Bible (ayt)",
        "tn": "Translation Helps (tn)",
        "tq": "Translation Questions (tq)",
        "tw": "Translation Words (tw)",
    }

    TEMPLATE_PATHS_MAP: Mapping[str, str] = {
        "book_intro": "backend/templates/tn/book_intro_template.md",
        "header_enclosing": "backend/templates/html/header_enclosing.html",
        "header_no_css_enclosing": "backend/templates/html/header_no_css_enclosing.html",
        "header_compact_enclosing": "backend/templates/html/header_compact_enclosing.html",
        "footer_enclosing": "backend/templates/html/footer_enclosing.html",
        "cover": "backend/templates/html/cover.html",
        "email-html": "backend/templates/html/email.html",
        "email": "backend/templates/text/email.txt",
    }

    DOCX_TEMPLATE_PATH: str = "/app/template.docx"
    DOCX_COMPACT_TEMPLATE_PATH: str = "/app/template_compact.docx"

    # Return boolean indicating if caching of generated documents should be
    # cached.
    ASSET_CACHING_ENABLED: bool = True
    # Caching window of time in which asset
    # files on disk are considered fresh rather than re-acquiring (in
    # the case of resource asset files) or re-generating them (in the
    # case of the final PDF). In hours.
    ASSET_CACHING_PERIOD: int

    # It doesn't yet make sense to offer the (high level)
    # assembly strategy _and_ the assembly sub-strategy to the end user
    # as a document request parameter so we'll just choose an arbitrary
    # sub-strategy here. This means that we can write code for multiple
    # sub-strategies and choose one to put in play at a time here.

    # Return a list of the Markdown section titles that our
    # Python-Markdown remove_section_processor extension should remove.
    MARKDOWN_SECTIONS_TO_REMOVE: list[str] = [
        "Examples from the Bible stories",
        "Links",
        "Picture of",
        "Pictures",
    ]

    # Provided by .env file:
    EMAIL_SEND_SUBJECT: str
    TO_EMAIL_ADDRESS: EmailStr

    # Provided by system env vars (fake values provided so github action can run):
    FROM_EMAIL_ADDRESS: EmailStr = "foo@example.com"
    SMTP_HOST: str = "https://example.com"
    SMTP_PORT: int = 111
    SMTP_PASSWORD: str = "fakepass"
    SEND_EMAIL: bool = False

    # Used by gunicorn
    PORT: int
    # local image tag for local dev with prod image
    IMAGE_TAG: str

    # Example fake user agent value required by domain host to allow serving
    # files. Other values could possibly work. This value definitely
    # works.
    USER_AGENT: str = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11"

    # Used in assembly_strategy_utils modeule when zero-filling various strings
    NUM_ZEROS: int = 3

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)


# mypy with pydantic v2 doesn't understand that defaults will be picked up from .env file as they had been in v1
settings = Settings()  # type: ignore
# Could also use:
# settings: Settings = Settings.parse_obj({})
# settings = Settings(_env_file=".env", _env_file_encoding="utf-8")
