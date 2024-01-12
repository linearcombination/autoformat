import sys

from typing import Any, Mapping, Optional, Sequence, TypeVar
import os
from os.path import exists, join, sep, basename

from document.domain import resource_lookup
from document.config import settings
from document.domain import parsing
from document.utils.file_utils import (
    delete_tree,
    load_json_object,
    source_file_needs_update,
)
import urllib
from urllib.request import urlopen
from contextlib import closing
from pathlib import Path
import shutil


from pydantic import HttpUrl


T = TypeVar("T")

# We'll want some code that systematically goes through all heart
# language repos to:
#
# - use translations.json or (eventually) the new graphql data API to find (mirrored) repo URL
# - clone each repo locally
# - check for issues using catalog of known issues
#   - if issue found, log it to file (in some suitable format)
#   - logs can then be manually inspected and approved by annotation for actual processing
#   - on second (elevated) pass revisit only logged issues
#     - for each logged issue:
#       - open issue using PORT api with standardized description
#       - attempt programmatic resolution
#       - notify (who? PORT will take care of this) of success or failure of resolution
#       - reparse asset to verify resolution
#       - if resolved then notify content team (via issue? this was suggested but is an odd use of issues)

# Common issues:
#
# - Upper \V instead of lowercase \v verse markers
# - Git merge conflict markers committed into source
# - Consecutive verse markers without content followed by content for all those verses
# - Upper \C instead of lowercase \c chapter markers


logger = settings.logger(__name__)


def resource_types_and_names(
    lang_code: str,
    working_dir: str = settings.RESOURCE_ASSETS_DIR,
    english_resource_type_map: Mapping[str, str] = settings.ENGLISH_RESOURCE_TYPE_MAP,
    id_resource_type_map: Mapping[str, str] = settings.ID_RESOURCE_TYPE_MAP,
    translations_json_location: HttpUrl = settings.TRANSLATIONS_JSON_LOCATION,
    usfm_resource_types: Sequence[str] = settings.USFM_RESOURCE_TYPES,
    tn_resource_types: Sequence[str] = settings.TN_RESOURCE_TYPES,
    tq_resource_types: Sequence[str] = settings.TQ_RESOURCE_TYPES,
    tw_resource_types: Sequence[str] = settings.TW_RESOURCE_TYPES,
) -> Sequence[tuple[str, str]]:
    if lang_code == "en":
        return [(key, value) for key, value in english_resource_type_map.items()]
    if lang_code == "id":
        return [(key, value) for key, value in id_resource_type_map.items()]
    data = resource_lookup.fetch_source_data(
        working_dir, str(translations_json_location)
    )
    for item in [lang for lang in data if lang["code"] == lang_code]:
        values = [
            (
                resource_type["code"],
                "{} ({})".format(
                    resource_type["name"] if "name" in resource_type else "",
                    resource_type["code"],
                ),
            )
            for resource_type in item["contents"]
            if (
                resource_type["code"]
                in [
                    *usfm_resource_types,
                    *tn_resource_types,
                    *tq_resource_types,
                    *tw_resource_types,
                ]
            )
        ]
    return sorted(values, key=lambda value: value[0])


def log_event(context: dict[str, T]) -> None:
    logger.debug(context)


def delete_asset(resource_dir: str, dir_to_preserve: str = "temp") -> None:
    parent_dir = str(Path(resource_dir).parent.absolute())
    if dir_to_preserve != Path(parent_dir).name:
        delete_tree(parent_dir)
    elif dir_to_preserve != Path(resource_dir).name:
        delete_tree(resource_dir)


def main() -> None:
    """
    Check heart language USFM assets.

    Usage:
    >>> main()
    """
    heart_lang_codes_and_names = [
        lang_code_and_name
        for lang_code_and_name in resource_lookup.lang_codes_and_names()
        if not lang_code_and_name[2]
    ]
    for lang_code_and_name in heart_lang_codes_and_names:
        usfm_check_for_lang(lang_code_and_name)


