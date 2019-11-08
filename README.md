# p2p-local
Local decentralized p2p network

```Node(serv_port,prot_port,name,protocol='itecnet',timer=3,**functions)```

The Node class abstracts away all low-level functionality, giving you a simple interface for a local P2P network.

#### Argument description:
- `serv_port`: Integer, the port that the Node should respond to requests on. This should not be used more than once per computer.`
- `prot_port`: Integer, the port for the Node to advertise on. This should be the same for all nodes in your network, and can be used multiple times per computer.
- `name`: String, the unique name for your Node. There should only be one Node per name on a network.
- `protocol`: String, designates what broadcasts to respond to, if multiple networks are advertising on the same port. This should be the same for every Node in a network, and you should really never have to change it.
- `timer`: Float OR Integer, represents the time between advertising attempts. The discovery loop runs on a `timer+2 second` loop.
- `**functions`: Pass any amount of keyword arguments with functions for the Node to perform. e.g. 

```def func(kwargs):
    #do something
    return value
Node(...,func1=func,...)```

Every function passed in `**functions` must accept one argument, `kwargs`, which is a dict of all arguments passed by a requesting Node.

#### Initialization:
Upon initialization, a Node will start a server instance, an advertiser, and a discovery loop on separate, non-blocking threads. It will then wait `timer+3` seconds to make sure that all other Nodes on the network have been discovered, and print a message upon completion.

#### Methods:
- `Node().request(target,function,**kwargs)`
  - 
