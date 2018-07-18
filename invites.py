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


from collections import defaultdict

datesbyperson = defaultdict(lambda: set())
personbything = defaultdict(lambda: set())
peopleanddatebything = {}

thresholds = defaultdict(lambda: 2)
required_attendees = defaultdict(lambda: [])
required_attendees['thing1'].append("person4")

"""
goal: figure out which combinations of people+date+thing would have the best attendance.
	
for any "thing" with interest above a threshold, show the date that works for the most people, then re-check the threshold and remove if not met.

- group people by interest in thing
- remove things with total interest below threshold
- for each remaining thing:
	- collect people interested in thing, grouped by date
	- remove thing if max(group_lens) < thresh
"""
for person, (dates, things) in data.items():
	datesbyperson[person].update(dates)
	for thing in things:
		personbything[thing].add(person)
		
for thing, people in personbything.items():
	if len(people) < thresholds[thing]:
		print "removing {} because only {} interest (min {})".format(thing, len(people), thresholds[thing])
		del(personbything[thing])
		continue
	
	peoplebydate = defaultdict(lambda: set())
	for person, dates in datesbyperson.items():
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
		
	peopleanddatebything[thing] = []
	for date in bestdates:
		peopleanddatebything[thing].append((date, peoplebydate[date]))
		
print "==="
for thing, options in peopleanddatebything.items():
	print "Top options for {}:".format(thing)
	for date, people in options:
		print "  {} with {}: {}".format(date, len(people), '; '.join(people))
		
