''' Python script (run in Py 3.3.2) to listen to IMAP-accessible mailboxes for incoming emails and other events (deletion / expunge).
    It keeps a log of mailbox  activity.  This uses push rather than polling, with IMAP IDLE. I'd call this a listener / event handler.
    You can use "tail -f" on the log file to perform other actions--logging activity to a database, for example.  '''

import logging
import imaplib2
import email
from email.header import decode_header
from threading import Thread, Event


class Idler(object):
  def __init__(self, user, pwd, handler, imap='imap.gmail.com', port=993):
    self.thread = Thread(target=self.idle)
    self.user = user
    self.pwd = pwd
    self.imap = imap
    self.port = port
    self.handler = handler
    self.event = Event()
    self.headers = ['From', 'To', 'Subject']

  def start(self):
    self.thread.start()

  def stop(self):
    self.event.set()

  def handle_msg(self, response, cb_arg, error):
    print "response:%s, cb_arg:%s, error:%s" % (str(response),
                                                str(cb_arg),
                                                str(error))

  def decode_header(self, header):
    if header.startswith('=?'):
      d = decode_header(header)
      return d[0][0].decode(d[0][1])
    return header

  def decode_text(self, msg):
      dec = None
      ct = msg["CONTENT-TYPE"]
      p = msg.get_payload(decode=True)
      if ct:
        dt = ct.split()
        for d in dt:
          if d.startswith('charset='):
            dec = d.split('=')[1]
        if dec:
          p = p.decode(dec)
      return p

  def do(self):
    typ, data = self.conn.select("Inbox", readonly=True)
    mid = data[0]
    typ, data = self.conn.fetch(mid, "(RFC822)")
    emsg = email.message_from_string(data[0][1])
    value = {}
    for header in self.headers:
      value[header] = self.decode_header(emsg[header])

    text = ''
    if emsg.is_multipart():
      for payload in emsg.get_payload():
        text += self.decode_text(payload)
    else:
      text += self.decode_text(emsg)

    value['Text'] = text
    try:
      self.handler(mid, value)
    except:
      logging.debug("error while handle value:%s", str(value), exc_info=True)

  def idle(self):
    while not self.event.is_set():
      self.conn = imaplib2.IMAP4_SSL(self.imap, self.port)
      self.conn.login(self.user, self.pwd)
      self.conn.select("Inbox", readonly=True)
      print "login!"

      while not self.event.is_set():
        self.needsync = False

        def callback(args):
          if not self.event.is_set():
            self.needsync = True
            self.event.set()
        try:
          self.conn.idle(callback=callback)
        except:
          logging.debug("error while idle", exc_info=True)
          break

        self.event.wait()

        if self.needsync:
          self.event.clear()
          try:
            self.do()
          except:
            logging.debug("error while do", exc_info=True)

    self.conn.close()
    self.conn.logout()
