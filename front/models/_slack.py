# -*- coding: utf-8 -*-
from logging import basicConfig, getLogger, DEBUG

from google.appengine.ext import ndb

basicConfig(level=DEBUG)
logger = getLogger(__name__)

class Channel(ndb.Model):
	id = ndb.StringProperty(indexed=False, default='')
	name = ndb.StringProperty(indexed=False, default='')
	name_normalized = ndb.StringProperty(indexed=False, default='')

	@classmethod
	def key_from_id(cls, id):
		return ndb.Key(cls, "%s_slack" % str(id))

	@classmethod
	def get_by_id(cls, id):
		key = cls.key_from_id(id)
		entity = key.get()
		if entity:
			logger.info('Get Channel: %r ' % id)
			return entity
		else:
			logger.info('Create Channel: %r ' % id)
			return cls(key=key)

	@classmethod
	def update(cls, channel_info):
		_id = channel_info.get('id')
		entity = cls.get_by_id(_id)
		entity.populate(
			id=channel_info.get('id'),
			name=channel_info.get('name'),
			name_normalized=channel_info.get('name_normalized'),
		)
		entity.put()
		logger.info('Update Channel: %r ' % _id)
		return entity

	@classmethod
	def delete(cls, channel_info):
		_id = channel_info.get('id')
		key = cls.key_from_id(id)
		logger.info('Delete Channel: %r ' % _id)
		return key.delete()


class Profile(ndb.Model):
	status_text = ndb.StringProperty(indexed=False, default='')
	status_emoji = ndb.StringProperty(indexed=False, default='')
	real_name = ndb.StringProperty(indexed=False, default='')
	display_name = ndb.StringProperty(indexed=False, default='')
	real_name_normalized = ndb.StringProperty(indexed=False, default='')
	display_name_normalized = ndb.StringProperty(indexed=False, default='')
	email = ndb.StringProperty(indexed=False)
	team = ndb.StringProperty(indexed=False)
	title = ndb.StringProperty(indexed=False, default='')


class SlackUser(ndb.Model):
	id = ndb.StringProperty(indexed=False, default='')
	team_id = ndb.StringProperty(indexed=False, default='')
	name = ndb.StringProperty(indexed=False, default='')
	deleted = ndb.BooleanProperty(indexed=False)
	real_name = ndb.StringProperty(indexed=False, default='')
	updated = ndb.IntegerProperty(indexed=False)
	is_app_user = ndb.BooleanProperty(indexed=False)
	profile = ndb.StructuredProperty(Profile, indexed=False)
	stared_channel = ndb.StringProperty(indexed=False, repeated=True)

	@classmethod
	def get_by_id(cls, id):
		key = ndb.Key(cls, "%s_slack" % str(id))
		entity = key.get()
		if entity:
			logger.info('Get SlackUser: %r ' % id)
			return entity
		else:
			logger.info('Create SlackUser: %r ' % id)
			return cls(key=key, profile=Profile())

	@classmethod
	def update(cls, user_info):
		_id = user_info.get('id')
		entity = cls.get_by_id(_id)
		entity.populate(
			id=user_info.get('id'),
			team_id=user_info.get('team_id'),
			name=user_info.get('name'),
			deleted=user_info.get('deleted'),
			real_name=user_info.get('real_name'),
			updated=user_info.get('updated'),
			is_app_user=user_info.get('is_app_user'),
			profile=Profile(
				status_text=user_info.get('profile', {}).get('status_text'),
				status_emoji=user_info.get('profile', {}).get('status_emoji'),
				real_name=user_info.get('profile', {}).get('real_name'),
				display_name=user_info.get('profile', {}).get('display_name'),
				real_name_normalized=user_info.get('profile', {}).get('real_name_normalized'),
				display_name_normalized=user_info.get('profile', {}).get('display_name_normalized'),
				email=user_info.get('profile', {}).get('email'),
				team=user_info.get('profile', {}).get('team'),
				title=user_info.get('profile', {}).get('title'),
			)
		)
		entity.put()
		logger.info('Update SlackUser: %r ' % _id)
		return entity

	@classmethod
	def add_stared_channels(cls, user_id, stared_channel_id):
		entity = cls.get_by_id(user_id)
		new_channels = set(entity.stared_channel)
		new_channels.add(stared_channel_id)
		entity.populate(stared_channel=list(new_channels))
		entity.put()
		logger.info('Stared channels SlackUser: %r %r' % (user_id, entity.stared_channel))
		return entity

	@classmethod
	def remove_stared_channels(cls, user_id, removed_channel_id):
		entity = cls.get_by_id(user_id)
		new_channels = set(entity.stared_channel)
		try:
			new_channels.remove(removed_channel_id)
		except KeyError as e:
			pass
		entity.populate(stared_channel=list(new_channels))
		entity.put()
		logger.info('Stared channels SlackUser: %r %r' % (user_id, entity.stared_channel))
		return entity
