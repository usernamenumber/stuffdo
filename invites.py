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

thresholds = defaultdict(lambda: 2)
datesbyperson = defaultdict(lambda: set())
personbything = defaultdict(lambda: set())
peopleanddatebything = {}

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
		if len(people) < thresholds[thing]:
			print "removing {} for {} because only {} interest (min {})".format(thing, date, len(people), thresholds[thing])
			del(peoplebydate[date])
			continue
			
	if len(peoplebydate) == 0:
		print "No dates where more than {} can do {}. Sadness.".format(thresholds[thing], thing)
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
		
