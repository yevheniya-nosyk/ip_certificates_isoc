from concurrent.futures import ThreadPoolExecutor, as_completed
from cryptography.hazmat.backends import default_backend
from cryptography.x509.oid import ExtensionOID
from cryptography import x509
import argparse
import datetime
import socket
import json
import ssl

def get_cert(ip,port):
    """Connect to IP:port and get the certificate"""
    
    # SSL setup
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    try:
        with socket.create_connection((ip, port), timeout=2) as sock:
            with context.wrap_socket(sock, server_hostname=ip) as ssl_sock:
                der_cert = ssl_sock.getpeercert(binary_form=True)
                if der_cert:
                    # Load the certificate
                    cert = x509.load_der_x509_certificate(der_cert, default_backend())
                    # SAN extension does not necessarily exist
                    try:
                        san = [str(i.value) for i in cert.extensions.get_extension_for_oid(ExtensionOID.SUBJECT_ALTERNATIVE_NAME).value]
                    except:
                        san = list()
                    
                    # Construct the response object
                    return {
                        "ip": ip, 
                        "port": port, 
                        "success": True, 
                        "subject": cert.subject.rfc4514_string(),
                        "issuer": cert.issuer.rfc4514_string(),
                        "serial": format(cert.serial_number, 'X'),
                        "not_valid_before": cert.not_valid_before_utc.isoformat(),
                        "not_valid_after": cert.not_valid_after_utc.isoformat(),
                        "san": san
                    }

    except Exception as e:
        return {"ip": ip, "port": port, "success": False, "error": str(e)}
    
def get_targets(filename):
    """Get scan targets"""

    results = set()
    with open(filename, "r") as f:
        for line in f:
            # Load the certificate
            certificate = json.loads(line)
            # Get relevant dates
            not_before = datetime.datetime.fromtimestamp(certificate["not_before"],tz=datetime.timezone.utc)
            not_after = datetime.datetime.fromtimestamp(certificate["not_after"],tz=datetime.timezone.utc)
            now = datetime.datetime.now(datetime.timezone.utc)
            # Check if valid now and at least 24 hours more in future
            if not_before < now and not_after > now + datetime.timedelta(hours=24):
                san_ips = [i[3:] for i in certificate["extensions"]["subjectAltName"].split(", ") if i.startswith("IP:")]
                for ip in san_ips:
                    results.add(ip)

    return results

if __name__ == "__main__":
    
    # Parse command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-w', '--work_dir', required=True, default=None, help="Path to the work directory")
    parser.add_argument('-c', '--certstream_file', required=True, default=None, help="Name of the certstream file")
    args = parser.parse_args()

    # Target ports
    ports = {
        21, 25, 110, 143, 443, 465, 
        587, 636, 853, 990, 993, 995, 
        1433, 2376, 3306, 3389, 5432, 
        5671, 6443, 7547, 8443, 8883, 
        9200, 27017
    }

    # Read the certstream file to get targets
    ip_targets = get_targets(filename=args.certstream_file)

    # Create IP/port pairs
    ip_port = [(ip,port) for ip in ip_targets for port in ports]

    with ThreadPoolExecutor(max_workers=30) as executor:
        for i in range(0, len(ip_port), 50_000):
            batch = ip_port[i:i + 50_000]
            # Submit a manageable number of tasks
            futures = [executor.submit(get_cert, ip=ip, port=port) for ip,port in batch]
            # Process results as they complete
            for future in as_completed(futures):
                print(json.dumps(future.result()))
