"""
Copyright 2019 EUROCONTROL
==========================================

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the 
following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following 
   disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following 
   disclaimer in the documentation and/or other materials provided with the distribution.
3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products 
   derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, 
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE 
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, 
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR 
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, 
WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE 
USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

==========================================

Editorial note: this license is an instance of the BSD license template as provided by the Open Source Initiative: 
http://opensource.org/licenses/BSD-3-Clause

Details on EUROCONTROL: http://www.eurocontrol.int
"""
import pytest

from subscription_manager.db import Topic
from subscription_manager.db.topics import get_topic_by_id, get_topics, create_topic, update_topic
from subscription_manager.db.utils import db_save
from tests.utils import make_topic

__author__ = "EUROCONTROL (SWIM)"


@pytest.fixture
def generate_topic():
    def _generate_topic(name):
        topic = make_topic(name)
        return db_save(topic)

    return _generate_topic


def test_get_topic_by_id__does_not_exist__returns_none():
    assert get_topic_by_id(1111) is None


def test_get_topic_by_id__object_exists_and_is_returned(generate_topic):
    topic = generate_topic('test_topic')

    db_topic = get_topic_by_id(topic.id)

    assert isinstance(db_topic, Topic)
    assert topic.id == db_topic.id


def test_get_topics__no_topic_in_db__returns_empty_list(generate_topic):
    db_topics = get_topics()

    assert [] == db_topics


def test_get_topics__existing_topics_are_returned(generate_topic):
    topics = [generate_topic('test_topic_1'), generate_topic('test_topic_2')]

    db_topics = get_topics()

    assert 2 == len(db_topics)
    assert topics == db_topics


def test_create_topic():
    topic = make_topic('test_topic')

    db_topic = create_topic(topic)

    assert isinstance(db_topic, Topic)
    assert isinstance(db_topic.id, int)
    assert topic.name == db_topic.name


def test_update_topic(generate_topic):
    topic = generate_topic('test_topic')

    topic.name = 'new name'

    updated_topic = update_topic(topic)

    assert isinstance(updated_topic, Topic)
    assert 'new name' == updated_topic.name