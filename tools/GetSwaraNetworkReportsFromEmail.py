import os, sys, ConfigParser
sys.path.append("../mojomail")
from mojomail import *

if __name__=="__main__":
  e=MojoMailer("/home/mojoarjun/configs/datamail.conf")
  e.logintomail()
  m=MojoMessage("/home/mojoarjun/configs/mm-GenericMessage.conf")
  p=e.getmessages("MOJOMAIL",sys.argv[1],sys.argv[2],m.getsubkey(),sys.argv[3])
  postlist=[]
  calllist=[]
  for item in p:
    if "Post" in item['$ATTACHMENT']:
      postlist.append(item['$ATTACHMENT'])
    if "Call" in item['$ATTACHMENT']:
      calllist.append(item['$ATTACHMENT'])
  finalposts=open(sys.argv[3]+"/CallReport-"+sys.argv[1]+"-to-"+sys.argv[2]+".csv","w")
  f=open(calllist[0],"rb")
  header=f.readlines()[0]
  finalposts.write(header)
  finallines=[]
  for logfile in calllist:
    p=open(logfile,"rb")
    lines=p.readlines()
    lines.remove(lines[0])
    finallines=finallines+lines
  for line in finallines:
    #print line
    finalposts.write(line)
  finalposts.close()
    
    
  '''
  #print m.getsubdict()
  #print m.getbodydict()
  subdict  = {'$TYPE': 'MoFoMail', '$META': 'TESTMESSAGE', '$TIMESTAMP': '2013-07-01 00:00:00', '$IDENTIFIER': '20922', '$PAYLOAD': '/home/mojoarjun/test.csv'}
  bodydict = {'$SERVERSIG': 'Hello Buddy, This is a fucking test', '$CONTENT': 'Donkeys Balls are big and strong \n Teri maa ke naurate kabhi nahi aate', '$RECIPIENT,': 'Buddy Boy', '$TIMESTAMP': '2013-07-01 00:00:00'}
  p=m.composemessage("arjunsdarkside@gmail.com",subdict,bodydict,"/home/mojoarjun/test.csv")
  e.sendmsg(p)
  #e.sendfile("/opt/mscodes.csv","swarahldev@gmail.com")
  '''
