from cryptography.fernet import Fernet
from django.conf import settings
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode


def encode_str(string):
    return force_str(urlsafe_base64_encode(force_bytes(string)))


def decode_str(string):
    return force_str(urlsafe_base64_decode(string))


def get_encrypted_secret(secret, key=settings.ENCRYPTION_KEY):
    return Fernet(key).encrypt(bytes(secret, "utf-8")).decode("utf-8")


def get_decrypted_data(secret, key=settings.ENCRYPTION_KEY):
    if secret is None:
        return secret

    return Fernet(key).decrypt(bytes(secret, "utf-8")).decode("utf-8")


def get_sorted_key_dict(d):
    return {key: d[key] for key in sorted(d.keys())}


def get_or_default(obj, key, default_value=""):
    return obj.get(key) or default_value


def value_or_default(val, default_value=""):
    return val or default_value
