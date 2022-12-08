import smtplib
from email.mime.text import MIMEText
import imaplib
import DHT11 as DHT
import RPi.GPIO as GPIO

DHTPin = 21
ledPin = 20

GPIO.cleanup()

GPIO.setmode(GPIO.BCM)
dht = DHT.DHT(DHTPin)
dht.readDHT11()

def updateDHT():
    dht.readDHT11()     #read DHT11 and get a return value. Then determine whether data read is normal according to the return value.

GPIO.setup(ledPin, GPIO.OUT)


motor_is_on = False
motor1 = 5
motor2 = 22
motor3 = 26
GPIO.setup(motor1, GPIO.OUT)
GPIO.setup(motor2, GPIO.OUT)
GPIO.setup(motor3, GPIO.OUT)
GPIO.output(motor2, True)
GPIO.output(motor3, False)

def getMotorStatus():
    return motor_is_on

def setMotor(status):
    global motor_is_on
    GPIO.output(motor1, status)
    motor_is_on = status

def setLED(status):
    if status:
        GPIO.output(ledPin, True)
    else: 
        GPIO.output(ledPin, False)

# imap setup
print("connecting to imap")
mailserver = imaplib.IMAP4_SSL('192.168.0.11', 993)
username = '2044092@iotvanier.com'
password = '2044092'
mailserver.login('2069941@iotvanier.com', '2069941')

# smtp setup
print('Connecting to SMTP server...')
server = smtplib.SMTP('192.168.0.11', 587)
sender_username = '2069941@iotvanier.com'
sender_password = '2069941'
server.starttls()
server.login(sender_username, sender_password)
print('Connected\n')

def sendMail(recipient, subject, message):
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = '2069941@iotvanier.com'
    msg['To'] = recipient

    server.sendmail('2069941@iotvanier.com', recipient, msg.as_string())
    print('mail sent\n')

def getResponse():
    status, count = mailserver.select('Inbox')
    print(count)
    status, data = mailserver.fetch(count[0], '(UID BODY[TEXT])')
    response = str(data[0][1])
    is_on = False

    if "YES" in response.upper():
        is_on = True
        print("Found 'YES' Turn on the Motor")
        setMotor(True)
        mailserver.select('Inbox')
        typ, data = mailserver.search(None, 'ALL')
        for num in data[0].split():
            mailserver.store(num, '+FLAGS', '\\Deleted')
        mailserver.expunge()
        sendMail('2069941@iotvanier.com', '', '')
    else:
        print ('notfound')
    
    return is_on