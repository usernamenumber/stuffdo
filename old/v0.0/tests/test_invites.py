import invites
import json

base_data = {
    'person1': {
            'dates':  ("date1", "date4"),
            'events': ("thing1", "thing3"),
            'notes':  '',
    },
    'person2': {
            'dates':  ("date1", "date2"),
            'events': ("thing1", "thing2"),
            'notes':  '',
    },
    'person3': {
            'dates':  ("date1", "date2", "date3"),
            'events':  ("thing1", "thing2", "thing3", "thing4"),
            'notes':  '',
    },
}

def do_test(data, overrides, expected):
    options = invites.all_viable_options(data, overrides)
    # json conversion ignores list vs tuple and other
    # subtle differences we don't care about
    assert(json.dumps(options) == json.dumps(expected))


def test_basics():
    overrides = {}
    expected = {
        "thing2": [
            [ "date1", [ "person2", "person3"] ], 
            [ "date2", [ "person2", "person3" ] ] ], 
        "thing3": [ 
            [ "date1", [ "person3", "person1" ] ] ], 
        "thing1": [ 
            [ "date1", [ "person2", "person3", "person1" ] ], 
            [ "date2", [ "person2", "person3" ] ]
        ]
    }

    do_test(base_data, overrides, expected)


def test_required_attendees():
    overrides = {
		'required_attendees': {
			'thing1': ["person4",],
		},
	}
    expected = {u'thing2': [[u'date1', [u'person2', u'person3']], [u'date2', [u'person2', u'person3']]], u'thing3': [[u'date1', [u'person3', u'person1']]]}
    do_test(base_data, overrides, expected)


def test_low_threshold():
    overrides = {
		'thresholds': {
			'thing4': 1,
		},
	}
    expected = {u'thing2': [[u'date1', [u'person2', u'person3']], [u'date2', [u'person2', u'person3']]], u'thing3': [[u'date1', [u'person3', u'person1']]], u'thing1': [[u'date1', [u'person2', u'person3', u'person1']], [u'date2', [u'person2', u'person3']]], u'thing4': [[u'date1', [u'person3']], [u'date3', [u'person3']], [u'date2', [u'person3']]]}
    do_test(base_data, overrides, expected)
    
