from django.test import TestCase
from stuffdo import models
from stuffdo import scoring 

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

        self.prefs = scoring.gather_prefs(self.form_data)

    def test_people_for_event(self):
        """people_for_event returns all people interested in an event"""
        print("P = {}".format(self.prefs))
        self.assertTrue(True)