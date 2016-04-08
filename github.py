#!/usr/bin/env python
# -*- coding: utf-8 -*-

import slumber
import requests


class Session:
    def __init__(self, url, user, token):
        self.api_session = requests.session()
        self.api_session.headers['Accept'] = 'application/vnd.github.v3+json'

        self.auth = requests.auth.HTTPBasicAuth(user, token)

        self.api = slumber.API(url, session = self.api_session, auth = self.auth, append_slash = False)

    def set_status(self, owner, repo, sha, params):
        self.api.repos(owner)(repo).statuses(sha).post(params)
