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

#%% 
class DateSelector(object):
    @staticmethod
    def from_json(form_data):
        date_tuples = []
        event_tuples = []
        for d in form_data:
            person = d['person']
            dates = d['dates']
            events = d['events']
            date_tuples += [(person, date) for date in dates]
            event_tuples += [(person, event) for event in events]
        return DateSelector(date_tuples, event_tuples)

    def __init__(self, date_tuples, event_tuples):
        availability = pd.DataFrame(date_tuples, columns=('person','date')).set_index('person')
        interest = pd.DataFrame(event_tuples, columns=('person','event')).set_index('person')

        self.prefs = availability.join(interest).reset_index()
        self._scores = None
        self._selections = None
        self._invites = None

    def _people_for_event(self, event):
        return set(self.prefs[self.prefs['event'] == event]['person'])

    def _people_for_event_date(self, event, date):
        return set(self.prefs[(self.prefs['date'] == date) & (self.prefs['event'] == event)]['person'])

    def _dates_for_event_person(self, event, person):
        return set(self.prefs[(self.prefs['event'] == event) & (self.prefs['person'] == person)]['date'])

    def _events_for_person(self, person):
        return set(self.prefs[self.prefs['person'] == person]['event'])

    def _dates_for_person(self, person):
        return set(self.prefs[self.prefs['person'] == person]['date'])

    def _dates_for_event(self, event):
        """
        Note that this does not return dates an event could run but in which 0 people expressed interest
        """
        return set(self.prefs[self.prefs['event'] == event]['date'])


    def scores_for(self, prefs):
        selections = []
        scores = pd.DataFrame()
        # Higher the fewer other dates on which this attendee could attend this event
        scores['other_dates_score'] = prefs.apply(lambda p: 1.0 / len(self._dates_for_event_person(p['event'], p['person'])), axis=1) 

        # Higher the fewer other events the average interested person also wants to attend
        scores['other_events_score'] = prefs.apply(lambda p: 1.0 / len(self._events_for_person(p['person'])), axis=1) 

        # Higher the greater the % of people interested in this event who are available on this date
        scores['other_interest_score'] = prefs.apply(lambda p: len(self._people_for_event_date(p['event'], p['date'])) / len(self._people_for_event(p['event'])), axis=1)

        # Higher the fewer other events can run on this date
        scores['date_competition_score'] = prefs.apply(lambda p: 1/len(self._dates_for_event(p['event'])), axis=1)

        # Take the mean of all person+date+event scores...
        scores = scores.join(prefs).groupby(['date','event']).mean()

        # Then take the mean of those for a single score for each date+event pair
        return scores.mean(axis=1).sort_values()

    @property
    def scores(self):
        if self._scores is None:
            self._scores = self.scores_for(self.prefs)

        return self._scores

    @property
    def selections(self):
        def _get_selections(prefs):
            # This means we've reached the end of recursion
            if len(prefs) == 0:
                return []

            scores = self.scores_for(prefs)

            # Extract properties of the highest-scoring date/event combination
            (date, event, score) = scores.index[-1] + (scores[scores.index[-1]],) 
            people = self._people_for_event_date(event, date)
            
            # Recurse with all date/event combos minus the selected date and event
            # Thus, scores are re-calculated based on remaining options
            # TODO: reassociate with attendees for this date+event combo
            return [(date,event,people,score)] + _get_selections(prefs[(prefs.date != date) & (prefs.event != event)])

        if self._selections is None:
            self._selections = _get_selections(self.prefs)

        return self._selections


    @property
    def invites(self):
        def _get_invites():
            return { }

        if self._invites is None:
            self._invites = _get_invites()
        
        return self._invites
        

if __name__ == '__main__':
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

    interest = DateSelector.from_json(form_data)
    print(interest.scores)