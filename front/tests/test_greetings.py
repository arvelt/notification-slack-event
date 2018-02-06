# -*- coding: utf-8 -*-
import logging

from front.models import Greeting

class TestGreetings(object):
    def test_greetings(self):
        entity = Greeting()
        assert entity is not None
