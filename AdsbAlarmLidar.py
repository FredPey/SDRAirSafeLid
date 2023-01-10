# coding: utf-8

#!/usr/bin/env python

# Fred Peyrin (OPGC)

# 2019-04-24 AdsbAlarmLidar.py

"""
A python package for driving Laser Lidar security with ABS-D messages.
"""
import smtplib
import socket
import sys
from email.mime.text import MIMEText
from email.header import Header

import os
import datetime
import RPi.GPIO as GPIO
    
def Log(TrameAdsb, Fichier):
    # Horodatage
    Stamp= str(datetime.datetime.now())
    date_stamp = str(Stamp[0:10])
    time_stamp = str(Stamp[11:19])
    
    # Composition ligne
    ligne=(date_stamp + '\t' + time_stamp + '\t' + str(TrameAdsb) +'\n')
    
    # Archivage dans fichier
    pathSource = "/home/pi/fichier_adsb/"
    with open(str(pathSource + Fichier + '.txt'), "a") as Fichier:
         Fichier.write(ligne)

def AlarmFlag(value):
	with open('/home/pi/fichier_adsb/AlarmFlag.txt', "w") as Fichier:
		Fichier.write(value)	
         
def AlarmInitGpio():
    # initialisation sortie GPIO Raspberry
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(12, GPIO.OUT, initial = GPIO.LOW)
    GPIO.setup(16, GPIO.IN, pull_up_down = GPIO.PUD_UP) # pour contatc sec
    #GPIO.setup(16, GPIO.IN, pull_up_down = GPIO.PUD_DOWN) # pour cmde 3.3V/5V
        
def AlarmOnFile():
	if not os.path.exists ('/home/pi/fichier_adsb/Laser.stop'):
		fp = open('/home/pi/fichier_adsb/Laser.stop','w')
		fp.close()

def AlarmOffFile():
	if os.path.exists ('/home/pi/fichier_adsb/Laser.stop'):
		os.remove('/home/pi/fichier_adsb/Laser.stop')
	
def AlarmOnMail(Msg):
	#email = MIMEText('Arret Laser: ',_charset='utf-8')
	email = MIMEText('Securite Lidar : ' + str(Msg) + '\n***\n' + '(Ceci est un message automatique.)',_charset='utf-8')	
	
	email['Subject'] = Header('[COPLid // ADS-B]: ' + str(Msg))
	email['From'] = Header('Frederic Peyrin <f.peyrin@opgc.fr>')
	email['To'] = Header('Frederic Peyrin <f.peyrin@opgc.fr>')

	smtpserver = smtplib.SMTP('opgc.univ-bpclermont.fr',25)
	smtpserver.ehlo()
	smtpserver.starttls()
	smtpserver.ehlo()
	smtpserver.sendmail ('f.peyrin@opgc.fr','f.peyrin@opgc.fr',email.as_string())
	smtpserver.quit()
    
def IntruderOnGpio():
	# detection barriere IR
	return (GPIO.input(16))

def AlarmOnGpio():
    # alarme sur sortie GPIO Raspberry
    GPIO.output(12, GPIO.HIGH)
    
def AlarmOffGpio():
    # fin d'alarme du sortie GPIO Raspberry
    GPIO.output(12, GPIO.LOW)
    
def AlarmOnSocket(hote = '172.16.0.131', port = 15554, msg = u'0'):
    # Envoi d'un signal logique sur socket
    print ('---AlarmOnSocket ----------------')		

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #s.setblocking(False)
        s.settimeout(1.0)
        s.connect((hote, port))
        s.send(msg.encode())
        s.close()	
        print ('\x1b[92m' + 'Connexion avec ' + hote +" OK \x1b[39m* Proximité immediate d'un aeronef = " + str(bool(int(msg))) + ' *')
    except socket.error as msg:
		#print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
		print ('\x1b[91m' + 'PAS DE CONNEXION AVEC ' + str(hote) +' * \x1b[39m ')

    print ('---------------------------------')	
