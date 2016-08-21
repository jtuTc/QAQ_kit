#coding=utf-8
import socket
import base64
import hashlib
import select
import struct

class WebSocket:
	handle = None
	clients = []
	def __init__(self,port,numbers):
		self.handle = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		self.handle.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
		self.handle.bind(('0.0.0.0',port))
		self.handle.listen(numbers)
		self.clients.append(self.handle)

	def run(self):
		while True:
			rs,ws,es=select.select(self.clients,[],[],1)
			if len(rs):
				self.dealConnection(rs)

	def dealConnection(self,conList):
		for r in conList:
			if r is self.handle:
				con,addr=r.accept()
				hdt = con.recv(1024)
				con.send(self.upgrade(hdt))
				self.clients.append(con)
			else:
				try:
					omsg = r.recv(1024)
					if not omsg:
						self.clients.remove(r)
						continue
					recvs = self.decoding(omsg)
					#浏览器刷新/断开
					if recvs == '\x03\xe9':
						r.close()
						self.clients.remove(r)
						continue
					self.broadcast(self.encoding(recvs))
				except Exception as e:
					r.close()
					self.clients.remove(r)

	def broadcast(self,message):
		for temp in self.clients:
			if temp is not self.handle:
				temp.send(message)

	def decoding(self,data):
		if not len(data):
			return False
		datalen = ord(data[1]) & 127
		if datalen == 126:
			masks = data[4:8]
			data = data[8:]
		elif datalen == 127:
			masks = data[10:14]
			data = data[14:]
		else:
			masks = data[2:6]
			data = data[6:]
		dedata = ""
		i = 0
		for d in data:
			dedata += chr(ord(d) ^ ord(masks[i % 4]))
			i += 1
		return dedata

	def encoding(self,data):
		token = "\x81"
		length = len(data)
		if length < 126:
			token += struct.pack("B", length)
		elif length <= 0xFFFF:
			token += struct.pack("!BH", 126, length)
		else:
			token += struct.pack("!BQ", 127, length)
		data = '%s%s' % (token, data)
		return data

	def upgrade(self,headers):
		temp = headers.split("\r\n")
		key = ""
		for s in temp:
			if "Sec-WebSocket-Key" in s:
				key = s.split(":")[1]
				break

		return 'HTTP/1.1 101 Switching Protocols\r\n' \
			'Upgrade: websocket\r\n' \
			'Connection: Upgrade\r\n' \
			'Sec-WebSocket-Accept: %s\r\n\r\n'  % base64.b64encode(hashlib.sha1(key[1:] + '258EAFA5-E914-47DA-95CA-C5AB0DC85B11').digest())

	def __del__(self):
		self.handle.close()