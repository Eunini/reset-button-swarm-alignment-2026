# Direct Adaption API connection — preexisting preparation, November 5

The user requested a route without a plugin. `scripts/adaption_connection.py` provides temporary key intake and read-only API access. It holds the key in process memory only. It never writes the key to disk, echoes it, or prints upstream error bodies. Restarting or expiring the process loses the key; closing the browser alone does not.

The shared preview tool was unavailable in this headless client. A temporary Cloudflare tunnel was therefore configured with `--allowed-mail` restricted to the participant's registration email, which the participant can access. Unauthenticated requests to the form, status and read endpoints were checked and redirected to Cloudflare's verification service. Do not expose this service without that access restriction. The relay is a third-party HTTPS service; do not describe it as a local-only browser connection or end-to-end encryption that excludes the relay.

User steps: sign into the funded Adaption account, create a named API key under Settings → API keys, open the email-protected form, complete email verification, and enter the API key in its masked field. No key should be pasted into the chat. Initial verification calls only GET /api/v1/models and does not launch inference or training. It verifies key access; it does not independently establish the account's email, balance or Premium status.

Only a closed list of read-only operations is implemented. No automatic model inference, training or dataset generation is supported. The user-authorized credit budget and actual prices must be resolved before adding any paid operation. Read results still need to be checked for inference entitlements.

Start the local process with `python3 scripts/adaption_connection.py --ttl-minutes 60`, then expose its loopback port through the email-restricted tunnel. Keep tunnel logs outside the repository, with owner-only file permissions. Stop the tunnel after setup or when the local process expires. Do not copy credentials, browser cookies, or verification codes into source control or reports.

`python3 scripts/check_adaption_connection.py` reads connection status and displays public model identifiers without reading the key into the assistant context. `tests/test_adaption_connection.py` mocks all upstream calls while checking request forgery rejection, disabled paid operations, expiry, and absence of credentials in replies.

Sources: [Adaption API key setup](https://docs.adaptionlabs.ai/autoscientist-quickstart/), [Adaption responses](https://docs.adaptionlabs.ai/api/resources/responses/methods/create), [Cloudflare email-restricted temporary tunnels](https://developers.cloudflare.com/tunnel/get-started/quick-tunnels/).

All of these connection helpers were written before the sprint. They are not main research results and are additional to the original preexisting manifest.
