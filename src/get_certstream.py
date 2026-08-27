import certstream
import ipaddress
import argparse
import json

def print_callback(message, context):

    if message["message_type"] == "certificate_update":
        certificate = message["data"]["leaf_cert"]
        # Filter out pre-certificates
        if "ctlPoisonByte" not in certificate["extensions"]:
            # Get those with IPs in SAN
            san = certificate["extensions"]["subjectAltName"].split(", ")
            san_ips = [i[3:] for i in san if i.startswith("IP:")]
            if san_ips:
                for ip in san_ips:
                    try:
                        # Only keep valid IP addresses
                        ip_address = str(ipaddress.ip_address(ip))
                        print(f"{json.dumps(certificate)}", flush=True)
                    except:
                        pass


if __name__ == "__main__":
    
    # Parse command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-w', '--work_dir', required=True, default=None, help="Path to the work directory")
    parser.add_argument('-c', '--certstream', required=True, default=None, help="Certstream feed")
    args = parser.parse_args()

    # Query the certstream
    certstream.listen_for_events(print_callback, url=args.certstream)