def usfm_check_for_lang(
    lang_code_and_name: tuple[str, str, bool],
    usfm_resource_types: Sequence[str] = settings.USFM_RESOURCE_TYPES,
) -> None:
    """
    Check USFM for language

    Usage:
    >>> usfm_check_for_lang(("auh", "Aushi"))
    """
    # logger.debug("About to get data for language: %s", lang_code_and_name)
    # Could be more than one USFM type per language, e.g., ulb and f10
    usfm_resource_types_and_names = [
        resource_type_and_name
        for resource_type_and_name in resource_types_and_names(lang_code_and_name[0])
        if resource_type_and_name[0] in usfm_resource_types
    ]
    book_codes = resource_lookup.book_codes_for_lang(lang_code_and_name[0])
    for book_code in book_codes:
        for usfm_resource_type_and_name in usfm_resource_types_and_names:
            # FIXME usfm_resource_lookup uses translations.json to find lookup info.
            # Bear in mind that if we are working with mirrored repos that are not
            # in translations.json this is a chicken before the egg situation.
            # However, if we find the issue in the repo pointed to by
            # translations.json then we can subsequently lookup its mirrored repo
            # using some reliable URL naming pattern and make changes on the
            # mirrored repo.
            resource_lookup_dto = resource_lookup.usfm_resource_lookup(
                lang_code_and_name[0],
                usfm_resource_type_and_name[0],
                book_code[0],
            )
            # FIXME Some assets will not be git repos, for those that are zip files we can
            # at least find issues. We would need to determine the git repo where
            # the zips are coming from in order to see if that repo was mirrored so
            # that we could clone and make changes there.
            #
            # Check if the resource has already been checked and only proceed for
            # this resource if resource_dir does not physically exist. This makes
            # usfm_checker restartable, which is nice since it checks a LOT of
            # repos.
            resource_dir = resource_lookup.resource_directory(
                resource_lookup_dto.lang_code,
                resource_lookup_dto.book_code,
                resource_lookup_dto.resource_type,
            )
            if exists(resource_dir):
                continue
            resource_dir = resource_lookup.provision_asset_files(resource_lookup_dto)
            content_file = None
            html: Optional[str] = None
            try:
                content_file = parsing.usfm_asset_file(
                    resource_lookup_dto, resource_dir
                )
                html = parsing.usfm_asset_html(content_file, resource_lookup_dto)
            except:
                logger.exception("Failed due to the following exception")
            if not content_file:
                # TODO This is likely because the
                # resource_lookup_dto.url attribute was None which is likely because another
                # jsonpath needs to be added to find the URL in resource_lookup.usfm_resource_lookup
                log_event(
                    {
                        "event": "content_file is None",
                        "resource_lookup_dto": resource_lookup_dto,
                        "content_file": content_file,
                        "resource_dir": resource_dir,
                    }
                )
            elif not html:
                log_event(
                    {
                        "event": "html is None",
                        "resource_lookup_dto": resource_lookup_dto,
                        "content_file": content_file,
                        "resource_dir": resource_dir,
                    }
                )
            elif html and not len(html) > 300:
                # TODO Start going through catalog of checks on
                # scripture source to determine the issues and
                # possibly fix them programmatically
                log_event(
                    {
                        "event": "len(html) <= 300",
                        "resource_lookup_dto": resource_lookup_dto,
                        "content_file": content_file,
                        "resource_dir": resource_dir,
                    }
                )
                # TODO Possibly Add the removal of repo
            else:
                log_event(
                    {
                        "event": "parses to HTML fine",
                        "resource_lookup_dto": resource_lookup_dto,
                        "content_file": content_file,
                        "resource_dir": resource_dir,
                    }
                )
                # We can delete the resource directory of the
                # successfully parsed resource to conserve space
                delete_asset(resource_dir)


if __name__ == "__main__":

    # To run the doctests in the this module, in the root of the project do:
    # FROM_EMAIL_ADDRESS=... python backend/usfm_checker.py
    # See https://docs.python.org/3/library/doctest.html
    # for more details.
    import doctest

    doctest.testmod()
