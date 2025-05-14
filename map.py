from tkinter import *
from PIL import Image, ImageTk
import tkintermapview
import socket
import math
import struct
import json
import time
import threading
import queue

root = Tk()
root.title("ife-map")
root.geometry("900x700")

multicast_group = '224.1.1.1' #gruppo multicast
multicast_port = 5004   #porta multicast

#i valori sono settati su None prima di ricevere i dati
locallatitude=None #latitudine dell aereo
locallongitude=None #longitudine dell aereo
originlatitude=None #latitudine del aeroporto di partenza
originlongitude=None #longitudine del aeroporto di partenza
destinationlatitude=None #latitudine del aeroporto di destinazione
destinationlongitude=None #longitudine del aeroporto di destinazione
Altitude=None #altitudine aereo (metri)
gSpeed=None #velocità (unita nautica)
tottime=None #tempo trascorso
takeoff_t=None #ora di partenza
landing_t=None #ora di arrivo
totdistance=None #total distance
temperature=None #temperatura (kelvin)
origin_name=None #nome aeroporto di partenza
destination_name=None #nome aeroporto di arrivo

enabler=False #variabile usata esclusivamente per avviare la prima volta
angle=0 #angolazione del velivolo
screen=0 #variabile sul controllo dello zoom
isfirstart=True
datareceived=False #variabile di controllo di ricezione dati

#variabili per i marker
originposition=None 
destinationposition=None
aircraftposition=None

sock=None

#quando è true mostra il messaggio di errore
errorstatus=False

#dati precedenti sulla posizione del aereo
preclatitude=None
preclongitude=None

