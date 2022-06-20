import ast
import os

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from dotenv import find_dotenv, load_dotenv


def get_env_value(env_variable, default_value=None):
    try:
        if default_value is None:
            return os.environ[env_variable]
        return os.getenv(env_variable, default_value)
    except KeyError:
        error_msg = f"Set the {env_variable} environment variable"
        raise ImproperlyConfigured(error_msg)


def load_envfile(env_name):
    try:
        dotenv_path = f".env.{env_name}"
        dotenv_path = find_dotenv(filename=dotenv_path, raise_error_if_not_found=True)
        load_dotenv(dotenv_path=dotenv_path, verbose=True)
    except Exception:
        load_dotenv(verbose=True)


def get_list_of_non_empty_item(text):
    return [item.strip() for item in text.split(",") if len(item.strip()) > 0]


def get_list_from_env(name, default_value=""):
    return get_list_of_non_empty_item(os.getenv(name, default_value))


def get_bool_from_env(name, default_value=False):
    if name in os.environ:
        value = os.environ[name]
        try:
            return ast.literal_eval(value)
        except ValueError as e:
            raise ValueError(f"{value} is an invalid value for {name}") from e
    return default_value


def load_env_from_s3():
    file_name = ".env.s3"
    if not find_dotenv(filename=file_name):
        from core_utils import s3_manager

        s3 = s3_manager.S3Manager(settings.AWS_STORAGE_BUCKET_NAME)
        s3.download_file(settings.S3_ENV_FILE_LOCATION, file_name)
    load_dotenv(dotenv_path=file_name)


def lookup_env(names, default_value=None):
    """Look up for names in environment. Returns the first element found."""
    for name in names:
        if value := os.getenv(name):
            return value
    return default_value
