# Cloudflare Zero Trust Access Policy IP Updater

This Docker container fetches the public IP address of the host it is running on and updates a Cloudflare Zero Trust Access Policies by adding the current public IP to the Policy. It also accepts a comma-separated list of additional IPs to whitelist, and can resolve DNS records to IP addresses. The updates are made at a configurable interval.

## Features:
- Fetches the current public IP address from `https://ip.tiippex.de`.
- Adds the current public IP to Cloudflare Zero Trust's Access Polices.
- Accepts a list of IP addresses or DNS records to whitelist alongside the public IP.
- Runs at a user-defined interval (in minutes), or runs once and exits if no interval is specified.
- Optional IP lookup and DNS resolution for more flexibility.

## API Key Permissions:

- When creating the API token in Cloudflare, set the following permission for the token:
    - **Account** > **Access: Apps and Policies** > **Edit**.

## Environment Variables:

| Environment Variable          | Description                                                                              | Required  | Default   |
|-------------------------------|------------------------------------------------------------------------------------------|-----------|-----------|
| **`CLOUDFLARE_API_KEY`**      | Your Cloudflare API key.                                                                 | Yes       | None      |
| **`CLOUDFLARE_ACCOUNT_ID`**   | The Account ID from your Cloudflare dashboard.                                           | Yes       | None      |
| **`CLOUDFLARE_POLICY_ID`**    | The Access Policy ID from your Zero Trust dashboard.                                     | Yes       | None      |
| **`IP_RANGE`**                | A comma-separated list of IPs to whitelist                                               | No        | None      |
| **`IP_LOOKUP_ENABLED`**       | Set to `true` (default) or `false` to control whether the public IP lookup is performed. | No        | `true`    |
| **`IP_FROM_DNS`**             | A comma-separated list of DNS records to resolve to IPs and whitelist.                   | No        | None      |
| **`UPDATE_INTERVAL_MINUTES`** | Time in minutes between updates. If not set, the script will run once and then stop.     | No        | None      |

## Running the Docker Container:

To run the Docker container with necessary environment variables:

```bash
docker run -e TZ=Europe/Berlin \
           -e CLOUDFLARE_API_KEY=your_api_key \
           -e CLOUDFLARE_ACCOUNT_ID=your_account_id \
           -e CLOUDFLARE_POLICY_ID=your_policy_id \
           -e IP_RANGE="127.0.0.1,10.0.0.0/24" \
           -e IP_LOOKUP_ENABLED=true \
           -e IP_FROM_DNS="example.com,github.com" \
           -e UPDATE_INTERVAL_MINUTES=15 \
           tiippex/cloudflare-access-policy-ip-updater:latest
```

## Docker Compose Example:

Below is an example `docker-compose.yml` file that you can use to set up the container using Docker Compose:

```yaml
version: "3"
services:
  cloudflare-access-policy-updater:
    image: tiippex/cloudflare-access-policy-ip-updater:latest
    environment:
      - TZ=Europe/Berlin
      - CLOUDFLARE_API_KEY=your_api_key
      - CLOUDFLARE_ACCOUNT_ID=your_account_id
      - CLOUDFLARE_POLICY_ID=your_policy_id
      - IP_RANGE=127.0.0.1,10.0.0.0/24
      - IP_LOOKUP_ENABLED=true
      - IP_FROM_DNS=example.com,github.com
      - UPDATE_INTERVAL_MINUTES=15
    restart: always
```