#funzione per la ricezione dei dati in multicast dal server 
def multicast_listener():
    global locallatitude
    global locallongitude
    global originlatitude
    global originlongitude
    global destinationlatitude
    global destinationlongitude
    global angle
    global datareceived
    global sock
    global errorstatus
    global Altitude
    global gSpeed
    global temperature
    global totdistance
    global takeoff_t
    global landing_t
    global totdistance
    global tottime
    global origin_name
    global destination_name
	
	#chiudere dei sock se sono rimasti aperti in precedenza
    if sock is not None:
        sock.close()
        print("previous opened sock has been closed")

	#roba varia sulla ricezione dei dati non lo so
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', multicast_port))
    group = socket.inet_aton(multicast_group)
    mreq = struct.pack('4sL', group, socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    print("sock opened successfully")
    
    
    while True:
        try:
            print("receiving data...")
            data, _ = sock.recvfrom(1024)
            json_data = json.loads(data.decode('utf-8'))
			
			#ricezione dei dati in formato JSON
            temp_locallatitude = json_data.get("local-latitude")
            temp_locallongitude = json_data.get("local-longitude")
            temp_angle = json_data.get("local-angle")
            temp_altitude = json_data.get("local-altitude")
            temp_gspeed = json_data.get("local-groundspeed")
            temp_temperature = json_data.get("local-temperature")
            temp_takeoff_t = json_data.get("origin-time")
            temp_originlatitude = json_data.get("origin-latitude")
            temp_originlongitude = json_data.get("origin-longitude")
            temp_destinationlatitude = json_data.get("destination-latitude")
            temp_destinationlongitude = json_data.get("destination-longitude")
            temp_landing_t = json_data.get("destination-time")
            temp_totdistance = json_data.get("total-distance")
            temp_tottime= json_data.get("total-time")
            temp_origin_name = json_data.get("origin-name")
            temp_destination_name = json_data.get("destination-name")
			
			#controllo se tutti i dati ricevuti sono validi
            if all(x is not None for x in [
                temp_locallatitude, temp_locallongitude, temp_angle,
                temp_originlatitude, temp_originlongitude,
                temp_destinationlatitude, temp_destinationlongitude, temp_altitude,
                temp_gspeed, temp_temperature, temp_takeoff_t, temp_landing_t,
                temp_totdistance, temp_tottime, temp_origin_name, temp_destination_name
            ]):
				#assegnazione alle variabili definitive
                print("data successfully received")
                locallatitude = temp_locallatitude
                locallongitude = temp_locallongitude
                angle = temp_angle
                Altitude = temp_altitude
                gSpeed = temp_gspeed
                temperature = temp_temperature
                takeoff_t = temp_takeoff_t
                landing_t = temp_landing_t
                totdistance = temp_totdistance
                tottime = temp_tottime
                originlatitude = temp_originlatitude
                originlongitude = temp_originlongitude
                destinationlatitude = temp_destinationlatitude
                destinationlongitude = temp_destinationlongitude
                origin_name = temp_origin_name
                destination_name = temp_destination_name
                errorstatus=False
                datareceived=True
                #richiamo la funzione updateflightmap senza congelare la gui
                root.after(0, update_flight_map)

        except Exception as e:
            datareceived=False
            print("Error receiving data:", e)
            errorstatus = True
            break
    #chiusura del sock
    sock.close()
    print("sock closed")
	
#funzione per aggiornare la mappa
def update_flight_map():
	global locallatitude
	global locallongitude
	global originlatitude
	global originlongitude
	global destinationlatitude
	global destinationlongitude
	global preclatitude
	global preclongitude
	global aircraft_icon
	global aircraftposition
	global originposition
	global destinationposition
	global angle	
	global isfirstart
	global errorstatus
	global Altitude
	global gSpeed
	global temperature
	global totdistance
	global takeoff_t
	global landing_t
	global totdistance
	global tottime
	global enabler
	
	#controllo se i dati non sono identici ai precedenti
	if((locallatitude!=preclatitude or locallongitude!=preclongitude) or isfirstart==True):
		#controllo se i dati sono validi 
		if(locallatitude is not None and locallongitude is not None): 
			aircraft_icon_rotation = aircraft_icon_resize.rotate(angle, expand=True) #angolazione del velivolo
			aircraft_icon = ImageTk.PhotoImage(aircraft_icon_rotation) #imposto icona del marker
			
			#rimuovere il marker del velivolo se è stato piazzato in precedenza
			try:
				aircraftposition.delete()
			except:
				pass
			print("aircraft position updated")
			
			#se sono alla schermata con zoom ogni volta punto al velivolo
			if(screen==0):
				map_widget.set_position(locallatitude, locallongitude)
			
			#posiziono il velivolo attuale
			aircraftposition=map_widget.set_marker(locallatitude, locallongitude, icon=aircraft_icon)
			#assegno i dati attuali come precedenti
			preclatitude=locallatitude
			preclongitude=locallongitude
	else:
		print("aircraft position is the same, not updating")
		#uso i dati precedenti per lo zoom sul aereo
		if(screen==0):
				map_widget.set_position(preclatitude, preclongitude)
		
	#controllo se i dati sono validi
	if all(x is not None for x in [
		Altitude, gSpeed, temperature, totdistance, tottime]):
		#modifico i label dei vari dati
		data_totdistance.config(text="Total distance: "+ str(round(totdistance, 2))+"km")
		data_altitude.config(text="Altitude: "+ str(Altitude)+"m")
		data_gspeed.config(text="Ground speed: "+ str(round(gSpeed*1.852, 2))+"km/h")
		data_temperature.config(text="Temperature: "+str(round(temperature-273.15, 2))+"C")
		data_tottime.config(text="time passed since takeoff: "+tottime)
	
	#Svolgo questa operazione solo una volta alla prima ricezione
	if isfirstart==True:
		if(originlatitude is not None and originlongitude is not None): #posizione del aeroporto di partenza
			originposition=map_widget.set_marker(originlatitude, originlongitude)
			print("origin position set")
		if(destinationlatitude is not None and destinationlongitude is not None): #posizione del aeroporto di arrivo
			destinationposition=map_widget.set_marker(destinationlatitude, destinationlongitude)
			print("desination position set")
		#altri label dei dati
		if(takeoff_t is not None and landing_t is not None):
			data_takeoff_t.config(text="time at takeoff: "+takeoff_t)
			data_landing_t.config(text="time at landing: "+landing_t)
		if(origin_name is not None and destination_name is not None):
			data_airports.config(text="Origin:"+origin_name+" to "+"Destination:"+destination_name)
		#indico che la prima operazione è stata completata
		isfirstart=False
		#i dati possono essere mostrati a schermo
		enabler=True
		print("first start completed")
		
#thread per la ricezione dei dati
def receiver_thread():
	multicast_thread = threading.Thread(target=multicast_listener, daemon=True)
	multicast_thread.start()

#richiamo le funzioni principali al interno di questa funzione
def main_activity():
	
	print("starting up...")
	if isfirstart==True:
				loading_label.place(relx=0.5, rely=0.5, anchor="center")
	#richiamo il thread di ricezione dati
	threading.Thread(target=receiver_thread, daemon=True).start()
	
    #richiamo la funzione senza congelare la gui
	root.after(5000, check_status)

#cose da fare dopo la ricezione o non ricezione dei dati
def check_status():
	global errorstatus
	global datareceived
	global enabler
	
	#se i dati sono stati ricevuti
	if datareceived==True:
		#se tutto è apposto attivo la mappa e le informazioni
		if enabler==True:
			root.after(0, normal_status)
			enabler=False
		#controllo se la scritta di caricamento è presente e dopo la nascondo
		if loading_label.winfo_ismapped():
			print("loading completed")
			loading_label.place_forget()
		if not map_widget.winfo_ismapped():
			map_widget.pack(fill="both", expand=True)
		if error_label.winfo_ismapped():
			error_label.place_forget()
	else:
		#in caso di errore mostro il messaggio
		print("Unable to receive data")
		error_label.place(relx=0.5, rely=1.0, anchor="s", y=-20)
		root.after(3000, check_status)

#funzione che a ripetizione cambia la schermata della mappa o dei dati
def normal_status():
		global screen
		#mostro la mappa
		print("switching to map screen")
		mapscreen()
		#dopo 10 secondi mostro i dati di volo
		print("switching to data screen")
		root.after(10000, datascreen)
		#variabile per mettere lo zoom o meno sul velivolo
		screen+=1
		#quando raggiungo 2 ritorno a 0
		if(screen==2):
			screen=0
		#richiamo la stessa funzione cosi si ripete tutto
		root.after(20000, normal_status)

#funzione per la mappa
def mapscreen():
	global screen
	#rimuovo i label della schermata info di volo
	data_label.pack_forget()
	data_altitude.pack_forget()
	data_gspeed.pack_forget()
	data_temperature.pack_forget()
	data_totdistance.pack_forget()
	data_tottime.pack_forget()
	data_takeoff_t.pack_forget()
	data_landing_t.pack_forget()
	data_airports.pack_forget()
	
	#se la variabile è a 1 metto a zoom sul velivolo se a 0 metto lo zoom
	#sui due aeroporti di partenza e di arrivo
	if screen==1:
		map_widget.set_zoom(8)
	elif screen==0:
		map_widget.set_zoom(5)
		map_widget.fit_bounding_box((max(originlatitude, destinationlatitude), min(originlongitude, destinationlongitude)),(min(originlatitude, destinationlatitude), max(originlongitude, destinationlongitude)))
	
	#inserisco la mappa occupando tutto lo schermo
	maplabel.pack(fill="both", expand=True)
	map_widget.pack(fill="both", expand=True)
	print("map showed")
	
#mostro i dati di volo	
def datascreen(): 
	#nascondo la mappa
	map_widget.forget()
	maplabel.forget()
	print("map is hidden")
	print("data is shown")
	
	#metto le varie informazioni a schermo
	data_label.pack()
	data_altitude.pack()
	data_gspeed.pack()
	data_temperature.pack()
	data_totdistance.pack()
	data_tottime.pack()
	data_takeoff_t.pack()
	data_landing_t.pack()
	data_airports.pack()
	

	
#risorse relative alla mappa e al testo delle informazioni di volo
maplabel=LabelFrame(root)
maplabel.pack(fill="both", expand=True)

map_widget = tkintermapview.TkinterMapView(maplabel, corner_radius=0)

data_label=Label(root, text="Flight summary", font=("Arial", 30))

data_altitude = Label(root, text="", font=("Arial", 24))
data_gspeed = Label(root, text="", font=("Arial", 24))
data_temperature = Label(root, text="", font=("Arial", 24))
data_totdistance= Label(root, text="", font=("Arial", 24))
data_takeoff_t=Label(root, text="", font=("Arial", 24))
data_landing_t= Label(root, text="", font=("Arial", 24))
data_tottime=Label(root, text="", font=("Arial", 24))
data_airports=Label(root, text="", font=("Arial", 24))

error_label = Label(root, text="Flight data not available, retrying")

loading_label=Label(root, text="Retrieving flight data, please wait...")



#risorse per l'icona del aereo
aircraft_icon_path_og = Image.open("./resources/aircraft.png") 
aircraft_icon_resize = aircraft_icon_path_og.resize((50, 50))
aircraft_icon = ImageTk.PhotoImage(aircraft_icon_resize)




#quando il programma viene avviato richiamo la funzione principale
if __name__ == "__main__":
	main_activity()
	root.mainloop()
