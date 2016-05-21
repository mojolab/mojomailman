#!/usr/bin/python
#Import everything and the kitchen sink
import email, getpass, imaplib, os, sys
import datetime,quopri
sys.path.append("..//libs")
from database import *
from utilities import *
from email.header import decode_header

# directory where to save attachments (default: current)
detach_dir = '/opt/swara/sounds/rcvd' 
config=ConfigParser.ConfigParser()
config.read("/etc/swara.conf")
USERNAME = config.get("System","inboundgmail")
PASSWORD = config.get("System","inboundgmailpw")
SERVERNAME = config.get("System","servername")
NUMBER = config.get("System","phonenum")
user = USERNAME
pwd = PASSWORD

# Open up a link to Mr Database
db = Database()	 
		
# connecting to the gmail imap server
if __name__ == '__main__':
    # Get current STR Messages on email
    m = imaplib.IMAP4_SSL("imap.gmail.com")
    m.login(user,pwd)
    print "Logged in"
    #print m.list()
    m.select("[Gmail]/All Mail") # here you a can choose a mail box like INBOX instead
    # use m.list() to get all the mailboxes
    date = (datetime.date.today() - datetime.timedelta(int(sys.argv[1]))).strftime("%d-%b-%Y")
    searchstring='(SINCE "'+date+'" SUBJECT "Swara")'
    #print searchstring
    #resp, items = m.search(None, "ALL") # you could filter using the IMAP rules here (check http://www.example-code.com/csharp/imap-search-critera.asp)
    resp, items = m.search('utf-8'	, searchstring) # you could filter using the IMAP rules here (check http://www.example-code.com/csharp/imap-search-critera.asp)
    items = items[0].split() # getting the mails id
    for emailid in items:
        resp, data = m.fetch(emailid, "(RFC822)") # fetching the mail, "`(RFC822)`" means "get the whole stuff", but you can ask for headers only, etc
        email_body = data[0][1] # getting the mail content
        mail = email.message_from_string(email_body) # parsing the mail content to get a mail object
        #Check if any attachments at all
        if mail.get_content_maintype() != 'multipart':
            continue
        fromaddr=mail["From"]
        subject=mail["Subject"]
        # we use walk to create a generator so we can iterate on the parts and forget about the recursive headach
        subject= decode_header(subject)[0][0]
        title=subject.split(']')[1]
        metadata=subject.split(']')[0].split('[')[1].split('|')
	servername=metadata[0]
	postid=metadata[1]
	command=metadata[2]
	if len(metadata)>3:
	    user=metadata[3]
	    location=metadata[4]
	    timestamp=metadata[5]
	else:
	    user="UNKNOWN"
	    location="UNKNOWN"
	    timestamp="UNKNOWN"
	statefile=open("../conf/states","r").readlines()
        statenums={}
	for line in statefile:
	    statenums[line.strip().split(',')[1]]=line.strip().split(',')[0]
	if statenums[command]:
	    state=statenums[command]
	else:
	    state=1
        
	for part in mail.walk():
            # multipart are just containers, so we skip them
            if part.get_content_maintype() == 'multipart':
                continue
            # is this part an attachment ?
            if part.get('Content-Disposition') is None:
                message=part.get_payload(decode=1)
                continue
            filename = part.get_filename()
            counter = 1
            if not filename:
                filename = 'part-%03d%s' % (counter, 'bin')
                counter += 1
	    if servername==SERVERNAME:
                postid=filename.split(".")[0]
            else:
                auth=db.getAuthDetails(user)
		if auth == 0:
		    auth=db.addAuthor(user)
		postid = db.addCommentToChannel(user, auth,'12345')
		extension=filename.split(".")[1]
		filename=str(postid)+"."+extension
            # if there is no filename, we create one with a counter to avoid duplicates
            att_path = os.path.join(detach_dir, filename)
            os.system("cp %s %s.orig" %(att_path, att_path))
            os.system("rm %s " %(att_path))
            timestamp=datetime.date.today().strftime("%d-%b-%Y")
            os.system("cp /opt/swara/sounds/%s.wav /opt/swara/sounds/original/%s.wav.%s" %(postid,postid,timestamp))
            os.system("/usr/local/bin/lame %s --decode /opt/swara/sounds/%s.wav" %(att_path,postid))		
            os.system("cp %s /opt/swara/sounds/web" %(att_path))
            
            #Check if its already there
            if not os.path.isfile(att_path) :
                # finally write the stuff
                fp = open(att_path, 'wb')
                fp.write(part.get_payload(decode=True))
                fp.close()
            timestamp=datetime.date.today().strftime("%d-%b-%Y")
            os.system("cp /opt/swara/sounds/%s.wav /opt/swara/sounds/original/%s.wav.%s" %(postid,postid,timestamp))
            os.system("/usr/bin/lame %s --decode /opt/swara/sounds/%s.wav" %(att_path,postid))		
            os.system("cp %s /opt/swara/sounds/web" %(att_path))
	    
            subject=title.replace("\n","<br>")
            text=message.replace("\n","<br>")
            text=message.replace("\r","<br>")
            db.updatePost(postid,subject,text)
	    auth=db.getAuthDetails(user)
	    if auth == 0:
		auth=db.addAuthor(user)
            db.updateAuthor(auth,postid)
	    db.updateUser(user,postid)
	    db.changePostState(postid,str(state))
            #print emailid
            #m.store(emailid,"+FLAGS",'\\Deleted')
	    
            m.store(emailid,'+X-GM-LABELS', '\\Trash')
            m.expunge()
