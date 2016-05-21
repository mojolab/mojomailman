import os, sys, ConfigParser
sys.path.append("../mojomail")
from mojomail import *

if __name__=="__main__":
  e=MojoMailer("/home/mojoarjun/configs/datamail.conf")
  e.logintomail()
  m=MojoMessage("/home/mojoarjun/configs/mm-GenericMessage.conf")
  #print e.getfolderlist()
  print e.getfoldernames()
  p=e.getmessagelist(e.getfoldernames()[2],"MOJOMAIL","01-Jul-2013 00:00:00","02-Jul-2013 00:00:00")
  print p
  t=e.getmessages(p,"/home/mojoarjun/attachments")
  print t
  '''
  #print m.getsubdict()
  #print m.getbodydict()
  subdict  = {'$TYPE': 'MoFoMail', '$META': 'TESTMESSAGE', '$TIMESTAMP': '2013-07-01 00:00:00', '$IDENTIFIER': '20922', '$PAYLOAD': '/home/mojoarjun/test.csv'}
  bodydict = {'$SERVERSIG': 'Hello Buddy, This is a fucking test', '$CONTENT': 'Donkeys Balls are big and strong \n Teri maa ke naurate kabhi nahi aate', '$RECIPIENT,': 'Buddy Boy', '$TIMESTAMP': '2013-07-01 00:00:00'}
  p=m.composemessage("arjunsdarkside@gmail.com",subdict,bodydict,"/home/mojoarjun/test.csv")
  e.sendmsg(p)
  #e.sendfile("/opt/mscodes.csv","swarahldev@gmail.com")
  '''
