#!/usr/bin/python
#Import everything and the kitchen sink
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

import email, getpass, imaplib, os, sys,string
import datetime,quopri
import ConfigParser
#Send out a file attached to an email
from dateutil import parser
from pytz import timezone
import base64
from bs4 import BeautifulSoup
import re
import json
sys.path.append(".")
from mojomail import *
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

def convertstringtodate(string,tz):
  fmt='%a, %d %b %Y %H:%M:%S %z (%Z)'
  t=parser.parse(string)
  p=t.astimezone(timezone(tz))
  return p

SCOPES = 'https://mail.google.com/'

class MojoGMail(MojoMailer):
    def __init__(self,*args, **kwargs):
        super(MojoGMail,self).__init__(*args, **kwargs)
        config=ConfigParser.ConfigParser()
        config.read(self.configfile)
        #print configfile
        self.logger.info("Trying to get a GMail API login")
        self.store = file.Storage(config.get("GMail","outhtoken"))
        self.creds = self.store.get()
        if not self.creds or self.creds.invalid:
            flow = client.flow_from_clientsecrets(config.get("GMail","outhfile"), SCOPES)
            self.creds = tools.run_flow(flow, store)
        self.service = build('gmail', 'v1', http=self.creds.authorize(Http()),cache_discovery=False)
        self.detach_dir=config.get("MojoMail","detach_dir")
    def get_labels(self):
        # Call the Gmail API
        self.logger("Getting labels")
        results = self.service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])
        return labels
    def get_messages_for_labels(self,labels=['INBOX','UNREAD']):
        self.logger.info("Getting messages for labels %s" %(",".join(labels)))
        user_id="me";
        response=self.service.users().messages().list(userId=user_id,labelIds=labels).execute()
        if 'messages' in response.keys():
            messages=response['messages']
        else:
            messages=[]
        #for message in messages:
        #    print message
        msgs=[]
        for mssg in messages:
            #temp_dict = { }
            message_dict={}
            m_id = mssg['id'] # get id of individual message
            message = self.service.users().messages().get(userId=user_id, id=m_id).execute() # fetch the message using API
            filename=os.path.join(self.detach_dir,"mojomail-"+m_id+".json")
            with open(filename,"w") as f:
                f.write(json.dumps(message))
            self.logger.info("Saved message meta as %s" %filename)
            message_dict['id']=m_id
            message_dict['filename']=filename
            self.service.users().messages().modify(userId=user_id, id=m_id,body={ 'removeLabelIds': ['UNREAD']}).execute()
            msgs.append(message_dict)
        return msgs
    def parse_messages(self,msgs):
        self.logger.info("Parsing messages that have already been downloaded")
        for msg in msgs:
            with open(msg['filename'],"r") as f:
                msg_json=json.loads(f.read())
            msg_meta={}
            msg_meta['snippet']=msg_json['snippet']
            msg_meta['id']=msg_json['id']
            for header in msg_json['payload']['headers']:
                if header['name']=='Subject':
                    msg_meta['subject']=header['value']
                if header['name']=="From":
                    msg_meta['from']=header['value']
            messagetextfile=msg['filename'].rstrip(".json")+".txt"
            with open(messagetextfile,"w") as f:
                f.write(json.dumps(msg_meta)+"\nENDOFHEADER\n")
            self.logger.info("Saved message text as %s" %messagetextfile)
            parts=[msg_json['payload']]
            while parts:
                part=parts.pop()
                if 'parts' in part.keys():
                    parts.extend(part['parts'])
                    #print parts
                if "filename" in part.keys():
                    if part['filename']!=u'':
                        if "data" in part['body'].keys():
                            file_data=base64.urlsafe_b64decode(part['body']['data'].encode("utf-8"))
                        elif 'attachmentId' in part['body']:
                            attachment=self.service.users().messages().attachments().get(userId="me",messageId=msg['id'],id=part['body']['attachmentId']).execute()
                            file_data=base64.urlsafe_b64decode(attachment['data'].encode("utf-8"))
                        else:
                            file_data=None
                        if file_data:
                            path=os.path.join(self.detach_dir,part['filename'])
                            with open(path,"wb") as f:
                                f.write(file_data)
                if "data" in part['body'].keys():
                    part_data=base64.urlsafe_b64decode(part['body']['data'].encode("utf-8"))
                    #print msg
                    with open(msg['filename'].rstrip(".json")+".txt","a") as f:
                            f.write(part_data+"\nENDOFPART\n")
    def create_message(self,sender, to,subject, message_text,cc=None):
        """Create a message for an email.

        Args:
        sender: Email address of the sender.
        to: Email address of the receiver.
        subject: The subject of the email message.
        message_text: The text of the email message.

        Returns:
        An object containing a base64url encoded email object.
        """
        self.logger.info("\n"+sender + ', ' + to + ', ' + subject + ', ' + message_text)
        message = MIMEText(message_text)
        message['to'] = to
        message['from'] = sender
        message['subject'] = subject
        message['cc'] = cc
        self.logger.info("Composed message: \n" + str(message))
        return {'raw': base64.urlsafe_b64encode(message.as_string())}

    def send_message(self, user_id, message_in):
        """Send an email message.

        Args:
        service: Authorized Gmail API service instance.
        user_id: User's email address. The special value "me"
        can be used to indicate the authenticated user.
        message: Message to be sent.

        Returns:
        Sent Message.
        """
        #pprint(message_in)
        try:
            message = (self.service.users().messages().send(userId=user_id, body=message_in).execute())
            self.logger.info('Message Id: %s' % message['id'])
            return message
        except errors.HttpError, error:
            self.logger.error('An error occurred: %s' % error)
