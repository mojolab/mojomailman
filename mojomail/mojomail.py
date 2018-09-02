#!/usr/bin/python
#Import everything and the kitchen sink
import os, sys,string
import datetime,quopri
import ConfigParser
import logging
import coloredlogs
sys.path.append(".")
from constants import  XPAL_CONSOLE_FORMAT,XPAL_LEVEL_STYLES,XPAL_FIELD_STYLES

def get_xpal_logger(name):
	xpallogger=logging.getLogger(name)
	coloredlogs.install(level="INFO",logger=xpallogger,fmt=XPAL_CONSOLE_FORMAT,level_styles=XPAL_LEVEL_STYLES,field_styles=XPAL_FIELD_STYLES)
	return xpallogger

baselogger=get_xpal_logger("MojoMailBaseLogger")

class MojoMailer(object):
  def __init__(self,configfile,logger=baselogger):
    # directory where to save attachments (default: current)
    config=ConfigParser.ConfigParser()
    config.read(configfile)
    logger.info("Making MojoMailer")
    self.name=config.get("MojoMail","name")
    self.logger=logger
    #self.logger=get_xpal_logger(self.name)
    self.logger.info("Server name is %s" %self.name)
    self.serversig=config.get("MojoMail","serversig")
    self.logfile=config.get("MojoMail","logfile")
    self.tz=config.get("MojoMail","timezone")
    self.detach_dir=config.get("MojoMail","detach_dir")
    self.transport=config.get("MojoMail","transport")
    self.configfile=configfile
  def gettsstring(self):
      return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  '''
  def gettransport(self):
      if self.transport=="GMail":
          self.gmail=MojoGMail(self.configfile)
  '''


class MojoMessager:
  def __init__(self,configfile):
    config=ConfigParser.ConfigParser()
    config.read(configfile)
    self.subskelpath=config.get("MojoMail","subskelpath")
    self.bodyskelpath=config.get("MojoMail","bodyskelpath")

  def composemessage(self,to,subdict,bodydict,payload):
    msg={}
    # First we create a title
    # Then we compose the subject
    ts=self.gettsstring()
    msg['subject']=open(self.subskelpath,"r").read().strip()
    for k,v in subdict.iteritems():
      msg['subject']=string.replace(msg['subject'],k,v)
    # And the text
    msg['text']=open(self.bodyskelpath,"r").read()
    for k,v in bodydict.iteritems():
      msg['text']=string.replace(msg['text'],k,v)
    # And finally the payload
    msg['attach']=payload
    msg['to']=to
    return msg

  def gettsstring(self):
      return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

  def getbodydict(self):
    f=open(self.bodyskelpath,"rb")
    bodydict={}
    bodykeys=[keyword for keyword in f.read().strip().split() if keyword.startswith("$")]
    for key in bodykeys:
      bodydict[key]=""
    return bodydict

  def getsubdict(self):
    f=open(self.subskelpath,"rb")
    subdict={}
    subkeys=f.read().strip().split("|")
    for key in subkeys:
      subdict[key]=""
    return subdict

  def getsubkey(self):
    f=open(self.subskelpath,"rb")
    subdict={}
    subkey=f.read().strip()
    return subkey
