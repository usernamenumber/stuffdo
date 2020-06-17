from django.test import TestCase
from stuffdo import models
from stuffdo.scoring import DateSelector 

# Create your tests here.

class scoringTestCase(TestCase):
    def setUp(self):
        self.form_data = [
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

        self.date_selector = DateSelector.from_json(self.form_data)

    def test_people_for_event(self):
        """people_for_event returns all people interested in an event"""
        self.assertEqual(
            self.date_selector._people_for_event('thing2'),
            set(['person2', 'person3']),
        )

    def test_selections(self):
        self.assertEqual(
            self.date_selector.selections,
            [('date2', 'thing2', {'person2', 'person3'}, 0.53125), ('date1', 'thing1', {'person2', 'person1', 'person3'}, 0.5277777777777778), ('date3', 'thing4', {'person3'}, 0.47916666666666663), ('date4', 'thing3', {'person1'}, 0.4375)],
        )

    def test_invites(self):
        self.date_selector.invites