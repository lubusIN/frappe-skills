# Webhooks

## Overview
Webhooks are "user-defined HTTP callbacks" that trigger on specific document events. When a `doc_event` occurs, Frappe makes an HTTP request to a configured URI, allowing one site's events to invoke behavior on another.

## Creating a Webhook
1. Go to Integrations > Webhook > Webhook
2. Select the DocType for which the Webhook triggers (e.g., `Quotation`)
3. Select the Doc Event (e.g., `on_update`)
4. Optionally set additional document Conditions for specific scenarios
5. Enter a valid request URL to receive the Webhook data
6. Select the Request Method (POST is default)
7. Optionally add HTTP headers (e.g., API key)

Disable a webhook by unchecking the `Enabled` checkbox.

## Supported Doc Events
- on_insert
- on_update
- on_submit
- on_cancel
- on_trash
- on_update_after_submit
- on_change

## Data Structure
The webhook sends document data in JSON format.

## Webhook Security
- Use HTTPS for the request URL
- Add authentication headers (e.g., API keys, tokens)
- Use conditions to limit which documents trigger the webhook

## Webhook Request Log
Frappe logs all webhook requests for debugging and auditing.

## Example Use Cases
- Notify external services when a document is created or updated
- Sync data between Frappe and third-party systems
- Trigger external workflows on document submission

Sources: Webhooks (official docs)
