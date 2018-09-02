#!/usr/bin/python
#Import everything and the kitchen sink
import os, sys,string
import datetime,quopri
import ConfigParser
from mojomailGMail import MojoGMail
class MojoMailer:
  def __init__(self,configfile):
    # directory where to save attachments (default: current)
    config=ConfigParser.ConfigParser()
    config.read(configfile)
    #self.inpassword=config.get("MojoMail","inpassword")
    #self.inusername=config.get("MojoMail","inusername")
    #self.outpassword=config.get("MojoMail","outpassword")
    #self.outusername=config.get("MojoMail","outusername")
    self.name=config.get("MojoMail","name")
    self.serversig=config.get("MojoMail","serversig")
    #self.outserver=config.get("MojoMail","outserver")
    #self.inserver=config.get("MojoMail","inserver")
    #self.outport=config.get("MojoMail","outport")
    #self.inport=config.get("MojoMail","inport")
    self.logfile=config.get("MojoMail","logfile")
    self.tz=config.get("MojoMail","timezone")
    self.detach_dir=config.get("MojoMail","detach_dir")
    self.transport=config.get("MojoMail","transport")
    self.configfile=configfile
  def gettsstring(self):
      return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  def gettransport(self):
      if self.transport=="GMail":
          self.gmail=MojoGMail(self.configfile)



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
