# -*- coding: utf-8 -*-

import socket, select, time

def compare_time(year, month, day, hour, minute,sec, milisec, leitura):
	if year < leitura[0:4] and month < leitura[5:7] and day < leitura[8:10] and hour < leitura[11:13] and minute < leitura[14:16] and sec < leitura[17:19] and milisec < leitura[20:]:
		return True
	return False

if __name__ == "__main__":
	
	name = ""
	#dictionary to store address corresponding to username
	
	record = {} # Conter todos os clientes (clientes e administradores)
	record2 = {} # Conter para cada cliente o ponto de interesse
	
	sensors = {} # Conter todos os sensores
	sensors_info = { } # Conter todas as info dos sensores
	sensors2 = {} # Conter todas as ultimas 10 leituras de cada sensor
	
	MAXSIZE = 10  # Tamanho máximo de leituras por sensor
	# List to keep track of socket descriptors
	connected_list = []
	buffer = 4096
	port = 5000
	
	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	server_socket.bind(("localhost", port))
	server_socket.listen(10) #listen atmost 10 connection at one time

	# Add server socket to the list of readable connections
	connected_list.append(server_socket)

	print "\33[32m \t\t\t\tSERVER WORKING \33[0m" 

	while 1:
        # Get the list sockets which are ready to be read through select
		rList,wList,error_sockets = select.select(connected_list,[],[])

		for sock in rList:
			#New connection
			if sock == server_socket:
				# Handle the case in which there is a new connection recieved through server_socket
				sockfd, addr = server_socket.accept()
				name = sockfd.recv(buffer)
				print name
				connected_list.append(sockfd)
				if name[-1]!='a' and name[-1]!='p':
					name,local,tipo,versao = name.split('|')
					if name in sensors.values():
						sockfd.send("\r\33[31m\33[1m Invalid ID!\n\33[0m")
						connected_list.remove(sockfd)
						sockfd.close()
						continue
					else:
						sensors[addr] = name
						sensors_info[name] = local + "|" + tipo + "|" + versao
						sensors2[name] = []
						print "Sensor (%s, %s) connected" % addr," [",sensors[addr],"]"
				else:		
					record[addr] = ""
					#print "record and conn list ",record,connected_list
					#if repeated username
					if name in record.values():
						sockfd.send("\r\33[31m\33[1m Username already taken!\n\33[0m")
						del record[addr]
						connected_list.remove(sockfd)
						sockfd.close()
						continue
					else:
						#add name and address
						record[addr] = name
						print "Client (%s, %s) connected" % addr," [",record[addr],"]"
						sockfd.send("\33[32m\r\33[1m Bem-Vindo ao Pollutants System. Enter 'exit' em qualquer altura para sair!\n\33[0m\n")
			#Some incoming message from a client
			else:
				# Data from client
				try:
					data1 = sock.recv(buffer)
					#print "sock is: ",sock
					data = data1[:data1.index("\n")]
					#print "\ndata received: ",data
					#print data
					
                    #get addr of client sending the message
					i,p = sock.getpeername()
					if (i,p) in record:
						if data == "exit" or data == "Exit" :
							msg="\r\33[1m" + "\33[31m " + record[(i,p)] + " left the conversation \33[0m\n"
							print "Client (%s, %s) is offline" % (i,p)," [",record[(i,p)],"]"
							del record[(i,p)]
							connected_list.remove(sock)
							sock.close()
							continue				
							
						elif data == "listar": # Listar Cliente
							data1 = sock.recv(buffer)
							data = data1[:data1.index("\n")]
							if not sensors:
								try :
									msg = "\r\33[1m"+"\33[35m Broker: "+"\33[0m"+'Nao ha sensores registados\n'
									sock.send(msg)
								except :
									# if connection not available
									sock.close()
									connected_list.remove(sock)
							else:
								msg = "\r\33[1m"+"\33[35m Broker: "+"\33[0m" + "\n"
								for x in sensors:
									if sensors_info[sensors[x]] not in msg:
										local,tipo,versao = sensors_info[sensors[x]].split('|')
										if data == tipo:
											msg += local +'; ' + "\n"
								try :
									sock.send(msg)
								except :
									# if connection not available
									sock.close()
									connected_list.remove(sock)						
									
						elif data == "sensoresListar": # Listar Admin
							if not sensors:
								try :
									msg="\r\33[1m"+"\33[35m Broker: "+"\33[0m"+'Nao ha sensores registados\n'
									sock.send(msg)
								except :
									# if connection not available
									sock.close()
									connected_list.remove(sock)
							else:
								msg = "\r\33[1m"+"\33[35m Broker: "+"\33[0m" + "\n"
								listados = []
								for x in sensors:
									if sensors[x] not in listados:
										msg += sensors[x] + '|' + sensors_info[sensors[x]] + '; ' + "\n"
										listados.append(sensors[x])
								msg = msg[:-2] + "\n"
								try :
									sock.send(msg)
								except :
									# if connection not available
									sock.close()
									connected_list.remove(sock)							
									
						elif data == "ultimaLeitura": # Ultima Leitura Admin
							data1 = sock.recv(buffer)
							data = data1[:data1.index("\n")]
							if not sensors:
								try :
									msg="\r\33[1m"+"\33[35m Broker: "+"\33[0m"+'Nao ha sensores nesse local\n'
									sock.send(msg)
								except :
									# if connection not available
									sock.close()
									connected_list.remove(sock)
							else:
								msg = "\r\33[1m"+"\33[35m Broker: "+"\33[0m" + "\n"
								for x in sensors:
									local,tipo,versao = sensors_info[sensors[x]].split('|')
									if data == sensors[x]:
										msg += sensors2[sensors[x]][len(sensors2[sensors[x]])-1] + "\n"
								try :
									sock.send(str(msg))
								except :
									# if connection not available
									sock.close()
									connected_list.remove(sock)
									
						elif data == "ultLeitura":  # Ultima Leitura Cliente
							data1 = sock.recv(buffer)
							data = data1[:data1.index("\n")]
							if not sensors:
								try :
									msg="\r\33[1m"+"\33[35m Broker: "+"\33[0m"+'Nao ha sensores nesse local\n'
									sock.send(msg)
								except :
									# if connection not available
									sock.close()
									connected_list.remove(sock)
							else:
								year = 0
								month = 0
								day = 0
								hour = 0
								minute = 0
								sec = 0
								milisec = 0
								for x in sensors:
									local,tipo,versao = sensors_info[sensors[x]].split('|')
									if data == local and compare_time(year, month, day, hour, minute, sec, milisec, sensors2[sensors[x]][len(sensors2[sensors[x]])-1]):
										msg = "\r\33[1m" + "\33[35m Broker: " + "\33[0m" + sensors2[sensors[x]][len(sensors2[sensors[x]])-1] + "\n"
								try :
									sock.send(str(msg))
								except :
									# if connection not available
									sock.close()
									connected_list.remove(sock)
								
						elif data == "sub":
							data1 = sock.recv(buffer)
							data = data1[:data1.index("\n")]
							msg = "\r\33[1m"+"\33[35m Broker: "+"\33[0m"+'\n'
							for x in sensors:
								local,tipo,versao = sensors_info[sensors[x]].split('|')
								if record[(i,p)] in record.keys():
									msg = "\r\33[1m"+"\33[35m Broker: "+"\33[0m"+'Cliente ja tem uma subscricao.\n'
								else:
									if data == local :
										record2[record[(i,p)]] = local
										msg = "\r\33[1m"+"\33[35m Broker: "+"\33[0m"+'Subscricao concluida.\n'
							try :
								sock.send(msg)
							except :
								# if connection not available
								sock.close()
								connected_list.remove(sock)
										
						elif data == "desativar":
							data1 = sock.recv(buffer)
							data = data1[:data1.index("\n")]
							if not sensors:
								try :
									msg="\r\33[1m"+"\33[35m Broker: "+"\33[0m"+'Nao ha sensors registados\n'
									sock.send(msg)
								except :
									# if connection not available
									sock.close()
									connected_list.remove(sock)
							else:
								msg="\r\33[1m"+"\33[35m Broker: "+"\33[0m"+'Nao exite sensor com esse ID.\n'
								for x in sensors:
									if sensors[x] == data:
										itersocks=iter(connected_list)
										next(itersocks)
										for sck in itersocks:
											if sck.getpeername() == x:
												sck.send("")
												sck.close()
												connected_list.remove(sck)
												y=x
												msg="\r\33[1m"+"\33[35m Broker: "+"\33[0m"+'O sensor foi desativado.\n'
								sensors2.pop(sensors[y])
								sensors_info.pop(sensors[y])
								sensors.pop(y)
								try :
									sock.send(msg)
								except :
									# if connection not available
									sock.close()
									connected_list.remove(sock)
						
						elif data == "upgrade":
							tipo_s = sock.recv(buffer)
							tipo_s = tipo_s[:tipo_s.index("\n")]
							versao_s = sock.recv(buffer)
							versao_s = versao_s[:versao_s.index("\n")]
							l = sock.recv(buffer)
							l = l.strip()
							if data == "NoFile":
								print "Cancel upgrade"
							else:
								for x in sensors:
									local,tipo,versao = sensors_info[sensors[x]].split('|')
									if tipo == tipo_s and float(versao) < float(versao_s):
										itersocks = iter(connected_list)
										next(itersocks)
										for sck in itersocks:
											if sck.getpeername() == x:
												sck.send("upgrade|" + versao_s)
												time.sleep(0.5)
												sck.send(l)
												msg="\r\33[1m" + "\33[35m Broker: " + "\33[0m" + 'Os sensores foram atualizados.\n'
												sensors_info[sensors[x]]=sensors_info[sensors[x]].replace(versao,versao_s)
								sock.send(msg)
						else:
							msg = "\r\33[1m"+"\33[35m Broker: "+"\33[0m"+'Not a valid operation.'+"\n"
							try :
								sock.send(msg)
							except :
								# if connection not available
								sock.close()
								connected_list.remove(sock)
								
					elif (i,p) in sensors:
						print data
						if data == "":
							msg="\r\33[1m"+"\33[31m "+sensors[(i,p)]+" left the conversation \33[0m\n"
							print "Client (%s, %s) is offline" % (i,p)," [",sensors[(i,p)],"]"
							del sensors[(i,p)]
							connected_list.remove(sock)
							sock.close()
							continue
						else:
							try :
								if len(sensors2[sensors[(i,p)]]) < MAXSIZE:
									sensors2[sensors[(i,p)]].append(data)
									for x in record2:
										local,tipo,versao = sensors_info[sensors[(i,p)]].split('|')
										if record2[x] == local:
											for z in record:
												if record[z] == x:
													itersocks = iter(connected_list)
													next(itersocks)
													for sck in itersocks:
														if sck.getpeername() == z:
															#\33[34m\33[1m   \33[0m
															sck.send('\n\n'+'\33[32m\33[1mSubscricao\33[0m\n' + 'Local:' + '\33[36m\33[1m %s\n\33[0m' % local + 'Tipo de poluente:' + '\33[36m\33[1m %s\n\33[0m' % tipo+data+'\n\n')
								else:
									sensors2[sensors[(i,p)]].pop(0)
									sensors2[sensors[(i,p)]].append(data)
									for x in record2:
										local,tipo,versao = sensors_info[sensors[(i,p)]].split('|')
										if record2[x] == local:
											for z in record:
												if record[z] == x:
													itersocks = iter(connected_list)
													next(itersocks)
													for sck in itersocks:
														if sck.getpeername() == z:
															#\33[34m\33[1m   \33[0m
															sck.send('\n\n\n'+'\33[32m\33[1mSubscricao\33[0m\n' + 'Local:' + '\33[36m\33[1m %s\n\33[0m' % local + 'Tipo de poluente:' + '\33[36m\33[1m %s\n\33[0m' % tipo+data+'\n\n')
							except :
								# if connection not available
								sock.close()
								connected_list.remove(sock)
                #abrupt user exit
				except:
					(i,p) = sock.getpeername()
					if (i,p) in record:
						print "Client (%s, %s) is offline (error)" % (i,p)," [",record[(i,p)],"]\n"
						del record[(i,p)]
						connected_list.remove(sock)
						sock.close()
						continue
					elif (i,p) in sensors:
						print "Sensor (%s, %s) is offline (error)" % (i,p)," [",sensors[(i,p)],"]\n"
						del sensors[(i,p)]
						del sensors_info[sensors[(i,p)]]
						connected_list.remove(sock)
						sock.close()
						continue
	server_socket.close()
