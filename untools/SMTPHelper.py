#coding:utf-8
import socket
import base64
class SMTPHelper:
	_username = ""
	_bun = ""
	_bpw = ""
	_domain = ""
	_port = ""
	_socket = None
	_timeout = 5
	def __init__(self,domain,port,username,password):
		self._domain = domain
		self._port = port
		self._username = username
		self._bun = base64.b64encode(username)
		self._bpw = base64.b64encode(password)
		self._socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		self._socket.settimeout(self._timeout)

	def connect(self):
		self._socket.connect((self._domain,self._port))
		recv = self._socket.recv(1024)
		if recv[0:3] == "220":
			return True
		return recv;

	def query(self,query):
		self._socket.send(query+"\r\n")
		return self._socket.recv(1024)

	def login(self):
		recv = self.query("EHLO %s" % self._domain)
		if recv[0:3] != "250":
			return recv
		recv = self.query("AUTH LOGIN")
		if recv[0:3] != "334":
			return recv
		recv = self.query(self._bun)
		if recv[0:3] != "334":
			return recv
		recv = self.query(self._bpw)
		if recv[0:3] != "235":
			return recv
		return True

	def preSend(self,to):
		recv = self.query("MAIL FROM:<%s>" % self._username)
		if recv[0:3] != "250":
			return recv
		recv = self.query("RCPT TO:<%s>" % to)
		if recv[0:3] != "250":
			return recv
		recv = self.query("DATA")
		if recv[0:3] != "354":
			return recv
		return True

	def sendMail(self,to,nick,title,body):
		recv = self.connect()
		if recv != True:
			return recv
		recv = self.login()
		if recv != True:
			return recv
		recv = self.preSend(to)
		if recv != True:
			return recv
		content = "FROM:%s <%s>\r\nTO:<%s>\r\nSUBJECT:%s\r\n\r\n%s\r\n.\r\n" % (nick,self._username,to,title,body)
		recv = self.query(content)
		if recv[0:3] != "250":
			return recv
		return True

	def sendHtmlMail(self,to,nick,title,body):
		recv = self.connect()
		if recv != True:
			return recv
		recv = self.login()
		if recv != True:
			return recv
		recv = self.preSend(to)
		if recv != True:
			return recv
		content = "FROM:%s <%s>\r\nTO:<%s>\r\nSUBJECT:%s\r\nContent-Type:text/html; charset=utf-8\r\n\r\n%s\r\n.\r\n" % (nick,self._username,to,title,body)
		recv = self.query(content)
		if recv[0:3] != "250":
			return recv
		return True

	def __del__(self):
		self._socket.close()