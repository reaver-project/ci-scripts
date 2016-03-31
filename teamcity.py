#!/usr/bin/env python
# -*- coding: utf-8 -*-

import slumber
import requests


class Session:
    def __init__(self, url, user, password):
        self.api_session = requests.session()
        self.api_session.headers['Accept'] = 'application/json'
        self.api_session.headers['Content-Type'] = 'application/json'

        self.auth = requests.auth.HTTPBasicAuth(user, password)

        self.api = slumber.API(url, session = self.api_session, auth = self.auth)

    def locator_to_string(self, locator):
        return ','.join(['%s:%s' % (key, str(value)) for key, value in locator.iteritems()])

    def trigger(self, build_conf, properties = {}, personal = False, change = None):
        data = {
            'buildType': {
                'id': build_conf
            },
            'personal': personal
        }

        if properties:
            data['properties'] = {
                'property': [
                    {
                        'name': key,
                        'value': value
                    } for key, value in properties.iteritems()
                ]
            }

        if change is not None:
            data['lastChanges'] = {
                'change': [
                    { 'id': change }
                ]
            }

        response = self.api.buildQueue.post(data)
        return response

    def get_change_id(self, locator):
        resource = getattr(self.api.builds, self.locator_to_string(locator)).get()
        return resource['lastChanges']['change'][0]['id']

    def add_tag(self, locator, tag):
        payload = { 'count': 1, 'tag': [ { 'name': tag } ] }
        getattr(self.api.builds, self.locator_to_string(locator)).tags.post(payload)
