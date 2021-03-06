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
import logging
import os
import time
from typing import Callable, Optional

from psycopg2 import errorcodes
from pkg_resources import resource_filename
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm.exc import NoResultFound
from werkzeug.security import generate_password_hash

from subscription_manager.app import create_app
from subscription_manager.db.models import User
from swim_backend.db import db_save, db

__author__ = "EUROCONTROL (SWIM)"

_logger = logging.getLogger(__name__)


def _save(obj):
    try:
        db_save(db.session, obj)
    except Exception as e:
        _logger.error(f"Couldn't save object {obj}: {str(e)}")


def _user_exists(user):
    try:
        db.session.query(User).filter_by(username=user.username).one()
    except NoResultFound:
        return False

    return True


def init_db():
    config_file = resource_filename(__name__, 'config.yml')
    app = create_app(config_file)

    users = [
        User(username=os.environ['SM_ADMIN_USER'],
             password=generate_password_hash(os.environ['SM_ADMIN_PASS']),
             active=True,
             is_admin=True),
        User(username=os.environ['SWIM_ADSB_SM_USER'],
             password=generate_password_hash(os.environ['SWIM_ADSB_PASS']),
             active=True,
             is_admin=False),
        User(username=os.environ['SWIM_EXPLORER_SM_USER'],
             password=generate_password_hash(os.environ['SWIM_EXPLORER_PASS']),
             active=True,
             is_admin=False)
    ]

    with app.app_context():
        for user in users:
                if _user_exists(user):
                    _logger.info(f"User {user.username} already exists. Skipping...")
                    continue
                _save(user)
                _logger.info(f'User {user.username} saved successully in DB')


def db_operation(func: Callable, retry: int, delay: Optional[int] = 1):
    """

    :param func:
    :param retry:
    :param delay:
    :return:
    """
    try:
        func()
    except OperationalError as e:
        retry -= 1
        if retry < 0:
            _logger.info(f'Max retries reached. Failed because: {str(e)}')
            return
        _logger.info(f'DB error occurred. Retrying in {delay} seconds...')
        time.sleep(delay)
        db_operation(func, retry, delay * 2)


if __name__ == '__main__':
    db_operation(init_db, retry=5)
