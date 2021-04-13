"""Checks and generates a new SSL certificate if necessary"""
from pathlib import Path
from socket import gethostname, gethostbyname
import datetime
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa

certificate_path: Path = (Path(__file__).resolve().parent / '..' / '..' / 'certificate.crt').resolve()
certificate_path_key: Path = (Path(__file__).resolve().parent / '..' / '..' / 'certificate.key').resolve()

class SSLGenerator:
    """Checks and generates a new SSL certificate if necessary"""

    def __init__(self):
        print('[Web API] Checking for SSL Certificate...')
        self.hostname = gethostname()
        self.ip_address = gethostbyname(self.hostname)

        if not certificate_path.is_file() or not certificate_path_key.is_file():
            print('[Web API] No certificate found, generating one')
            self.generate_certificate()

    def generate_certificate(self):
        key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        with open(certificate_path_key, "wb") as file:
            file.write(key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),
            ))
        subject = issuer = x509.Name([
            x509.NameAttribute(x509.oid.NameOID.COUNTRY_NAME, u"CH"),
            x509.NameAttribute(x509.oid.NameOID.STATE_OR_PROVINCE_NAME, u"ZH"),
            x509.NameAttribute(x509.oid.NameOID.LOCALITY_NAME, u"Zürich"),
            x509.NameAttribute(x509.oid.NameOID.ORGANIZATION_NAME, u"ZHAW"),
            x509.NameAttribute(x509.oid.NameOID.COMMON_NAME, self.hostname),
        ])
        cert = x509.CertificateBuilder().issuer_name(issuer
                                       ).subject_name(subject
                                       ).public_key(key.public_key()
                                       ).serial_number(x509.random_serial_number()
                                       ).not_valid_before(datetime.datetime.utcnow()
                                       ).not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=365 * 5)
                                       ).add_extension(
                                            x509.SubjectAlternativeName([
                                                x509.DNSName("localhost"),
                                                x509.DNSName("127.0.0.1"),
                                                x509.DNSName(self.ip_address)]),
                                            critical=False).sign(key, hashes.SHA256(), default_backend())
        with open(certificate_path, "wb") as file:
            file.write(cert.public_bytes(serialization.Encoding.PEM))