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
from slackclient import SlackClient

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

    logging.basicConfig(level=logging.INFO)

    return configured

  # Main loop for the bot, connects to slack and watches for incoming commands
  def run(self):
    self.running = self.init()
    self.log.info("Slack bot connecting to server")
    self.slack_client = SlackClient(self.slackBotToken)
    if self.slack_client.rtm_connect(with_team_state=False):
      starterbot_id = self.slack_client.api_call("auth.test")["user_id"]
      self.log.info("Slack bot connected; botId=" + starterbot_id)
      while self.running:
        command, args, channel, user = self.parse_bot_commands(self.slack_client.rtm_read())
        if command:
          self.handle_command(self.slack_client, command, args, channel, user)
        time.sleep(1)
    else:
      self.log.error("Slack bot connection failed.")

  # Parses incoming message for a valid command
  def parse_bot_commands(self, slack_events):
    for event in slack_events:
      if event["type"] == "message" and not "subtype" in event:
        command, args = self.parse_command(event["text"])
        user = event["user"]
        return command, args, event["channel"], user
    return None, None, None, None

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
    client.api_call(
        "chat.postMessage",
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

def handle_signal(signal, frame):
  os._exit(0)

def main():
  signal.signal(signal.SIGINT, handle_signal)
  bot = Elastabot()
  bot.run()

if __name__ == '__main__':
  sys.exit(main())
