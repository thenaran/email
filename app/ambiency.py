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


"""

Ambiency library module
=======================
- Ambiency library Version 0.1.141111
- Ambiency version greater than or equal to 1.2.14102800
"""
# default
import uuid

# clique
import clique
import clique.event
import clique.isc
import clique.runtime
from clique.isc import Endpoint

AMBIENCY_SENSOR_CHANGED = '''ambiency.sensor.changed'''
AMBIENCY_ACTUATOR_CHANGED = '''ambiency.actuator.changed'''
clique.event.create_topic(AMBIENCY_SENSOR_CHANGED)
clique.event.create_topic(AMBIENCY_ACTUATOR_CHANGED)

PUSH_KEY = uuid.uuid4()
ACTUATORS_KEY = uuid.uuid4()
SENSORS_KEY = uuid.uuid4()
ENDPOINTS_KEY = uuid.uuid4()

__ACTION_ID__ = '''action_id'''
__ACTIONS__ = '''actions'''
__ACTUATOR_ID__ = '''actuator_id'''
__CHILDREN__ = '''children'''
__DATA__ = '''data'''
__DATA_TYPES__ = '''data_types'''
__DEFAULT__ = '''default'''
__DESC__ = '''desc'''
__DETAIL__ = '''detail'''
__DISPLAY_NAME__ = '''display_name'''
__FUNC__ = '''func'''
__ICON_URI__ = '''icon_uri'''
__KEY__ = '''key'''
__META_TYPE__ = '''meta_type'''
__NATIVE_TYPE__ = '''native_type'''
__REQUIRED__ = '''required'''
__SENSOR_ID__ = '''sensor_id'''
__SOURCE_ID__ = '''source_id'''
__SOURCE_IDS__ = '''source_ids'''
__SOURCES__ = '''sources'''
__TRIGGER_ID__ = '''trigger_id'''
__TRIGGERS__ = '''triggers'''


def build_sensor(sensor_id, display_name, triggers,
                 desc='', icon_uri=''):
  """Helper to build a sensor model.

  :param string sensor_id: Sensor ID
  :param string display_name: Display name of Sensor
  :param list triggers: Triggers
  :param string desc: Description of Sensor
  :param string icon_uri:Icon uri path of Sensor
  :rtype: dict
  :return: Sensor
  """
  if not (sensor_id and display_name and triggers):
    raise

  return {__SENSOR_ID__: sensor_id,
          __DISPLAY_NAME__: display_name,
          __TRIGGERS__: triggers,
          __DESC__: desc,
          __ICON_URI__: icon_uri}


def build_trigger(trigger_id, display_name, sources=[], 
                  data_types=[], desc='', icon_uri=''):
  """Helper to build a trigger model.
  
  :param string trigger_id: Trigger ID
  :param string display_name: Display name of Trigger
  :param list sources: Sources of Sensor
  :param list data_types: Action Data types
  :param string desc: Description of Trigger
  :param string icon_uri: Icon uri path of Trigger
  :rtype: dict
  :return: Trigger
  """
  if not (trigger_id and display_name):
    raise

  return {__TRIGGER_ID__: trigger_id,
          __DISPLAY_NAME__: display_name,
          __SOURCES__: sources,
          __DATA_TYPES__: data_types,
          __DESC__: desc,
          __ICON_URI__: icon_uri}


def build_trigger_data_type(key, display_name, native_type, meta_type,
                            desc=''):
  """Helper to build a trigger data type model.
  
  :param string key: Key of Trigger data type
  :param string display_name: Display name of Trigger data type
  :param string native_type: Native type of Trigger data type
                             (int, string, boolean, list, dict, float, tuple)
  :param string meta_type: Meta type of Trigger data type
                           (text, uri, html, fileobj, endpoint, number,
                            file_path, time, date, min, hour, day, month, week, year)
  :param string desc: Description of Trigger data type
  :rtype: dict
  :return: Trigger data type
  """
  if not (key and display_name and meta_type, native_type):
    raise

  return {__KEY__: key,
          __DISPLAY_NAME__: display_name,
          __NATIVE_TYPE__: native_type,
          __META_TYPE__: meta_type,
          __DESC__: desc}


def build_source(source_id, display_name,  detail={},
                 children=[], desc='', icon_uri=''):
  """Helper to build a sensor source model.

  :param string source_id: Source ID
  :param string display_name: Display name of Source
  :param dict detail: Display detail information of Source
  :param list children: Children of Souce
  :param string desc: Description of Source
  :param string icon_uri: Icon uri path of Source
  :rtype: dict
  :return: Source
  """
  if not (source_id and display_name):
    raise

  return {__SOURCE_ID__: source_id,
          __DISPLAY_NAME__: display_name,
          __DETAIL__: detail,
          __CHILDREN__: children,
          __DESC__: desc,
          __ICON_URI__: icon_uri}


