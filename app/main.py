#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2012 Narantech Inc.
#
# This program is a property of Narantech Inc. Any form of infringement is
# strictly prohibited. You may not, but not limited to, copy, steal, modify
# and/or redistribute without appropriate permissions under any circumstance.
#
#  __    _ _______ ______   _______ __    _ _______ _______ _______ __   __
# |  |  | |   _   |    _ | |   _   |  |  | |       |       |       |  | |  |
# |   |_| |  |_|  |   | || |  |_|  |   |_| |_     _|    ___|       |  |_|  |
# |       |       |   |_||_|       |       | |   | |   |___|       |       |
# |  _    |       |    __  |       |  _    | |   | |    ___|      _|       |
# | | |   |   _   |   |  | |   _   | | |   | |   | |   |___|     |_|   _   |
# |_|  |__|__| |__|___|  |_|__| |__|_|  |__| |___| |_______|_______|__| |__|


"""App store manager application
"""

# default
import os
import re
import logging
import smtplib
from functools import partial

# clique
import clique
import clique.runtime
import clique.web

# email
from idle import Idler
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

#ambiency
import ambiency
from ambiency import build_sensor 
from ambiency import build_trigger 
from ambiency import build_trigger_data_type
from ambiency import build_source
from ambiency import build_actuator
from ambiency import build_action
from ambiency import build_action_data_type


SUPPORT_MAIL = {'gmail': [('imap.gmail.com', 993), ('smtp.gmail.com', 587)],
                'narantech': [('imap.gmail.com', 993), ('smtp.gmail.com', 587)],
                'naver': [('imap.naver.com', 993), ('smtp.naver.com', 587)],
                'daum': [('imap.daum.net', 993), ('smtp.daum.net', 465)],
                'hanmail': [('imap.daum.net', 993), ('smtp.daum.net', 465)]}
IMAPS = {}
MAIL_IDS = {}  # user -> last mail id
USERS = '''users'''


@clique.web.endpoint()
def test_send(user):
  password = get_user_password(user)
  send_mail(user, password, user, [user], "Test", "Test")


@clique.web.endpoint()
def get_users():
  users_folder = os.path.join(clique.runtime.res_dir(),
                              USERS)
  if os.path.exists(users_folder):
    users = os.listdir(users_folder)
    logging.debug("get users:%s", str(users))
    return users
  return []


@clique.web.endpoint()
def add_user(user, password):
  if not re.match(r"[^@]+@[^@]+\.[^@]+", user):
    return False

  data = SUPPORT_MAIL.get(extract_mail(user))
  if not data:
    return False

  if user and password:
    logging.debug("insert user:%s", str(user))
    insert_user(user, password)
    user_added(user, password, data[0])
    ambiency.refresh_all()
    return user
  else:
    raise Exception("user id and password can't be empty")


@clique.web.endpoint()
def delete_user(user):
  path = _build_user_path(user)
  if os.path.exists(path):
    logging.debug("delete user:%s", str(user))
    os.remove(path)
    user_removed(user)
    ambiency.refresh_all()
  return user


def load_users():
  for user in get_users():
    data = SUPPORT_MAIL[extract_mail(user)]
    password = get_user_password(user)
    user_added(user, password, data[0])


def _build_user_path(user):
  users_folder = os.path.join(clique.runtime.res_dir(),
                              USERS)

  if not os.path.exists(users_folder):
    os.mkdir(users_folder)
  
  file_path = os.path.join(users_folder, user)
  return file_path


def insert_user(user, password):
  file_path = _build_user_path(user)

  if os.path.exists(file_path):
    raise Exception("user exists:%s" % user)

  with open(file_path, 'w') as f:
    f.write(':'.join([user, password]))

  logging.debug("insert user success:%s", str(user))
  return user


def get_user_password(user):
  file_path = _build_user_path(user)

  if not os.path.exists(file_path):
    raise Exception("user not exists:%s" % user)

  with open(file_path, 'r') as f:
    data = f.read().split(':')
    logging.debug("user:%s has password:%s", str(user), str(data[1]))
    return data[1]


def user_added(user, password, imap_data):
  imap = Idler(user, password, partial(handle_message, user),
               imap_data[0], imap_data[1])
  imap.start()
  logging.debug("user:%s imap started", str(user))
  IMAPS[user] = imap


def extract_mail(user):
  ri = user.rindex('@')
  add = user[ri + 1:]
  return add.split('.')[0]


def user_removed(user):
  if user in IMAPS:
    imap = IMAPS[user]
    imap.stop()
    logging.debug("user:%s imap stopped", str(user))
    del IMAPS[user]


