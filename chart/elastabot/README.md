
# Helm Chart for Kubernetes

An Elastabot chart is available in the Codesim LLC Helm repository, and can be installed into an existing Kubernetes cluster by following the instructions below.

## Installing the Chart

Add the Codesim repository to your Helm configuration:

```console
helm repo add jertel https://helm.jertel.com
```

Next, install the chart with a release name, such as elastabot:

```console
helm install elastabot jertel/elastabot
```

The command deploys Elastabot on the Kubernetes cluster in the default configuration. The [configuration](#configuration) section lists the parameters that can be configured during installation. The [secrets](#secrets) section lists the required Kubernetes secrets.

## Uninstalling the Chart

To uninstall/delete the elastabot deployment:

```console
helm delete elastabot --purge
```

The command removes all the Kubernetes components associated with the chart and deletes the release.

## Configuration

| setting                        | description                                                                                                              | default
|--------------------------------|--------------------------------------------------------------------------------------------------------------------------|--------
| image.repository               | Docker image repository                                                                                                  | `jertel/elastabot`
| image.tag                      | Tag, typically the version, of the Docker image                                                                          | `1.5.3
| image.pullPolicy               | Kubernetes image pull policy                                                                                             | `IfNotPresent`
| commandPrefix                  | Special character or phrase to trigger the bot, typically an exclamation point, !. Ex: !ack                              | `!`
| elasticsearch.host             | Hostname for the Elasticsearch server                                                                                    |
| elasticsearch.port             | Port for the Elasticsearch server                                                                                        | `9200`
| elasticsearch.sslEnabled       | If true, uses SSL/TLS to connect to Elasticsearch                                                                        | `false`
| elasticsearch.sslStrictEnabled | If true, the SSL/TLS certificates will be validated against known certificate authorities                                | `false`
| elasticsearch.timeoutSeconds   | Number of seconds to wait for an Elasticsearch response                                                                  | `10`
| elasticsearch.urlPrefix        | URL prefix for Elasticsearch, typically an empty string                                                                  |
| elastalert.index               | The index prefix used by Elastalert within Elasticsearch, typically elastalert                                           | `elastalert`
| elastalert.silenceMinutes      | Number of minutes to silence an acknowledge alert if a silence duration is not explicitly given with the ack command.    | `240`
| elastalert.recentMinutes       | Number of minutes to look back through Elasticsearch indices for a matching triggered alert                              | `4320`
| smtp.host                      | Hostname for the SMTP server                                                                                             |
| smtp.port                      | Port for the SMTP server                                                                                                 | `25`
| smtp.secure                    | If true, will connect to the SMTP host over SSL/TLS                                                                      | `false`
| smtp.starttls                  | If true, will send the starttls command (typically not used with smtp.secure=true)                                       | `false`
| smtp.timeoutSeconds            | Number of seconds to wait for the SMTP server to respond                                                                 | `10`
| smtp.to                        | Email address that will receive the triage email                                                                         |
| smtp.from                      | Sender email address                                                                                                     |
| smtp.subjectPrefix             | If non-empty string, will be prepended to each email subject. Ex: `[prod] `, `[test] `, etc                              | 
| smtp.debug                     | If true, the SMTP connectivity details will be logged to stdout                                                          | `false`
| triageTarget                   | How to initiate the triage process, currently only smtp is supported.                                                    | `smtp`
| searchEnabled                  | Allow all Slack users to search the Elasticsearch cluster for any data. Disable in public communities with sensitive data| `true`
| debug                          | If true, will output debug logging to help troubleshoot connectivity problems.                                           | `false`

## Secrets

| variable               | required | description
|------------------------|----------|------------
| slackBotToken          | true     | The Slack-generated bot token, provided by slack.com
| elasticsearchUsername  | true     | Elasticsearch username, provided by your ES admin
| elasticsearchPassword  | true     | Elasticsearch password, provided by your ES admin
| smtpUsername           | false    | Optional SMTP username, provided by your SMTP admin (used with SMTP triage target)
| smtpPassword           | false    | Optional SMTP password, provided by your SMTP admin (used with SMTP triage target)

Below is a sample secrets.yaml file that can be used as a template. Remember that all secrets must be base64-encoded. You can do this via a Linux terminal as follows:

```bash
echo -n "xoxb-xxxx-yyyy-zzzzzz" | base64
```

Note the `-n` is critical when created secrets with this technique, to avoid linefeeds getting mixed in with the secrets.

IMPORTANT - Please see the note in the Elastabot main [README.md](../../README.md) where it explains how to create a classic bot in order to use this Elastabot. Skipping over this information will prevent Elastabot from connecting to your Slack community.

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: elastabot-secrets
type: Opaque
data:
  slackBotToken: ""
  elasticsearchUsername: ""
  elasticsearchPassword: ""
  smtpUsername: ""
  smtpPassword: ""
```

Once you have provided the base64-encoded secret values, apply the file to your Kubernetes cluster as follows:

```console
kubectl apply -f secrets.yaml
```
