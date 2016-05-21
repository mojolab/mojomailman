#!/usr/bin/python

#Import everything and the kitchen sink
import os,sys,time,string
sys.path.append("../libs")
from database import *
from utilities import *
import ConfigParser
import oauth2 as oauth
import os,sys
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email import Encoders


# Get the gyaan from the config file, the server specifics
config=ConfigParser.ConfigParser()
config.read("/etc/swara.conf")

# Set up the variables for later
USERNAME = config.get("System","outboundgmail")
PASSWORD = config.get("System","outboundgmailpw")
SERVERNAME = config.get("System","servername")
NUMBER = config.get("System","phonenum")
gmail_user = USERNAME
gmail_pwd =  PASSWORD

# Open up a connection with Mr Database
db = Database()	 

#Get the last post we pushed out...there MUST be a more elegant way
#of doing this that doesnt involve a database change
def getLastPushedPostID():
	post=os.popen("cat lastemailedpost").read().strip()
	return post

#Send out a post as an email
def mail(post,to):
	# First we get the title for the subject
	title=db.getTitleforPost(12345,post)[:120]
	title=title.replace("&#039;","'")
	# Then we get the state of the post
	statenum=db.getStateforPost(12345,post)
	# And change it to human readable format
	statefile=open("../conf/states","r").readlines()
	states={}
	for line in statefile:
		states[line.strip().split(',')[0]]=line.strip().split(',')[1]
	if states[str(statenum)]:
		state=states[str(statenum)]
	else:
		state=str(statenum)
		
	# Next we get the content 
	content=str(db.getMessageforPost(12345,post)[0])
	content=content.replace("&#039;","'")
	content=content.replace("<br>","\n")
	
	# And also the name of the whodunnit
	user=str(db.getUserforPost(12345,post)[0])
	# And when did they do this deed
	timestamp=str(db.getPostedTime(12345,post))
        
	# Then we compose the subject
	subject=open("../conf/subject.skel","r").read().strip()
	subject=string.replace(subject,"SERVERNAME",SERVERNAME)
	subject=string.replace(subject,"POSTID",str(post))
	subject=string.replace(subject,"STATE",state)
	subject=string.replace(subject,"USER",user)
	subject=string.replace(subject,"TIMESTAMP",timestamp)
	subject=string.replace(subject,"TITLE",title)
	
	# And the text
	text=open("../conf/email.skel","r").read()
	text=string.replace(text,"NUMBER",NUMBER)
	text=string.replace(text,"TIMESTAMP",timestamp)
	text=string.replace(text,"CONTENT",content)
	text=string.replace(text,"USER",user)
	
	# And finally the payload
	attach='/opt/swara/sounds/web/'+str(post)+'.mp3'
	
	# Wrap it all up
	msg = MIMEMultipart()
	msg['From'] = SERVERNAME
	msg['To'] = to
	msg['Subject'] = subject
	msg.attach(MIMEText(text))
	if attach != "":
		try:
			part = MIMEBase('application', 'octet-stream')
			part.set_payload(open(attach, 'rb').read())
			Encoders.encode_base64(part)
			part.add_header('Content-Disposition','attachment; filename="%s"' % os.path.basename(attach))
			msg.attach(part)
		except:
			print  sys.exc_info()[0]
			pass
	#Connect to Server
	mailServer = smtplib.SMTP("smtp.gmail.com", 587)
	mailServer.ehlo()
	mailServer.starttls()
	mailServer.ehlo()
	mailServer.login(gmail_user, gmail_pwd)
	mailServer.sendmail(gmail_user, to, msg.as_string())
	# Should be mailServer.quit(), but that crashes...
	mailServer.close()


if __name__=="__main__":
	#Create Database object
	postid=getLastPushedPostID() 
	print postid
	pid=int(postid)
	while db.getPostedTime(12345,pid)==None:
		pid-=1
	postid=str(pid)
	print postid 
	posts=db.getAllUnpushedPostsInChannel(12345,postid)
	if len(posts) == 0:
		print "No unexported posts"
		exit()
	for post in posts:
		mail(post,USERNAME)
		os.system("echo %s > lastemailedpost" %(str(post)))
	print "Final post = " + str(post)
	
