#!/usr/bin/python
#Import everything and the kitchen sink
import email, getpass, imaplib, os, sys,string
import datetime,quopri
import ConfigParser
sys.path.append("..//libs")
from email.header import decode_header
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email import Encoders
import smtplib
import logging
#Send out a file attached to an email
from dateutil import parser
from pytz import timezone

def convertstringtodate(string,tz):
  fmt='%a, %d %b %Y %H:%M:%S %z (%Z)'
  t=parser.parse(string)
  p=t.astimezone(timezone(tz))
  return p



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
    self.outserver=config.get("MojoMail","outserver")
    self.inserver=config.get("MojoMail","inserver")
    self.outport=config.get("MojoMail","outport")
    self.inport=config.get("MojoMail","inport")
    self.logfile=config.get("MojoMail","logfile")
    self.tz=config.get("MojoMail","timezone")
    self.detach_dir=config.get("MojoMail","detach_dir")

  def gettsstring(self):
      return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

  def logintoinmailIMAP(self):
    self.m = imaplib.IMAP4_SSL(self.inserver)
    self.m.login(self.inusername,self.inpassword)
    print "Logged in"

  def sendmsgSMTP(self,cmsg):
    # Wrap it all up
    msg = MIMEMultipart()
    msg['From'] = self.name
    msg['To'] = cmsg['to']
    msg['Subject'] = cmsg['subject']
    msg.attach(MIMEText(cmsg['text']))
    if cmsg['attach'] != "":
        try:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(open(cmsg['attach'], 'rb').read())
            Encoders.encode_base64(part)
            part.add_header('Content-Disposition','attachment; filename="%s"' % os.path.basename(cmsg['attach']))
            msg.attach(part)
        except:
            print  sys.exc_info()[0]
            pass
    #Connect to Server
    mailServer = smtplib.SMTP(self.outserver, self.outport)
    mailServer.ehlo()
    mailServer.starttls()
    mailServer.ehlo()
    mailServer.login(self.outusername,self.outpassword)
    mailServer.sendmail(self.outusername, cmsg['to'], msg.as_string())
    # Should be mailServer.quit(), but that crashes...
    mailServer.close()

  def getfolderlistIMAP(self):
    status,response=self.m.list() # here you a can choose a mail box like INBOX instead
    folderlist=[]
    for i in response:
      folderlist.append(i)
    return folderlist
  def getfoldernames(self):
    folderlist=self.getfolderlist()
    foldernames=[]
    for i in folderlist:
      x=i.split(' "/" ')
      foldernames.append(x[1])
    return foldernames

  def getmessagelistIMAP(self,folder,search,since,before):
    self.m.select(folder) # here you a can choose a mail box like INBOX instead
    #date = (datetime.datetime.now() - datetime.timedelta(numdays)).strftime("%d-%b-%Y %H:%M%S")
    #searchstring='(SINCE "19-May-2013 13:00:00" SUBJECT "'+search+'")'
    searchstring='(SINCE "'+since+'" BEFORE "'+before+'" SUBJECT "'+search+'")'
    print searchstring
    resp, items = self.m.search('utf-8'	, searchstring)
    messagelist= items[0].split()
    return messagelist
  def getmessageshortsIMAP(self,items):
    logging.basicConfig(filename=self.logfile, level=logging.INFO, format='%(asctime)s %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
    messageshorts=[]
    for emailid in items:
      dictionary={}
      dictionary['$UID']=emailid
      resp, data = self.m.fetch(emailid, "(RFC822.HEADER)") # fetching the mail, "`(RFC822)`" means "get the whole stuff", but you can ask for headers only, etc
      email_body = data[0][1] # getting the mail content
      #print email_body
      mail = email.message_from_string(email_body) # parsing the mail content to get a mail object
      #Check if any attachments at all
      dictionary['$FROM']=mail["From"]
      dictionary["$TO"]=mail["To"]
      dictionary["$TIMESTAMP"]=convertstringtodate(mail['Date'],self.tz)
      subject=mail["Subject"]
      dictionary['$SUBJECT']=decode_header(subject)[0][0]
      messageshorts.append(dictionary)
      logging.info("Read header " + subject)
    return messageshorts

  #def getmessages(self,search,since,subjectkey,detach_dir):
  def getmessagesIMAP(self,items,detach_dir):
    logging.basicConfig(filename=self.logfile, level=logging.INFO, format='%(asctime)s %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
    detach_dir=self.detach_dir
    messages=[]
    for emailid in items:
      dictionary={}
      print emailid
      dictionary['$UID']=emailid
      resp, data = self.m.fetch(emailid, "(RFC822)") # fetching the mail, "`(RFC822)`" means "get the whole stuff", but you can ask for headers only, etc
      email_body = data[0][1] # getting the mail content
      #print email_body
      mail = email.message_from_string(email_body) # parsing the mail content to get a mail object
      #Check if any attachments at all
      #if mail.get_content_maintype() != 'multipart':
          #continue
      print mail.keys()
      dictionary['$FROM']=mail["From"]
      dictionary["$TO"]=mail["To"]
      dictionary["$TIMESTAMP"]=convertstringtodate(mail['Date'],self.tz)
      subject=mail["Subject"]
      print subject
      dictionary['$SUBJECT']=decode_header(subject)[0][0]
      print dictionary
      for part in mail.walk():
        # multipart are just containers, so we skip them
        if part.get_content_maintype() == 'multipart':
          continue
          # is this part an attachment ?
        if part.get('Content-Disposition') is None:
          message=part.get_payload(decode=1)
          dictionary["$MESSAGE"]=message
          continue
        filename = part.get_filename()
        counter = 1
        if not filename:
            filename = 'part-%03d%s' % (counter, 'bin')
            counter += 1
        att_path = os.path.join(detach_dir, filename)
        if not os.path.isfile(att_path) :
          # finally write the stuff
          fp = open(att_path, 'wb')
          fp.write(part.get_payload(decode=True))
          fp.close()
        dictionary["$ATTACHMENT"]=att_path
      messages.append(dictionary)
      logging.info("Read message " + subject)
    return messages

  def getmailmessageIMAP(self,emailid,subjectkey,detach_dir):
      logging.basicConfig(filename=self.logfile, level=logging.INFO, format='%(asctime)s %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
      m = imaplib.IMAP4_SSL("imap.gmail.com")
      self.m.select("[Gmail]/All Mail") # here you a can choose a mail box like INBOX instead
      resp, data = self.m.fetch(emailid, "(RFC822)") # fetching the mail, "`(RFC822)`" means "get the whole stuff", but you can ask for headers only, etc
      email_body = data[0][1] # getting the mail content
      mail = email.message_from_string(email_body) # parsing the mail content to get a mail object
      #Check if any attachments at all
      if mail.get_content_maintype() != 'multipart':
          return dict(mail)
      fromaddr=mail["From"]
      subject=mail["Subject"]
      subkeys=subjectkey.split("|")
      # we use walk to create a generator so we can iterate on the parts and forget about the recursive headach
      subject= decode_header(subject)[0][0]
      subvals= subject.split("|")
      #print subkeys, subvals
      if len(subkeys)!=len(subvals):
          print "Invalid request"
          return
      else:
          dictionary={}
          for i in range(0,len(subkeys)):
            dictionary[subkeys[i]]=subvals[i]
            i+=1
      for part in mail.walk():
        # multipart are just containers, so we skip them
        if part.get_content_maintype() == 'multipart':
          continue
          # is this part an attachment ?
        if part.get('Content-Disposition') is None:
          message=part.get_payload(decode=1)
          dictionary["$MESSAGE"]=message
          continue
        filename = part.get_filename()
        counter = 1
        if not filename:
            filename = 'part-%03d%s' % (counter, 'bin')
            counter += 1
        att_path = os.path.join(detach_dir, filename)
        if not os.path.isfile(att_path) :
          # finally write the stuff
          fp = open(att_path, 'wb')
          fp.write(part.get_payload(decode=True))
          fp.close()
        dictionary["$ATTACHMENT"]=att_path
        logging.info("Read message " + subject)
        return dictionary

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
