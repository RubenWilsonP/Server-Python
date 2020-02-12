# -*- coding: utf-8 -*-

import time, socket, select, string, sys, threading, random
from datetime import datetime
        
class Sensor:
	
	def connect(self):
		if len(sys.argv)<2:
			host = '0.0.0.0'
		else:
			host = sys.argv[1]

		port = 5000
		buffer = 4096
		t = 10.0

		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.settimeout(2)
		
		# connecting host
		try :
			s.connect((host, port))
		except :
			print "\33[31m\33[1m Can't connect to the server \33[0m"
			sys.exit()

		#if connected
		s.send(str(self.id) + '|' + str(self.local) + '|' + str(self.tipo) + '|' + str(self.versao))
		
		time.sleep(1)
		t1=threading.Thread(target=self.envioPeriodico,kwargs=dict(sock=s))
		t1.setDaemon(True)
		t1.start()
		
		while 1:
			
			socket_list = [sys.stdin, s]
			
			# Get the list of sockets which are readable
			rList, wList, error_list = select.select(socket_list , [], [])
			
			for sock in rList:
				#incoming message from server
				if sock == s:
					data = sock.recv(buffer)
					if not data :
						print '\33[31m\33[1m \rDISCONNECTED!!\n \33[0m'
						sys.exit()
					else :
						if data[:data.index("|")] == "upgrade":
							self.versao = float(data[data.index("|")+1:])
							f = open(self.tipo+'_'+str(self.versao)+'T.txt', "wt")
							l = sock.recv(buffer)
							l = l.strip()
							f.write(l)
							f.close()
							print '\33[32m\33[1mUpdate!\33[0m\n' + 'O firmware foi atualizado para a versao: ' + str(self.versao)
						else:
							sys.stdout.write(data)
				#user entered a message
				else :
					msg = sys.stdin.readline()
					s.send(msg)

	def envioPeriodico(self, sock):
		msg = str(datetime.now()) + " | " + str((random.randint(0,20))) + " µg/m³" +  " | " + str(self.versao) + "\n"
		sock.send(msg)
		while 1:
			time.sleep(10)
			msg = str(datetime.now()) + " | " + str((random.randint(0,20))) + " µg/m³" +  " | " + str(self.versao) + "\n"
			sock.send(msg)
	
	def __init__(self, ID, tipo, local, v): 
		self.id = ID
		self.tipo = tipo
		self.local = local
		self.versao = float(v)
	
	@classmethod
	def from_input(cls):
		return cls(int(raw_input('id: ')),raw_input('tipo: '), raw_input('local: '),raw_input('versao: '))

if __name__ == "__main__":
	sensor = Sensor.from_input()
	sensor.connect()
