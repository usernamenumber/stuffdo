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
	date_and_people_by_event = {}

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
			
		date_and_people_by_event[event] = []
		for date in bestdates:
			date_and_people_by_event[event].append((date, peoplebydate[date]))

	return date_and_people_by_event
		
def print_options(date_and_people_by_event, include_emails=True):
	print "==="
	for event, options in date_and_people_by_event.items():
		print "\n\nTop options for {}:".format(event)
		for date, people in options:
			line = "  {} with {}".format(date, len(people))
			if include_emails:
				line += ' ' + '; '.join(people)
			print line

def print_people_notes(data):
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
	argparser.add_argument("fn")
	args = argparser.parse_args()

	data = data_from_file(args.fn)
	overrides = file(args.overrides).read() if args.overrides else {}
	options = all_viable_options(data)
	print_options(options, include_emails=False)
	print_people_notes(data)