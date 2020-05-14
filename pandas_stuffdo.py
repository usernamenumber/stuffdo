# %%
import pandas as pd
import numpy as np

# %% [markdown]
# # Scoring algorithm
# ## Per-attendee component
# - Higher the fewer other dates on which this attendee could attend this event
# - Higher the fewer other events in which this attendee is interested
# 
# ## Per-date component
# - Higher the greater the % of people interested in this event are available on this date
# - Higher the fewer other events can run on this date
# 
# ## Per-event component 
# - Higher the fewer other dates on which this event could run
# 
# 
# 1. For each event+date pair, calculate a score factoring in all of the above
#  1. Select top-scoring event+date
#  2. Remove ^^^
#  3. Repeat

# %%
def gather_prefs(form_data):
    date_tuples = []
    for d in form_data:
        person = d['person']
        dates = d['dates']
        date_tuples += [(person, date) for date in dates]
    availability = pd.DataFrame(date_tuples, columns=('person','date')).set_index('person')

    event_tuples = []
    for d in form_data:
        person = d['person']
        events = d['events']
        event_tuples += [(person, event) for event in events]
    interest = pd.DataFrame(event_tuples, columns=('person','event')).set_index('person')

    return availability.join(interest).reset_index()

# %%
def gen_scores(prefs):
    def people_for_event(event):
        return set(prefs[prefs['event'] == event]['person'])

    def people_for_event_date(event, date):
        return set(prefs[(prefs['date'] == date) & (prefs['event'] == event)]['person'])

    def dates_for_event_person(event, person):
        return set(prefs[(prefs['event'] == event) & (prefs['person'] == person)]['date'])

    def events_for_person(person):
        return set(prefs[prefs['person'] == person]['event'])

    def dates_for_person(person):
        return set(prefs[prefs['person'] == person]['date'])

    def dates_for_event(event):
        """
        Note that this does not return dates an event could run but in which 0 people expressed interest
        """
        return set(prefs[prefs['event'] == event]['date'])

    selections = []
    scores = pd.DataFrame()
    # Higher the fewer other dates on which this attendee could attend this event
    scores['other_dates_score'] = prefs.apply(lambda p: 1.0 / len(dates_for_event_person(p['event'], p['person'])), axis=1) 

    # Higher the fewer other events the average interested person also wants to attend
    scores['other_events_score'] = prefs.apply(lambda p: 1.0 / len(events_for_person(p['person'])), axis=1) 

    # Higher the greater the % of people interested in this event who are available on this date
    scores['other_interest_score'] = prefs.apply(lambda p: len(people_for_event_date(p['event'], p['date'])) / len(people_for_event(p['event'])), axis=1)

    # Higher the fewer other events can run on this date
    scores['date_competition_score'] = prefs.apply(lambda p: 1/len(dates_for_event(p['event'])), axis=1)

    # Take the mean of all person+date+event scores...
    scores = scores.join(prefs).groupby(['date','event']).mean()

    # Then take the mean of those for a single score for each date+event pair
    return scores.mean(axis=1).sort_values()

def selections(prefs):
    if len(prefs) == 0:
        return []

    #scores = score(prefs)
    scores = gen_scores(prefs)
    (date, event, score) = scores.index[-1] + (scores[scores.index[-1]],)
    # TODO: reassociate with attendees for this date+event combo
    return [(date,event,score)] + selections(prefs[(prefs.date != date) & (prefs.event != event)])

# %%
form_data = [
    {
            'person':   'person1',
            'dates':  ("date1", "date4"),
            'events': ("thing1", "thing3"),
            'notes':  '',
    },
    {
            'person':  'person2',
            'dates':  ("date1", "date2"),
            'events': ("thing1", "thing2"),
            'notes':  '',
    },
    {
            'person': 'person3',
            'dates':  ("date1", "date2", "date3"),
            'events':  ("thing1", "thing2", "thing3", "thing4"),
            'notes':  '',
    },
]

print(selections(gather_prefs(form_data)))
