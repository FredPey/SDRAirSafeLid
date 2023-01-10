# coding: utf-8

#!/usr/bin/env python

# Fred Peyrin (OPGC)

# 2019-10-01 AdsLidSec_8d.py


import json
import os
import datetime as dt
import time
import socket

import AdsbAlarmLidar as aal

class AdsbCmd():
	def __init__(self):
		#__init__
		self.lat_ref = 45.7616
		self.lon_ref = 3.1108
		self.alertMsg = '*-'
		self.LastAlarmIcao = ''
		self.memoire = False
		self.ArretLaser = False
		self.alarmConnu = False
		self.alarmDist = False
		self.alarmSig = False
		self.alarmAlt = False
		self.intruder = True
		
	def onInit(self):
		
		aal.AlarmInitGpio()
		self.chemin=''
		
		# Seuils Alerte
		self.SigAlarm = -2.5	# signal critique (en dB)
		self.AltAlarm = 1000 	# altitude critique (en m)
		self.DistAlarm = 20		# distance critique (en km)
		self.SpecialIcao = ['39066C']
		self.LocalIcao = ['39AC43','39C9D5','39866D']
		self.MsgAlarm = ['\x1b[91m'+'0-ARRET-LASER-'+'\x1b[39m ','\x1b[93m'+'1-ALERTE------'+'\x1b[39m ','\x1b[92m'+'2-VIGILANCE---'+'\x1b[39m ','3-RAS---------']
		
		aal.AlarmOffFile()	
		# aal.AlarmOnMail('Securite aerienne ON')	
		aal.AlarmFlag('0')
		
	def Traitement(self):

		# Initiation Ecran
		os.system('clear')			
		
		# Acquisition Donnees
		os.chdir("/home/pi/fichier_json")
		try:
			with open ('aircraft.json','r') as fic:
				series=json.load(fic)
		except:
			print ('Erreur lors de la lecture')
			exit(1)
		
		Now = series['now']
		Maintenant = dt.datetime.fromtimestamp(int(Now))
		Datage = Maintenant.strftime('%Y%m%d')
		Horo = Maintenant.strftime('%H:%M:%S')
		
		'''
		# Barriere IR sur entree GPIO Raspberry
		# Si Intrusion 
		if aal.IntruderOnGpio():
			msg = "Detection de passage dans l'escalier"
			aal.AlarmOnGpio()
			if not(self.intruder):
				aal.AlarmOnMail(msg)
				aal.Log(str(Maintenant) + '\t' + msg , Datage + '_AlarmLog')
				self.intruder = True
		else:
			msg = 'Plateforme securisee'
			aal.AlarmOffGpio()
			if (self.intruder):
				aal.AlarmOnMail(msg)
				aal.Log(str(Maintenant) + '\t' + msg , Datage + '_AlarmLog')
				self.intruder = False	
				
		'''
		print (str(Maintenant))
		
		print ('---------------------------------')
		
		Nb = int(len(series['aircraft']))
			
		Messages=series['messages']
		print(str(Messages) + ' messages depuis le debut *** ' \
		+ str(Nb) + ' trames recues en ce moment')		
		
		print ('---------------------------------')		
		
		FichierLog = open('/home/pi/fichier_adsb/' + Datage + '_VigiLog.txt', "a")
		
		for i in range (0,Nb):
			# print Nb
			ligne=series['aircraft'][i]
			Icao=str(ligne['hex'])
			Icao=Icao.upper()
			
			try:
				Signal=ligne['rssi']
			except:
				Signal=-99.9
					
			try:
				Altitude=ligne['altitude']
				if Altitude!='ground':
					Altitude= int((0.3048 * float(Altitude)))
			except:
				Altitude=99999
							
			try:
				lat=ligne['lat']
				lon=ligne['lon']
				Distance=int((((float(lat)-float(self.lat_ref))**2+(float(lon)-float(self.lon_ref))**2)**0.5)*94)
			except:
				lat=89.999999
				lon=9.999999
				Distance=999

			# Surveillance Trafic Local
				
			if Icao in self.SpecialIcao:
				self.alertMsg = self.MsgAlarm[2]
				LigneLog = Horo + '\t' + Icao + '\t' + self.alertMsg + '\t' + 'Aeronef suivi' + '\t' + str(lat) + '\t' + str(lon) + '\t' + str(Distance)+ '\t'+ str(Signal)+ '\t'+ str(Altitude)
				print(LigneLog)
				with open ('/home/pi/fichier_adsb/' + Icao + '_SuiviLog.txt','a') as FichierSuivi:
					FichierSuivi.write(Datage + '\t' + LigneLog+'\n')
				
			if Icao in self.LocalIcao:
				self.alertMsg = self.MsgAlarm[2]
				self.alarmConnu=True
				LigneLog = Horo + '\t' + Icao + '\t' + self.alertMsg + '\t' + 'Aeronef connu' + '\t' + str(lat) + '\t' + str(lon) + '\t' + str(Distance)+ '\t'+ str(Signal)+ '\t'+ str(Altitude)
				print(LigneLog)
				FichierLog.write(LigneLog+'\n')
				
			# Surveillance Distance
				
			if Distance <= self.DistAlarm:
				self.alertMsg = self.MsgAlarm[0]
				self.alarmDist=True
				
			elif Distance > self.DistAlarm and Distance <= (2*self.DistAlarm):
				self.alertMsg = self.MsgAlarm[1]
				self.alarmDist=False
						
			elif Distance > (2*self.DistAlarm) and Distance <= (10*self.DistAlarm):
				self.alertMsg = self.MsgAlarm[2]
				self.alarmDist=False
				
			elif Distance > (10*self.DistAlarm):
				self.alertMsg=self.MsgAlarm[3]
				self.alarmDist=False		
				
			if self.alertMsg !=self.MsgAlarm[3]:
				LigneLog =  Horo +  '\t' + Icao + '\t' + self.alertMsg + '\t' + 'DIST (km):'+ '\t' + str(lat) + '\t' + str(lon) + '\t[' + str(Distance)+ ']\t'+ str(Signal)+ '\t'+ str(Altitude)
				print(LigneLog)
				FichierLog.write(LigneLog+'\n')

			# Surveillance Force Signal 
			
			if Signal >= self.SigAlarm:
				self.alertMsg = self.MsgAlarm[0]
				self.alarmSig=True
				
			elif Signal >=(5*self.SigAlarm) and (Signal < self.SigAlarm):
				self.alertMsg = self.MsgAlarm[1]
				self.alarmSig=False
				
			elif Signal >=(10* self.SigAlarm) and Signal <(5* self.SigAlarm):
				self.alertMsg = self.MsgAlarm[2]
				self.alarmSig=False
				
			elif Signal <(10* self.SigAlarm):
				self.alertMsg=self.MsgAlarm[3]	
				self.alarmSig=False
				
			if self.alertMsg !=self.MsgAlarm[3]:
				LigneLog =  Horo +  '\t' + Icao + '\t' + self.alertMsg + '\t' + 'SIGN (dB):'+ '\t' + str(lat) + '\t' + str(lon) + '\t' + str(Distance)+ '\t['+ str(Signal)+ ']\t'+ str(Altitude)
				print(LigneLog)
				FichierLog.write(LigneLog+'\n')

			# Surveillance Altitude
			
			if Altitude=='ground':
				self.alertMsg=self.MsgAlarm[2]
				self.alarmAlt=True				
				LigneLog =  Horo +  '\t' + Icao + '\t' + self.alertMsg + '\t' + ' Au sol!'+ '\t' + str(lat) + '\t' + str(lon) + '\t' + str(Distance)+ '\t'+ str(Signal)+ '\t['+ str(Altitude)+']'
				FichierLog.write(LigneLog+'\n')		
				
			elif Altitude<0:
				self.alertMsg=self.MsgAlarm[3]
				self.alarmAlt=False
				LigneLog =  Horo +  '\t' + Icao + '\t' + self.alertMsg + '\t' + ' Erreur Altitude!'+ '\t' + str(lat) + '\t' + str(lon) + '\t' + str(Distance)+ '\t'+ str(Signal)+ '\t['+ str(Altitude)+']'
				FichierLog.write(LigneLog+'\n')		
				
			elif Altitude < self.AltAlarm:
				self.alertMsg=self.MsgAlarm[3]		
				self.alarmAlt=False
				
			elif Altitude <(5*self.AltAlarm) and Altitude >= self.AltAlarm:
				self.alertMsg=self.MsgAlarm[3]
				self.alarmAlt=False	
				
			elif Altitude >=(5* self.AltAlarm):
				self.alertMsg=self.MsgAlarm[3]	
				self.alarmAlt=False				
				
			if self.alertMsg !=self.MsgAlarm[3]:
				LigneLog =  Horo + '\t' + Icao + '\t' + self.alertMsg + '\t' + 'ALTI  (m):'+ '\t' + str(lat) + '\t' + str(lon) + '\t' + str(Distance)+ '\t'+ str(Signal)+ '\t['+ str(Altitude)+']'
				print(LigneLog)
				FichierLog.write(LigneLog+'\n')

			Condition0 = self.alarmAlt
			Condition1 = self.alarmDist
			Condition2 = self.alarmSig
			Condition3 = self.alarmConnu
			
			Condition4 = self.alarmDist and (not(self.alarmAlt))
			Condition5 = self.alarmSig and (not(self.alarmAlt))
					
			Conditions = not(Condition0) and (Condition1 or Condition2)
				
			if Conditions == True:
				
				'''print ('-------------------------')	
				print ('Alertes primaires')
				print ('-------------------------')	
				print ('Distance  < '+str(DistAlarm)+'km', self.alarmDist)
				print ('Signal    > '+str(SigAlarm)+'dB',self.alarmSig)
				print ('-------------------------')	
				print ('Alertes secondaires')
				print ('-------------------------')	
				print ('Avion connu:',self.alarmConnu)				
				print ('Altitude  < '+str(AltAlarm)+'m',self.alarmAlt)
				print ('-------------------------')	
				print ('Alarme logique')
				print ('-------------------------')	
				print (Icao,'Laser OFF :',self.alarm)	'''			
				msglog=str(Maintenant) + '\t' + str(Icao) + '\t' + str(int(Condition1)) + '\t'+str(int(Condition2)) + '\t' + str(int(Condition4)) + '\t' + str(int(Condition5))
				aal.Log(msglog , Datage + '_AlarmLog')
				
				#os.rename('aircraft.json', str(Maintenant.strftime('%Y%m%d%H%M%S'))+'aircraft.json')
				
				self.ArretLaser=True
				self.LastAlarmIcao = str(Icao)
				aal.AlarmOnSocket(hote = '172.16.0.131', port = 15554, msg = u'1')
						
				aal.AlarmOnGpio()	
				aal.AlarmOnFile()		
				aal.AlarmFlag('1')
				self.memoire = self.ArretLaser
				
			self.alarmConnu=False
			self.alarmDist=False
			self.alarmSig=False
			self.alarmAlt=False	

		if (self.ArretLaser) and not(self.memoire):
			#aal.AlarmOnMail(self.LastAlarmIcao + ' Stop_Laser')
			self.memoire = self.ArretLaser
				
		if not(self.ArretLaser) and self.memoire:
			aal.AlarmOffGpio()
			aal.AlarmOffFile()
			#aal.AlarmOnMail(self.LastAlarmIcao +' ReStart_Laser')	
			aal.AlarmFlag('0')
			aal.AlarmOnSocket(hote = '172.16.0.131', port = 15554, msg = u'0')
			self.memoire = self.ArretLaser

		if not(self.ArretLaser) and not(self.memoire):
			aal.AlarmOnSocket(hote = '172.16.0.131', port = 15554, msg = u'0')
			self.memoire = self.ArretLaser

		FichierLog.close()

		self.ArretLaser=False
		self.alarmConnu=False
		self.alarmDist=False
		self.alarmSig=False
		self.alarmAlt=False	

		time.sleep(1)
     
if __name__ == "__main__":
	myAdsb=AdsbCmd()
	
	myAdsb.onInit()
	    
	while True:
		myAdsb.Traitement()