def handle_message(user, mid, message):
  last_one = MAIL_IDS.get(user)
  logging.debug("Handle message of user:%s, last mid:%s, new mid:%s, message:%s",
                str(user), str(last_one), str(mid), str(message))
  if last_one and last_one == mid:
    logging.debug("Last mid:%s and new mid:%s are same", str(last_one), str(mid))
    return
  ambiency.push('email', "receivedEmailTrigger", [user], message)
  MAIL_IDS[user] = mid


def send_mail(user, pwd, from_addr, to_addr, subject, body):
  extracted = extract_mail(user)
  logging.debug("extract mail:%s", str(extracted))
  data = SUPPORT_MAIL.get(extracted)
  if not data:
    logging.debug("Not support smtp mail:%s", str(user))
    return

  data = data[1]

  msg = MIMEMultipart('alternative')
  msg['Subject'] = subject
  msg['From'] = from_addr
  msg['To'] = ', '.join(to_addr)
  msg.attach(MIMEText(body, 'plain'))

  try:
    client = smtplib.SMTP(data[0], data[1])
    client.ehlo()
    client.starttls()
    client.login(from_addr, pwd)
    msg_txt = msg.as_string()
    logging.debug("send message\n%s", msg_txt)
    client.sendmail(from_addr, to_addr, msg_txt)
    client.close()
  except:
    logging.exception("Fail to send message from %s to %s", from_addr, to_addr)


def mail_action(data):
  logging.debug("mail action data :%s",
                str(data))

  if data.data and hasattr(data.data, '__dict__'):
    data.data = data.data.__dict__

  if data.data and isinstance(data.data, dict):
    password = get_user_password(data.source_ids[0])
    receivers = data.data.get('To').split(',')
    subject = data.data.get('Subject')
    message = data.data.get('Text')
    send_mail(data.source_ids[0], password, data.source_ids[0], receivers, subject, message)


@ambiency.actuators
def get_actuators():
  sources = []
  for user in get_users():
    sources.append(build_source(user, 'send a mail from %s' % user,
                                desc='Send a mail from sender to receivers',
                                icon_uri='/ambiency/source.ico'))
  types = [['To', 'Receivers', 'string', 'text', True, '', 'Represent receivers'],
           ['Subject', 'Subject', 'String', 'text', False, '', 'Represent a subject'],
           ['Text', 'Message', 'string', 'text', False, '', 'Represent a message']]
  action_data_types = []
  for typ in types:
    action_data_types.append(build_action_data_type(*typ))
  actions = []
  actions.append(build_action('sendEmailAction', 
                              'Send a mail',
                              sources,
                              action_data_types,
                              'Send a mail',
                              '/ambiency/action.ico'))
  actuators = []
  actuators.append(build_actuator('email', 'E-mail', actions, mail_action,
                                  'Utilizes email', '/ambiency/actuator.ico'))
  return actuators


@ambiency.sensors
def get_sensors():
  sources = []
  for user in get_users():
    sources.append(build_source(user, 'Receive by %s' % user,
                                desc='Notify received email',
                                icon_uri='/ambiency/source.ico'))

  types = [['From', 'Sender', 'string', 'text', 'Represent a sender'],
           ['To', 'Recivers', 'string', 'text', 'Represent receivers'],
           ['Subject', 'Subject', 'string', 'text', 'Represent a subject'],
           ['Text', 'Message', 'string', 'text', 'Represent a message']]
  trigger_data_types = []
  for typ in types:
    trigger_data_types.append(build_trigger_data_type(*typ))
  triggers = []
  triggers.append(build_trigger('receivedEmailTrigger',
                                'Receive a mail and match the message',
                                sources,
                                trigger_data_types,
                                "It's trigger when recieved a email",
                                '/ambiency/trigger.ico'))
  sensors = []
  sensors.append(build_sensor('email', 'E-mail', triggers,
                              'Utilizes email', '/ambiency/sensor.ico'))
  return sensors 


def terminate():
  logging.info("Terminating the Test...")


def start():
  try:
    logging.debug("Boot email app...")
    clique.web.set_static_path(os.path.join(clique.runtime.res_dir(), "web"),
                               sub_path=[{'url':'/ambiency', 
                                          'path': os.path.join(clique.runtime.res_dir(), 'ambiency')}])
    load_users()
    logging.debug("Start email app.")
  except:
    logging.exception("Failed to start the email app.")
    raise


if __name__ == "__main__":
  start()
