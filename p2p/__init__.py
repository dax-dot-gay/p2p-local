import xmlrpc.client as client
import xmlrpc.server as server
from threading import Thread
from time import sleep, time, ctime
from socket import *

class Server:
    def __init__(self,port,functions,inst=None,log=False):
        self.server = server.SimpleXMLRPCServer(('localhost',port),logRequests=log)
        for i in functions.keys():
            self.server.register_function(functions[i],i)
        if inst:
            self.server.register_instance(inst)
        self.server.register_introspection_functions()
    def start(self):
        self.thread = Thread(name='Server-instance',target=self.server.serve_forever)
        self.thread.start()
    def stop(self):
        self.server.shutdown()
        self.thread.join()

class Advertiser:
    def __init__(self,name,server_port,port=10000,prot='itecnet',timer=3):
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.socket.bind(('', 0))
        self.socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        self.ip = gethostbyname(gethostname())
        self.name = name
        self.prot = prot
        self.running = False
        self.timer = timer
        self.port = port
        self.sport = server_port

    def _start(self):
        self.running = True
        while self.running:
            data = self.prot+'|'+self.name+'|'+self.ip+':'+str(self.sport)
            self.socket.sendto(bytes(data,'utf-8'), ('<broadcast>', self.port))
            sleep(self.timer)
        self.socket.close()
    
    def start(self):
        self.thread = Thread(name='Advertiser-Instance',target=self._start)
        self.thread.start()

    def stop(self):
        self.running = False

class Node:
    def __init__(self,serv_port,prot_port,name,protocol='itecnet',timer=3,inst=None,**functions):
        self.timer = timer
        self.advertiser = Advertiser(name,serv_port,port=prot_port,timer=self.timer,prot=protocol)
        self.server = Server(serv_port,functions,inst=inst)
        self.advertiser.start()
        self.server.start()
        self.protocol = protocol
        self.ports = [serv_port,prot_port]
        self.targets = {}
        self.discoverer = Thread(name='Discoverer',target=self.discoverloop)
        self.discoverer.start()
        sleep(timer+3)
        print('Finished init of node '+name)

    def discover(self,name=None,timeout=5):
        s = socket(AF_INET, SOCK_DGRAM) #create UDP socket
        s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        s.bind(('', self.ports[1]))
        curtime = time()
        ret = {}
        while time() < curtime+timeout:
            data, addr = s.recvfrom(1024) #wait for a packet
            data = str(data)[2:].strip("'")
            if data.startswith(self.protocol):
                data = data.split('|')
                if data[1] != self.advertiser.name:
                    ret[data[1]] = data[2]
        
        if name:
            try:
                return ret[name]
            except KeyError:
                raise KeyError(name+' is not broadcasting.')
        else:
            return ret

    def discoverloop(self):
        self.discovering = True
        while self.discovering:
            new = self.discover(timeout=self.timer+2)
            self.targets = new

    def shutdown(self):
        self.discovering = False
        self.discoverer.join()
        self.server.stop()
        self.advertiser.stop()

    def request(self,target,function,**kwargs):
        try:
            target = self.targets[target].split(':')
            if target[0] == gethostbyname(gethostname()):
                target[0] = 'localhost'
            target = 'http://'+':'.join(target)+'/'
        except KeyError:
            raise ValueError('Target not found.')
        with client.ServerProxy(target,use_builtin_types=True) as cli:
            return getattr(cli,function)(kwargs)
    
    def getmethods(self,target):
        try:
            target = self.targets[target].split(':')
            if target[0] == gethostbyname(gethostname()):
                target[0] = 'localhost'
            target = 'http://'+':'.join(target)+'/'
        except KeyError:
            raise ValueError('Target not found.')
        with client.ServerProxy(target,use_builtin_types=True) as cli:
            return cli.system.listMethods()
        

#test

'''def echo(kwargs):
    return 'Echoed ' + kwargs['e'] + ' at ' + str(ctime())

n1 = Node(2000,2001,'node1',echo=echo)
n2 = Node(2002,2001,'node2')

print(n2.targets)
print(n2.getmethods('node1'))
while True:
    print(n2.request('node1','echo',e='TEST'))'''
