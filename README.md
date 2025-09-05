# Terraform Cloud Resources

## Setup

1. Install Python 3.x and the `requests` library:
   ```sh
   pip install requests
   ```
2. Set the required environment variables:
   - `TFC_TOKEN`: Your Terraform Cloud API token
   - `TFC_ORG`: Your Terraform Cloud organization name
   - `PORT_WEBHOOK_URL`: (Optional) Webhook URL for sending data to Port

   Example (Linux/macOS):
   ```sh
   export TFC_TOKEN="your-tfc-token"
   export TFC_ORG="your-org-name"
   export PORT_WEBHOOK_URL="https://your-port-webhook-url"
   ```

## How to run

Run the script from the command line:
```sh
python tfc.py
```

The script will:
- List all workspaces in your Terraform Cloud organization
- For each workspace, fetch the latest state version
- Download and parse the state file
- (If configured) Send resource data to the Port webhook

## Setting up the Port Webhook Receiver

1. **Upload the Blueprint**
   - In your Port admin console, go to the Blueprints section.
   - Copy the contents of the `terraform_cloud_resource.json` file to a new blueprint
   - You can also use the Port API:
     ```sh
     curl -X POST \
       https://api.getport.io/v1/blueprints \
       -H "Authorization: Bearer <YOUR_PORT_TOKEN>" \
       -H "Content-Type: application/json" \
       -d @blueprints/terraform_cloud_resource.json
     ```

2. **Configure the Webhook Receiver**
   - In Port, create a webhook receiver for your organization.
   - Set the authentication type to **Plain Auth**.
   - Copy the webhook URL and set it as the `PORT_WEBHOOK_URL` environment variable in your script environment.

   Example:
   ```sh
   export PORT_WEBHOOK_URL="https://api.getport.io/v1/webhook/<your-receiver-id>"
   ```

3. **Run the Script**
   - The script will send resource data to the Port webhook using the configured URL and authentication.

For more details, see the [Port documentation on webhook receivers](https://docs.port.io/docs/webhook-receivers).