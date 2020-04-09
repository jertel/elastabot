import logging
import datetime
import elastichelp
import timehelp
import triage

log = logging.getLogger('elastalert')

# Attempts to find a recently triggered alert
def findNewestAlert(es, index, recentMinutes, name):
  alert = None
  details = None
  res = es.search(index=index, size=1, sort='alert_time:desc', q='alert_time:[now-' + str(recentMinutes) + 'm TO now] AND !rule_name:Deadman* AND rule_name:' + name , _source_includes=['rule_name', 'match_body'])
  if res['hits']['hits']:
    alert = res['hits']['hits'][0]['_source']['rule_name']
    details = res['hits']['hits'][0]['_source']['match_body']
  return alert, details

# Attempts to find a recently triggered alert
def isAlertFiring(es, index, recentMinutes, alert):
  results = es.count(index=index, q='alert_time:[now-' + str(recentMinutes) + 'm TO now] AND rule_name:%s'+alert)
  return results['count'] > 0

# Acknowledges an Elastalert rule
def ack(conf, args):
  recentMinutes = conf['elastalert']['recentMinutes']
  defaultDurationMinutes = conf['elastalert']['silenceMinutes']
  if args == "help" or args == "-help":
    return """Acknowledge a recently fired alert. The alert will be silenced, and optionally triaged.```
Usage: ${prefix}ack [alert] [|<duration>] [?]
Options:
  alert     - Case-sensitive name of an alert rule, can contain spaces. Must have recently* fired. (optional)
  duration  - Number of minutes to silence the alert, defaults to %d minutes (optional)
  ?         - Initiates the triage process

If alert is not specified then the most recent* triggered alert will be used.

*Recent time is currently set to %s minutes.

The following examples will acknowledge the alert rule "Acme Flatline Alert":
  ${prefix}ack Acme Flatline Alert    will silence for the default duration
  ${prefix}ack Acme?                  will silence for the default duration
  ${prefix}ack Acme|10                will silence for 10 minutes
  ${prefix}ack Acme|10m               will silence for 10 minutes
  ${prefix}ack Acme |2d               will silence for 2 days
  ${prefix}ack Acme |2d ?             will silence for 2 days and triage

The following examples will acknowledge the most recent triggered alert:
  ${prefix}ack                        will silence for the default duration
  ${prefix}ack ?                      will silence for the default duration
  ${prefix}ack |20                    will silence for 20 minutes
  ${prefix}ack |4h                    will silence for 4 hours
  ${prefix}ack |2w ?                  will silence for 2 weeks and triage
```""" % (defaultDurationMinutes, recentMinutes)

  es = elastichelp.createElasticsearchClient(conf)

  triageTarget = None
  if args.find("?") >= 0:
    triageTarget = conf['triageTarget']
    args = args.replace("?","")

  name = ''
  durationMin = None
  if args:
    splitArgs = args.split("|", 1)
    name = splitArgs[0].replace(" ", "\\ ").strip()
    if len(splitArgs) > 1:
      durationMin = splitArgs[1].strip()

  index = conf['elastalert']['index']
  name = name + "*"
  name, details = findNewestAlert(es, index, recentMinutes, name)
  if not name:
    return "No matching, recent alerts have fired"
  
  timenow = timehelp.now()
  duration = timehelp.convertToMinutes(durationMin, defaultDurationMinutes)
  until = timenow + datetime.timedelta(seconds=(duration * 60))
  response = None
  body = {'exponent': 0,
          'rule_name': name + "._silence",
          '@timestamp': timenow,
          'until': until}
  try:
    es.index(index=conf["elastalert"]["index"] + "_silence", doc_type='silence', body=body)
    response = "Acknowledged alert *" + name + "* until " + str(until) + " UTC"
    if triageTarget:
      response = response + "\n" + triage.begin(conf, triageTarget, name, details)
  except Exception as e:
    log.exception("Error writing alert info to Elasticsearch: %s" % (e))
    response = "Failed to acknowledge alert: %s" % (e)
  return response

