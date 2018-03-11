# Elastabot Helm Chart

[elastabot](https://github.com/jertel/elastabot) a Slack bot for interacting with Elastalert.

## Installing the Chart

To install the chart with the release name `my-release`:

```console
$ helm install --name my-release stable/elastabot
```

The command deploys Elastabot on the Kubernetes cluster in the default configuration. The [configuration](#configuration) section lists the parameters that can be configured during installation. The [secrets](#secrets) section lists the required Kubernetes secrets.

## Uninstalling the Chart

To uninstall/delete the my-release deployment:

```console
$ helm delete my-release
```

The command removes all the Kubernetes components associated with the chart and deletes the release.

## Configuration

| setting                        | description                                                                                                           | default
|--------------------------------|-----------------------------------------------------------------------------------------------------------------------|----------
| image.repository               | Docker image repository                                                                                               | jertel/elastabot
| image.tag                      | Tag, typically the version, of the Docker image                                                                       | 1.0.0
| image.pullPolicy               | Kubernetes image pull policy                                                                                          | IfNotPresent
| elasticsearch.host             | Hostname for the Elasticsearch server                                                                                 |
| elasticsearch.port             | Port for the Elasticsearch server                                                                                     | 9200
| elasticsearch.sslEnabled       | If true, uses SSL/TLS to connect to Elasticsearch                                                                     | False
| elasticsearch.sslStrictEnabled | If true, the SSL/TLS certificates will be validated against known certificate authorities                             | False
| elasticsearch.timeoutSeconds   | Number of seconds to wait for an Elasticsearch response                                                               | 10
| elasticsearch.urlPrefix        | URL prefix for Elasticsearch, typically an empty string                                                               |
| elastalert.index               | The index prefix used by Elastalert within Elasticsearch, typically elastalert or elastalert_status                   | elastalert_status
| elastalert.silenceMinutes      | Number of minutes to silence an acknowledge alert if a silence duration is not explicitly given with the ack command  | 240
| elastalert.recentMinutes       | Number of minutes to look back in history for a fired alert in the Elasticsearch index                                | 4320
| smtp.host                      | Hostname for the SMTP server                                                                                          |
| smtp.port                      | Port for the SMTP server                                                                                              | 25
| smtp.secure                    | If true, will connect to the SMTP host over SSL/TLS                                                                   | False
| smtp.starttls                  | If true, will send the starttls command (typically not used with smtp.secure=true                                     | False
| smtp.timeoutSeconds            | Number of seconds to wait for the SMTP server to respond                                                              | 4
| smtp.to                        | Email address that will receive the triage email                                                                      |
| smtp.from                      | Sender email address                                                                                                  |
| smtp.subjectPrefix             | If non-empty string, will be prepended to each email subject                                                          |
| smtp.debug                     | If true, the SMTP connectivity details will be logged to stdout                                                       | False
| commandPrefix                  | Special character or phrase to trigger the bot, typically an exclamation point, !. Ex: !ack                           | !
| triageTarget                   | How to initiate the triage process, currently only smtp is supported.                                                 | smtp

## Secrets

The following environment variable secrets are required to be present in order for this chart to deploy:

| variable               | required | description 
|------------------------|----------|------------
| SLACK_BOT_TOKEN        | true  | The Slack-generated bot token, provided by slack.com
| ELASTICSEARCH_USERNAME | false | Optional Elasticsearch username, provided by your ES admin
| ELASTICSEARCH_PASSWORD | false | Optional Elasticsearch password, provided by your ES admin
| SMTP_USERNAME          | false | Optioanl SMTP username, provided by your SMTP admin
| SMTP_PASSWORD          | false | Optioanl SMTP password, provided by your SMTP admin

Below is a sample secrets.yaml file that can be used as a template. Remember that all secrets must be base64-encoded. Even if the token provided by Slack already appears to be base64-encoded you must encode it again.

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: elastabot-secrets
type: Opaque
data:
  slackBotToken: "BASE64-ENCODED-SLACK-TOKEN"
  smtpUsername: ""
  smtpPassword: ""
  elasticsearchUsername: ""
  elasticsearchPassword: ""
```

Once you have provided the SLACK_BOT_TOKEN base64-encoded value, apply the file to your Kubernetes cluster as follows:

```console
kubectl apply -f secrets.yaml
```