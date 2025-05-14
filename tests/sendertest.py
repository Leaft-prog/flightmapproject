import socket
import time
import json
import struct
from datetime import datetime, timedelta

# Questo programma invia semplicemente dati di un volo simulato
# partendo da Trieste per finire a Parigi


group = '224.1.1.1'  # gruppo multicast
port = 5004           # porta multicast

loclong=13.4722       # Longitudine iniziale
loclat=45.8275        # Latitudine iniziale

#latitudine e longitudine del aeroporto di partenza
orlat=45.8275
orlong=13.4722

#angolazione iniziale velivolo
angle=90

#nomi dei due aeroporti
origin_name="TRS"

destination_name="CDG"

#contatori del tempo
timestampseconds=0
timestampminutes=0
timestamphours=0 
totaltime=None
#variabile per controllare la destinazione
destination=False

#distanza totale
totaldistance=0.0
#temperatura in gradi kelvin
temperature=234.15

#altitudine in metri
altitude=5000
#velocita nautica
groundspeed=40.04

#latitudine e longitudine del aeroporto di destinazione
deslat=49.009724
deslong=2.547778

#variabili per ricavare i dati del tempo
start_time_seconds = time.time()
current_time=datetime.now()
start_time=current_time.strftime("%H:%M")
arrival_time_t=current_time+timedelta(minutes=3)
arrival_time=arrival_time_t.strftime("%H:%M")
#contatore del tempo trascorso
time_passed=0



# Set the TTL (Time To Live) for multicast (2 hops)
ttl = 2
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

while True:
	#cambia la posizione del velivolo sotto determinati criteri
	if(loclong>deslong):
		loclong-=0.1
		angle=90
	if(loclong>deslong and loclat<deslat):
		loclat+=0.1
		angle=30
	
	#se arrivato a destinazione lo segno
	if(loclong<=deslong):
		destination=True
	#finche non sono a destinazione continuo ad aggiungere i KM
	if(destination==False):
		totaldistance+=11.132
	
	#se sono a destinazione invia i dati che sono fermo
	if(destination==True):
		groundspeed=0.0
		altitude=0
		
	#calcoli per il tempo trascorso
	time_passed_seconds = time.time() - start_time_seconds
	timestampseconds = int(time_passed_seconds % 60)
	timestampminutes = int((time_passed_seconds // 60) % 60)
	timestamphours = int((time_passed_seconds // 3600))
    
    #messaggio completo per il tempo trascorso
	totaltime = f"{timestamphours:02}:{timestampminutes:02}"
    
	
	#dati JSON da inviare in multicast
	MESSAGE = {
	"local-latitude": loclat,
	"local-longitude": loclong,
	"local-angle": angle,
	"local-altitude": altitude,
	"local-groundspeed": groundspeed,
	"local-temperature": temperature,
	"origin-name":origin_name,
	"origin-time":start_time,
	"origin-latitude": orlat,
	"origin-longitude": orlong,
	"destination-name": destination_name,
	"destination-time":arrival_time,
	"destination-latitude":deslat,
	"destination-longitude":deslong,
	"total-distance":totaldistance,
	"total-time":totaltime
	}
	
	#codifica JSON del messaggio
	message_bytes = json.dumps(MESSAGE).encode('utf-8')
	
	#invio del messaggio in multicast
	sock.sendto(message_bytes, (group, port))
	
	#aspetto ogni 2 secondi
	time.sleep(2)
