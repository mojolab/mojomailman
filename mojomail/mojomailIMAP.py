from __future__ import unicode_literals
from imapclient import IMAPClient
import email
from email.header import decode_header
class MojoMailer:
  def __init__(self,configfile):
    # directory where to save attachments (default: current)
    config=ConfigParser.ConfigParser()
    config.read(configfile)
    self.inpassword=config.get("System","inpassword")
    self.inusername=config.get("System","inusername")
    self.outpassword=config.get("System","outpassword")
    self.outusername=config.get("System","outusername")
    self.name=config.get("System","name")
    self.serversig=config.get("System","serversig")
    self.outserver=config.get("System","outserver")
    self.inserver=config.get("System","inserver")
    self.outport=config.get("System","outport")
    self.inport=config.get("System","inport")
    self.logfile=config.get("System","logfile")
  def downloadmessages(self,messages,detach_dir):
    messagelist=[]
    for message in messages:
      dictionary={}
      response = server.fetch(message, ['RFC822','FLAGS', 'RFC822.HEADER'])
      mail=email.message_from_string(response[message]['RFC822'])
      #Check if any attachments at all
      if mail.get_content_maintype() != 'multipart':
        continue
      fromaddr=mail["From"]
      subject=mail["Subject"]
      # we use walk to create a generator so we can iterate on the parts and forget about the recursive headach
      subject= decode_header(subject)[0][0]
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
        dictionary["$ATTACHMENT"+str(counter)]=att_path
      messagelist.append(dictionary)
      logging.info("Read message " + subject)
    return messagelist





