# -*- coding: utf-8 -*-

import socket, select, string, time, sys, os.path
from os import path

class Admin(object):
	
	def __init__(self):
		self.main()
	
#Helper function (formatting)
	def display(self) :
		you="\33[33m\33[1m"+" You: "+"\33[0m"
		sys.stdout.write(you)
		sys.stdout.flush()
	
	def main(self):

		if len(sys.argv)<2:
			host = '0.0.0.0'
		else:
			host = sys.argv[1]

		port = 5000
		
		print "\33[31m\33[1m BEM-VINDO Administrador! \33[0m\n"

		name = raw_input("\33[34m\33[1m Enter username: \33[0m")
		name += "a"
		
		print ("\n\033[93m Verificar ultima leitura de um sensor -->\33[0m \033[01multimaLeitura")
		print ("\033[93m Listar todos os sensores existentes --> \33[0m \033[01msensoresListar")
		print ("\033[93m Desactivar um determinado sensor  -->\33[0m \033[01mdesativar")
		print ("\033[93m Fazer upgrade a um sensor -->\33[0m \033[01mupgrade\n")
		
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.settimeout(2)
		
		# connecting host
		try :
			s.connect((host, port))
		except :
			print "\33[31m\33[1m Can't connect to the server \33[0m"
			sys.exit()

		#if connected
		s.send(name)
		self.display()
		while 1:
			socket_list = [sys.stdin, s]
			
			# Get the list of sockets which are readable
			rList, wList, error_list = select.select(socket_list , [], [])
			
			for sock in rList:
				#incoming message from server
				if sock == s:
					data = sock.recv(4096)
					if not data :
						print '\33[31m\33[1m \rDISCONNECTED!!\n \33[0m'
						sys.exit()
					else :
						sys.stdout.write(data)
						self.display()
			
				#user entered a message
				else :
					msg = sys.stdin.readline()
					s.send(msg)
					data = msg[:msg.index("\n")]
					if data == "ultimaLeitura":
						print ("Introduza o ID do sensor -->")
						msg = sys.stdin.readline()
						s.send(msg)
					elif data == "sensorsListar":
						s.send(msg)
					elif data == "desativar":
						print ("Introduza o ID do sensor -->")
						msg = sys.stdin.readline()
						s.send(msg)
					elif data == "upgrade":
						print ("Introduza o tipo de sensor a atualizar -->")
						tipo = sys.stdin.readline()
						s.send(tipo)
						print ("Introduza o id versao atualizada -->")
						versao = sys.stdin.readline()
						s.send(versao)
						tipo=tipo[:tipo.index("\n")]
						versao=versao[:versao.index("\n")]
						if path.exists(tipo+'_'+versao+'.txt'):
							time.sleep(0.5)
							f = open(tipo+'_'+versao+'.txt', "rt")
							s.send(f.read()+"\n")
							f.close()
						else:
							msg = "NoFile"
							s.send(msg)
					self.display()

if __name__ == "__main__":
		client = Admin()

