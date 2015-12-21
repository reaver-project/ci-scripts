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

    def trigger(self, build_conf, properties = {}, personal = False):
        data = {
            'buildType': {
                'id': 'Random_Random'
            }
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

        response = self.api.buildQueue.post(data)
        return response

    def status(self, build_id):
        return getattr(self.api.buildQueue, 'id:%d' % build_id).get()

