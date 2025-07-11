#!/usr/bin/env python3

import requests
import os
import sys
import time
import socket
from datetime import datetime

def log(message):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{current_time}] {message}")

def get_public_ip():
    response = requests.get("https://ip.tiippex.de")
    if response.status_code == 200:
        public_ip = response.text.strip()

        log(f"Successfully got public IP: {public_ip}")
        return public_ip
    else:
        raise Exception("Could not get public IP")

def get_access_policy(api_key, account_id, policy_id):
    url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/access/policies/{policy_id}"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()['result']
    else:
        raise Exception(f"Failed to fetch Access Policy. Response: {response.text}")

def resolve_dns_to_ip(dns_record):
    try:
        return socket.gethostbyname(dns_record)
    except socket.gaierror as e:
        raise Exception(f"Failed to resolve DNS: {dns_record} - {e}")

def update_cloudflare_access_policy(api_key, account_id, policy_id, ip_range, ip_lookup_enabled, dns_list):
    url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/access/policies/{policy_id}"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    if ip_lookup_enabled:
        public_ip = get_public_ip()
        if not ip_range:
            ip_range = []
        ip_range.append(public_ip)

    if dns_list:
        for dns_record in dns_list:
            try:
                resolved_ip = resolve_dns_to_ip(dns_record)
                ip_range.append(resolved_ip)
                log(f"Resolved {dns_record} to {resolved_ip}")
            except Exception as e:
                log(f"Error resolving DNS {dns_record}: {e}")

    policy_data  = get_access_policy(api_key, account_id, policy_id)
    ip_includes = [{"ip": {"ip": ip}} for ip in ip_range]

    policy_data['include'] = ip_includes

    log(f"Trying to update {account_id}'s Access Policy with IPs: {', '.join(ip_range)}")

    response = requests.put(url, json=policy_data, headers=headers)

    if response.status_code == 200:
        log(f"Successfully updated Access Policy with IPs: {', '.join(ip_range)}")
    else:
        log(f"Failed to update Access Policy. Response: {response.text}")

if __name__ == "__main__":
    CLOUDFLARE_API_KEY = os.getenv("CLOUDFLARE_API_KEY")
    CLOUDFLARE_ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID")
    CLOUDFLARE_POLICY_ID = os.getenv("CLOUDFLARE_POLICY_ID")

    IP_RANGE = os.getenv("IP_RANGE", "").split(",") if os.getenv("IP_RANGE") else []
    IP_FROM_DNS = os.getenv("IP_FROM_DNS", "").split(",") if os.getenv("IP_FROM_DNS") else []
    IP_LOOKUP_ENABLED = os.getenv("IP_LOOKUP_ENABLED", "true").lower() == "true"

    UPDATE_INTERVAL_MINUTES = os.getenv("UPDATE_INTERVAL_MINUTES")

    if not CLOUDFLARE_API_KEY or not CLOUDFLARE_ACCOUNT_ID or not CLOUDFLARE_POLICY_ID:
        log("Required environment variables: CLOUDFLARE_API_KEY, CLOUDFLARE_ACCOUNT_ID, CLOUDFLARE_POLICY_ID")
        sys.exit(1)

    try:
        if not UPDATE_INTERVAL_MINUTES:
            log("No UPDATE_INTERVAL_MINUTES set, running once...")
            update_cloudflare_access_policy(CLOUDFLARE_API_KEY, CLOUDFLARE_ACCOUNT_ID, CLOUDFLARE_POLICY_ID, IP_RANGE, IP_LOOKUP_ENABLED, IP_FROM_DNS)
            log("Execution complete. Exiting.")
            sys.exit(0)

        else:
            UPDATE_INTERVAL_MINUTES = int(UPDATE_INTERVAL_MINUTES)
            while True:
                try:
                    update_cloudflare_access_policy(CLOUDFLARE_API_KEY, CLOUDFLARE_ACCOUNT_ID, CLOUDFLARE_POLICY_ID, IP_RANGE, IP_LOOKUP_ENABLED, IP_FROM_DNS)
                except Exception as e:
                    log(f"Error updating Cloudflare: {e}")

                time.sleep(UPDATE_INTERVAL_MINUTES * 60)

    except KeyboardInterrupt:
        log("\nGracefully shutting down. Exiting...")
        sys.exit(0)
