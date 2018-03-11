import smtphelp

def triage(conf, args):
  if args == "help" or args == "-help" or args.strip() == "":
    return """Triages an arbitrary issue.```
Usage: ${prefix}triage <arbitrary topic>
Options:
  arbitrary topic  - Topic that will begin the triage process

A triage process is defined by the Elastabot configuration, specifically the triage target.
Often it can be a simple email to some endpoint, such as a ticketing system, to begin the
triage workflow.

The following examples will begin the triage process for various topics:
  ${prefix}triage customers getting logged out after 1 minute of inactivity
  ${prefix}triage Problem discovered with auto-fetch results.
```"""
  return begin(conf, conf['triageTarget'], args, "")

def begin(conf, type, topic, details):
  if type == "smtp":
    return triageSmtp(conf, topic, details)
  else:
    return "Unsupported triage target: %s" % type

def triageSmtp(conf, topic, details):
  try:
    smtphelp.send(conf, topic, details)
    return "Triage process has started"
  except Exception as e:
    return "Failed to initiate triage process: %s" % (e)