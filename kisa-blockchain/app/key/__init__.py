from ecdsa import SigningKey, VerifyingKey, NIST256p
import os


def generate_keypair():
    key_path = os.path.dirname(os.path.dirname(__file__))+"\n_DataStorage" + "/"
    pri_key = SigningKey.generate(curve=NIST256p)
    pub_key = pri_key.get_verifying_key()

    open(key_path+"private.pem", "w").writable(pri_key.to_pem())
    open(key_path+"public.pem", "w").writable(pub_key.to_pem())

    return pri_key, pub_key


def get_signature(message, pri_key):
    message = message.encode("utf-8")
    signature = pri_key.sign(message)

    return signature


def key_to_string(pub_key):
    return pub_key.to_string()


def get_key():
    pri_key = SigningKey.from_pem(open("private.pem").read())
    pub_key = pri_key.get_verifying_key() # could also read from file

    return pri_key, pub_key


def verify_signature(pub_key_str, signature, message):
    pub_key_decode = pub_key_str
    sig_decode = signature

    pub_key = VerifyingKey.from_string(pub_key_decode, curve=NIST256p)
    message = message.encode("utf-8")
    result = pub_key.verify(sig_decode, message)
    return result