def __get_endpoint(func):
  """Get endpoint

  :param function func: function
  :rtype: endpoint
  :return: Endpoint
  """
  endpoints = clique.context(ENDPOINTS_KEY)
  if not endpoints:
    endpoints = {}
    clique.context(ENDPOINTS_KEY, endpoints)

  endpoint = endpoints.get(func.__name__)
  if not endpoint: 
    clique.isc.register_endpoint(func, namespace='ambiency')
    endpoint = Endpoint(name=func.__name__, namespace='ambiency',
                        appname=clique.runtime.app_name())
    endpoints[func.__name__] = endpoint
  return endpoint


def build_actuator(actuator_id, display_name, actions, func,
                   desc='', icon_uri=''):
  """Helper to build an actuator model.

  :param string actuator: Actuator ID
  :param string display_name: Display name of Actuator
  :param list actions: Actions
  :param function func: Function of action
  :param string desc: Description of Actuator
  :param string icon_uri: Icon uri path of Actuator
  :rtype: dict
  :return: Actuator
  """
  if not (actuator_id and display_name and func and actions):
    raise

  return {__ACTUATOR_ID__: actuator_id,
          __DISPLAY_NAME__: display_name,
          __ACTIONS__: actions,
          __FUNC__: __get_endpoint(func),
          __DESC__: desc,
          __ICON_URI__: icon_uri}


def build_action(action_id, display_name, sources=[],
                 data_types=[], desc='', icon_uri=''):
  """Helper to build an action model.

  :param string action_id: Action Id
  :param string display_name: Display name of Action
  :param list sources: Sources of Sensor
  :param list data_types: Action data types
  :param string desc: Description of Action
  :param string icon_uri: Icon uri paht of Action
  :rtype: dict
  :return: Action
  """
  if not (action_id and display_name):
    raise

  return {__ACTION_ID__: action_id,
          __DISPLAY_NAME__: display_name,
          __SOURCES__: sources,
          __DATA_TYPES__: data_types,
          __DESC__: desc,
          __ICON_URI__: icon_uri}


def build_action_data_type(key, display_name, native_type, meta_type,
                           required=False, default='', desc=''):
  """Helper to build an action data type model.

  :param string key: Key of Action data type
  :param string display_name: Display name of Action data type
  :param string native_type: Native type of Action data type
                             (int, string, boolean, list, dict, float, tuple)
  :param string meta_type: Meta type of Action data type
                           (text, uri, html, fileobj, endpoint, number, file_path,
                            time, date, min, hour, day, month, week, year)
  :param bool required: True to be required, False to be not required
  :param native_type default: Default value of Action data type
  :param string desc: Description of Action data type
  :rtype: dict
  :return: Action data type
  """
  if not (key and display_name, native_type, meta_type):
    raise

  return {__KEY__: key,
          __DISPLAY_NAME__: display_name,
          __NATIVE_TYPE__: native_type,
          __META_TYPE__: meta_type,
          __REQUIRED__: required,
          __DEFAULT__: default,
          __DESC__: desc}


def actuators(func):
  """Decorator to register the function as a get_actuators function.
  """
  clique.context(ACTUATORS_KEY, func)
  return func


def sensors(func):
  """Decorator to register the function as a get_sensors function.
  """
  clique.context(SENSORS_KEY, func)
  return func


@clique.isc.endpoint(namespace='ambiency')
def get_sensors(push):
  """Ambiency call function.

  :param function push:
  :rtype: list
  :return: Sensors
  """
  clique.context(PUSH_KEY, push)
  if clique.context(SENSORS_KEY):
    return clique.context(SENSORS_KEY)()
  else:
    return []


@clique.isc.endpoint(namespace='ambiency')
def get_actuators():
  """Ambiency call function.

  :rtype: list
  :return: Actuators
  """
  if clique.context(ACTUATORS_KEY):
    return clique.context(ACTUATORS_KEY)()
  else:
    return []


def push(sensor_id, trigger_id, source_ids, data):
  """Push the sensor data to the ambiency with the key and value pre-defined by the sensor data type.

  :param string sensor_id: Sensor ID
  :param string trigger_id: Trigger ID
  :param list source_ids: Source IDs, Suppose that you used chilren in a source, enumerate it from a parent source ID to a child source ID in a list 
  :param dict data: Notify to Ambiency for changed data
  """
  if clique.context(PUSH_KEY):
    clique.context(PUSH_KEY)({__SENSOR_ID__: sensor_id,
                              __TRIGGER_ID__: trigger_id,
                              __SOURCE_IDS__: source_ids,
                              __DATA__: data})


def refresh_sensors():
  """Refresh sensors.
  """
  clique.event.publish(AMBIENCY_SENSOR_CHANGED, None)


def refresh_actuators():
  """Refresh actuators
  """
  clique.event.publish(AMBIENCY_ACTUATOR_CHANGED, None)


def refresh_all():
  """Refresh Sensors & Actuators
  """
  refresh_sensors()
  refresh_actuators()
