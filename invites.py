#!/usr/bin/python
from argparse import ArgumentParser
import json
import re
import shlex
from collections import defaultdict

DEFAULT_MIN_ATTENDANCE = 5

def all_viable_options(data, overrides={}):
	"""
	goal: figure out which combinations of people+date+event would have the best attendance.
		
	for any "event" with interest above a threshold, show the date that works for the most people, then re-check the threshold and remove if not met.

	- group people by interest in event
	- remove events with total interest below threshold
	- for each remaining event:
		- collect people interested in event, grouped by date
		- remove event if max(group_lens) < thresh
	"""
	dates_by_person = defaultdict(lambda: [])
	notes_by_person = defaultdict(lambda: [])
	people_by_event = defaultdict(lambda: [])
	date_and_people_by_event = defaultdict(lambda: [])
	event_and_people_by_date = defaultdict(lambda: [])

	# Minimum attendance for an option to be considered,
	# keyed by event.
	thresholds = defaultdict(lambda: DEFAULT_MIN_ATTENDANCE)
	thresholds.update(overrides.get('thresholds', {}))

	# People who must be available for a date to be considered,
	# keyed by event.
	required_attendees = defaultdict(lambda: [])
	required_attendees.update(overrides.get('required_attendees', {}))

	for person, response in data.items():
		dates_by_person[person] = response.get('dates', ())
		notes_by_person[person] = response.get('notes', '')
		for event in response.get('events', ()):
			people_by_event[event].append(person)
			
	for event, people in people_by_event.items():
		if len(people) < thresholds[event]:
			print "removing {} because only {} interest (min {})".format(event, len(people), thresholds[event])
			del(people_by_event[event])
			continue
		
		peoplebydate = defaultdict(lambda: [])
		for person, dates in dates_by_person.items():
			# faster than nested loop iterating through
			# `people` for keys to get from datesby?
			if person not in people:
				continue
			for date in dates:
				peoplebydate[date].append(person)
				
		for date, people in peoplebydate.items():
			num_required = len(required_attendees[event])
			num_required_available = len(set(people).intersection(required_attendees[event]))
			if num_required != num_required_available:
				print "removing {} for {} because only {}/{} required attendees are available".format(date, event, num_required_available, num_required)
				del(peoplebydate[date])
				continue
		
			if len(people) < thresholds[event]:
				print "removing {} for {} because only {} interest (min {})".format(event, date, len(people), thresholds[event])
				del(peoplebydate[date])
				continue
				
		if len(peoplebydate) == 0:
			print "no dates where more than {} can do {}. Sadness.".format(thresholds[event], event)
			continue
			
		bestdates = sorted(peoplebydate, 
			lambda a,b: cmp(len(peoplebydate[b]),len(peoplebydate[a])))
			
		for date in bestdates:
			date_and_people_by_event[event].append((date, peoplebydate[date]))
			event_and_people_by_date[date].append((event, peoplebydate[date]))

	return (date_and_people_by_event, event_and_people_by_date)

def print_options(data_fn, overrides_fn=None, skip_notes=False, skip_emails=False):
	data = data_from_file(data_fn)
	overrides = file(overrides_fn).read() if overrides_fn else {}
	date_and_people_by_event, event_and_people_by_date = all_viable_options(data)

	print "==="
	for date, options in event_and_people_by_date.items():
		print "\n\nTop options for {}:".format(date)
		# Sort events by number of attendees
		for event, people in sorted(options, lambda a,b: cmp(len(b[1]), len(a[1]))):
			line = "  {} people for {}\t({} alternatives)".format(len(people), event, len(date_and_people_by_event[event]))
			if not skip_emails:
				line += ' ' + '; '.join(people)
			print line

		if not skip_notes:
			print "\n===\n"
			for person, response in data.items():
				notes = response.get('notes', '')
				if notes:
					print "Notes for {}:\n  {}\n".format(person, "\n  ".join(notes.split("\n")))

def data_from_file(fn, delim='\t'):
	data = {}
	rows = [ line.split('\t') for line in file(fn).readlines()[1:] if not re.match(r'^\s*$', line) ]
	for row in rows:
		(submitted, dates, events, notes, person) = [ item.strip() for item in row ]
		data[person] = {
			'dates':  [ date.strip() for date in dates.split(',') ],
			'events': [ event.strip() for event in events.split(',') ],
			'notes':  notes
		}
	return data


if __name__ == '__main__':
	argparser = ArgumentParser()
	argparser.add_argument("--overrides", default=None)
	argparser.add_argument("--no-emails", action='store_true')
	argparser.add_argument("--no-notes",  action='store_true')
	argparser.add_argument("fn")
	args = argparser.parse_args()

	print_options(args.fn, args.overrides, args.no_emails, args.no_notes)