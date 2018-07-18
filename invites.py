from collections import defaultdict

def all_viable_options(data, overrides={}):
	"""
	goal: figure out which combinations of people+date+thing would have the best attendance.
		
	for any "thing" with interest above a threshold, show the date that works for the most people, then re-check the threshold and remove if not met.

	- group people by interest in thing
	- remove things with total interest below threshold
	- for each remaining thing:
		- collect people interested in thing, grouped by date
		- remove thing if max(group_lens) < thresh
	"""
	dates_by_person = defaultdict(lambda: set())
	people_by_thing = defaultdict(lambda: set())
	date_and_people_by_thing = {}

	# Minimum attendance for an option to be considered,
	# keyed by event.
	thresholds = defaultdict(lambda: 2)
	thresholds.update(overrides.get('thresholds', {}))

	# People who must be available for a date to be considered,
	# keyed by event.
	required_attendees = defaultdict(lambda: [])
	required_attendees.update(overrides.get('required_attendees', {}))

	for person, (dates, things) in data.items():
		dates_by_person[person].update(dates)
		for thing in things:
			people_by_thing[thing].add(person)
			
	for thing, people in people_by_thing.items():
		if len(people) < thresholds[thing]:
			print "removing {} because only {} interest (min {})".format(thing, len(people), thresholds[thing])
			del(people_by_thing[thing])
			continue
		
		peoplebydate = defaultdict(lambda: set())
		for person, dates in dates_by_person.items():
			# faster than nested loop iterating through
			# `people` for keys to get from datesby?
			if person not in people:
				continue
			for date in dates:
				peoplebydate[date].add(person)
				
		for date, people in peoplebydate.items():
			num_required = len(required_attendees[thing])
			num_required_available = len(people.intersection(required_attendees[thing]))
			if num_required != num_required_available:
				print "removing {} for {} because only {}/{} required attendees are available".format(date, thing, num_required_available, num_required)
				del(peoplebydate[date])
				continue
		
			if len(people) < thresholds[thing]:
				print "removing {} for {} because only {} interest (min {})".format(thing, date, len(people), thresholds[thing])
				del(peoplebydate[date])
				continue
				
		if len(peoplebydate) == 0:
			print "no dates where more than {} can do {}. Sadness.".format(thresholds[thing], thing)
			continue
			
		bestdates = sorted(peoplebydate, 
			lambda a,b: cmp(len(peoplebydate[b]),len(peoplebydate[a])))
			
		date_and_people_by_thing[thing] = []
		for date in bestdates:
			date_and_people_by_thing[thing].append((date, peoplebydate[date]))

	return date_and_people_by_thing
		
def print_options(date_and_people_by_thing):
	print "==="
	for thing, options in date_and_people_by_thing.items():
		print "Top options for {}:".format(thing)
		for date, people in options:
			print "  {} with {}: {}".format(date, len(people), '; '.join(people))

def do_tests():
	data = {
		'person1': [
				("date1", "date4"),
				("thing1", "thing3"),
			],
		'person2': [
				("date1", "date2"),
				("thing1", "thing2"),
			],
		'person3': [
				("date1", "date2", "date3"),
				("thing1", "thing2", "thing3", "thing4"),
			],
	}

	print "BASIC\n========"
	print_options(all_viable_options(data))
	print ""

	print "MISSING REQUIRED ATTENDEE\n======="
	overrides = {
		'required_attendees': {
			'thing1': ["person4",],
		},
	}
	print_options(all_viable_options(data, overrides))
	print ""

	print "LOW THRESHOLD\n======="
	overrides = {
		'thresholds': {
			'thing4': 1,
		},
	}
	print_options(all_viable_options(data, overrides))
	print ""



if __name__ == '__main__':
	# TODO: split tests into proper tests/ dir
	do_tests()