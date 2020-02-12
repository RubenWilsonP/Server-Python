# -*- coding: utf-8 -*-

import socket, select, string, time, sys, os.path
from os import path

class PublicClient(object):
	
	def __init__(self):
		self.main()
	
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
		
		print "\33[31m\33[1m BEM-VINDO Cliente! \33[0m\n"
		
		#asks for user name
		name = raw_input("\33[34m\33[1m Enter username: \33[0m")
		name += "p"
		
		print ("\n\033[93m Listar Locais segundo um poluente --> \33[0m \033[01mlistar")
		print ("\033[93m Verificar a ultima leitura num local -->\33[0m \033[01multLeitura")
		print ("\033[93m Subscrever um local de interesse -->\33[0m \033[01msub\n")
		
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
					data=msg[:msg.index("\n")]
					if data == 'listar':
						print ("Introduza o poluente a pesquisar")
						msg = sys.stdin.readline()
						s.send(msg)
					elif data == "ultLeitura":
						print ("Introduza o local a pesquisar")
						msg = sys.stdin.readline()
						s.send(msg)
					elif data == "sub":
						print ("Introduza o local de interesse para subscrever")
						msg = sys.stdin.readline()
						s.send(msg)
					self.display()

if __name__ == "__main__":
		client = PublicClient()
