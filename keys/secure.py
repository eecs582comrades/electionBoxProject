
import uuid
import json
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization


def generate_uuid():
    return str(uuid.uuid4())


def generate_ecc_keypair():
    private_key = ec.generate_private_key(ec.SECP256R1())
    public_key = private_key.public_key()

    private_pem = private_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ).decode()

    public_pem = public_key.public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode()

    return private_pem, public_pem


def save_package(uuid_value, private_key, public_key, filename="master_package.json"):
    package = {
        "uuid": uuid_value,
        "private_key": private_key,
        "public_key": public_key
    }

    with open(filename, "w") as f:
        json.dump(package, f, indent=4)
    
    print(f"Saved offline master package to: {filename}")


if __name__ == "__main__":
    uid = generate_uuid()
    priv, pub = generate_ecc_keypair()
    save_package(uid, priv, pub)
