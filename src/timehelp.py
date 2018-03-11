import datetime
import logging

log = logging.getLogger('timehelp')

def now():
  return datetime.datetime.utcnow()

# Converts the given value into a number of minutes. Inputs can be a string of the following
# forms: 120, 120m, 2h, 2d, 1w
def convertToMinutes(str, defaultMins):
  mins = 0
  try:
    if not str:
      mins = defaultMins
    elif str.endswith('m'):
      mins = int(str[:-1])
    elif str.endswith('h'):
      mins = int(str[:-1]) * 60
    elif str.endswith('d'):
      mins = int(str[:-1]) * 1440
    elif str.endswith('h'):
      mins = int(str[:-1]) * 10080
    else:
      mins = int(str)
  except Exception as e:
    log.error("Unable to convert to minutes; str=%s; reason=%s" % (str, e))
    mins = int(defaultMins)
  return mins

