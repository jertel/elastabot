import os
import time
import datetime
import re
import logging
import os
import signal
import sys
import argparse
import json
import elastalerthelp
import elastichelp
import triage
import slack

class Elastabot():
  def __init__(self):
    self.running = False
    self.conf = {}
    self.log = logging.getLogger('elastabot')
  
  # Initializes the bot via a config file and env variables, invoked once
  def init(self):
    configured = True
    parser = argparse.ArgumentParser()
    parser.add_argument('--configFile', help='JSON configuration file', default="elastabot.json")
    args = parser.parse_args()
    
    with open(args.configFile, "r") as fp:
      self.conf = json.load(fp)

    self.slackBotToken = os.environ.get('SLACK_BOT_TOKEN')
    if not self.slackBotToken:
      self.log.error("SLACK_BOT_TOKEN is a required environment variable")
      configured = False
    else:
      self.slackBotToken = self.slackBotToken.strip()

    if self.conf['debug'] == True:
      logging.basicConfig(level=logging.DEBUG)
    else:
      logging.basicConfig(level=logging.INFO)

    return configured

  # Main loop for the bot, connects to slack and watches for incoming commands
  def run(self):
    if self.init():
      self.log.info("Slack bot connecting to server")
      self.slack_client = slack.RTMClient(token=self.slackBotToken)
      self.slack_client.on(event='message', callback=handle_message)
      self.slack_client.start()

  # Parses incoming message for a valid command
  def parse_bot_command(self, event):
    command, args = self.parse_command(event["text"])
    return command, args, event["channel"], event["user"]

  # Splits the command and arguments apart
  def parse_command(self, message_text):
    pattern =  "^%s([a-z_]+)(.*)" % (self.conf['commandPrefix'])
    matches = re.search(pattern, message_text)
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

  # Command distributor
  def handle_command(self, client, command, args, channel, user):
    default_response = "Unrecognized command; Try !help"
    response = None
    if command == "search":
      response = elastichelp.search(self.conf, args)
    elif command == "health":
      response = elastichelp.health(self.conf, args)
    elif command == "ack":
      response = elastalerthelp.ack(self.conf, args)
    elif command == "triage":
      response = triage.triage(self.conf, args)
    elif command == "help":
      response = self.help()

    msg = response.strip().replace("${prefix}", self.conf['commandPrefix'])
    client.chat_postMessage(
        as_user=True,
        channel=channel,
        text=msg or default_response
    )

  def help(self):
    return """Supported commands:```
${prefix}search   - Perform Elasticsearch search
${prefix}health   - Show Elasticsearch health
${prefix}ack      - Silence an alert with optional triage
${prefix}triage   - Triage an arbitrary issue
${prefix}help     - This help message

Specify `${prefix}command help` for more information about a specific command. Ex: `${prefix}ack help`
```"""

def handle_message(**payload):
  data = payload['data']
  if "text" in data:
    command, args, channel, user = bot.parse_bot_command(data)
    if command:
      bot.handle_command(payload['web_client'], command, args, channel, user)


def handle_signal(signal, frame):
  os._exit(0)

def main():
  global bot
  signal.signal(signal.SIGINT, handle_signal)
  bot = Elastabot()
  bot.run()

if __name__ == '__main__':
  sys.exit(main())
