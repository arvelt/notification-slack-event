# -*- coding: utf-8 -*-
# Copyright 2015 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import requests
import os
import json

from logging import basicConfig, getLogger, DEBUG

from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic.base import View
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from .forms import GreetingForm, SlackVerificationForm
from models import SlackUser, Channel
from slack_secret import SLACK_TOKEN

basicConfig(level=DEBUG)
logger = getLogger(__name__)

class IndexView(TemplateView):
    template_name = "index.html"

    def get(self, request, *args, **kwargs):
        return self.render_to_response({})

    def post(self, request, *args, **kwargs):
        form = GreetingForm(request.POST)
        if form.is_valid():
            _form = form
        else:
            _form = None
        return self.render_to_response({'form': _form})


class ReceiveHookView(View):

	@method_decorator(csrf_exempt)
	def dispatch(self, *args, **kwargs):
		return super(ReceiveHookView, self).dispatch(*args, **kwargs)

	def post(self, request, *args, **kwargs):
		# url_verification
		# logger.info('Url verification: %r %r %r' % (data.get('token'), data.get('challenge'), data.get('type')))
		# return HttpResponse(data.get('challenge', ''), content_type="text/plain")

		try:
			event_info = json.loads(request.body)
		except TypeError as e:
			return HttpResponse(status=200)
		logger.info('Subscribe event: %r' % event_info)

		event_type = event_info.get('event', {}).get('type')
		stared_item_type = event_info.get('event', {}).get('item', {}).get('type')
		if event_type == 'user_change':
			self._user_change(event_info)
		elif event_type == 'star_added' and stared_item_type == 'channel':
			self._star_add_channel(event_info)
		elif event_type == 'star_removed' and stared_item_type == 'channel':
			self._star_remove_channel(event_info)
		else:
			logger.info('Skip event: %s %s' % (event_type, stared_item_type))
		return HttpResponse(status=200)

	def _user_change(self, event_info):
		user_id = event_info.get('event', {}).get('user', {}).get('id') or ''
		name = event_info.get('event', {}).get('user', {}).get('name') or ''
		status_text = event_info.get('event', {}).get('user', {}).get('profile', {}).get('status_text')
		status_emoji = event_info.get('event', {}).get('user', {}).get('profile', {}).get('status_emoji')

		entity = SlackUser.get_by_id(user_id)
		logger.info('Change status %r to %r' % (entity.profile.status_text, status_text))

		if status_text == entity.profile.status_text:
			logger.info('Skip notification status: %r %r' % (name, user_id))
			return HttpResponse(status=200)
		entity = SlackUser.update(event_info.get('event', {}).get('user'))

		for channel_id in entity.stared_channel:
			message = "%s change status to %s %s" % (name, status_emoji, status_text)
			POST_URL = "https://slack.com/api/chat.postMessage" \
				"?token=%s&channel=%s&name=@Notification change status&text=%s" \
				% (SLACK_TOKEN, channel_id, message)
			logger.debug('POST_URL: %s' % POST_URL)
			res = requests.post(POST_URL)
			logger.info('chat.postMessage reponse: %s' % res.text)
		else:
			logger.info('Skip notification nothing stared channels, user:%s' % user_id)

		return HttpResponse(status=200)

	def _star_add_channel(self, event_info):
		channel_id = event_info.get('event', {}).get('item', {}).get('channel')
		user_id = event_info.get('event', {}).get('user')

		URL = "https://slack.com/api/channels.info" \
			"?token=%s&channel=%s" \
			% (SLACK_TOKEN, channel_id)
		logger.debug('URL: %s' % URL)
		res = requests.get(URL)
		try:
			_info = json.loads(res.text)
		except TypeError as e:
			return HttpResponse(status=200)
		entity = Channel.update(_info.get('channel'))
		SlackUser.add_stared_channels(user_id, channel_id)

		return HttpResponse(status=200)

	def _star_remove_channel(self, event_info):
		channel_id = event_info.get('event', {}).get('item', {}).get('channel')
		user_id = event_info.get('event', {}).get('user')

		URL = "https://slack.com/api/channels.info" \
			"?token=%s&channel=%s" \
			% (SLACK_TOKEN, channel_id)
		logger.debug('URL: %s' % URL)
		res = requests.get(URL)
		try:
			_info = json.loads(res.text)
		except TypeError as e:
			return HttpResponse(status=200)
		entity = Channel.update(_info.get('channel'))
		SlackUser.remove_stared_channels(user_id, channel_id)
		return HttpResponse(status=200)
