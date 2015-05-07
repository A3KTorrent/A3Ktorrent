import bencode
import requests
import hashlib
import random
import string
from twisted.internet import reactor

PEER_ID_START = '-KB1000-'

def generate_peer_id():
				N = 20 - len(PEER_ID_START)
				end = ''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(N))   # A GENERATOR
				peer_id = PEER_ID_START + end
				return peer_id
 

def main():
	print 'KRITESH'
	f=open('book2.torrent','rb')
	s=f.read()
	data={}

	print bencode.bdecode(f.read())
	data=bencode.bdecode(s)
	print data

	print 'folder_name:',data['info']['name']


	announce=data['announce']
	print announce
		
	info = data['info']
	info_hash=hashlib.sha1(bencode.bencode(info)).digest()
	print info_hash

	port = 59696

	length=data['info']['files'][0]['length']                #files ki ek list hai!
	print length

	peer_id=generate_peer_id()
	print peer_id


	dicto = {'info_hash':info_hash, 'peer_id':generate_peer_id(), 'port':port,
										'uploaded':0,'downloaded':0, 'left':length, 
								'compact':1, 'no_peer_id':0, 'event':"started"}




	r=requests.get(announce,params=dicto)
	#xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
	response=bencode.bdecode(r.content)
	
	print response
	print '--------------------------'
	peers = response['peers']
        peer_address = ''
        peer_list = []
        for i,c in enumerate(peers):
        	print i,':',ord(c)              #ord gives ascii value of character
        	if i%6 == 4:
        		port_large = ord(c)*256
        	elif i%6 == 5:
        		port = port_large + ord(c)
        		peer_address += ':'+str(port)
        		peer_list.append(peer_address)
        		peer_address = ''
        	elif i%6 == 3:
        		peer_address += str(ord(c))
        	else:
        		peer_address += str(ord(c))+'.'
	print peer_list
	peer_list2=[]
	peer_address=''
	for i,c in enumerate(peers):
		if i%6 == 4:                     		   #This is 4th bit(starting from 0)/5th bit(starting from 1) 
			port=ord(c)*256
		elif i%6 == 5:                    #This is 5th bit(starting from 0)/6th bit(starting from 1) 
			port+=ord(c)                     #[port number=5th*256+ 6th]  (starting from 1)
			peer_address+=':'+str(port)
			peer_list2.append(peer_address)
			peer_address=''
		elif i%6 == 3:
			peer_address+=str(ord(c))          #this is the last number in adress and dats why we dont add a dot
		else:
			peer_address+=str(ord(c))+'.'

	print peer_list2
	d={}
	d['info_hash']=info_hash
	f=requests.get('http://tracker.mininova.org/scrap',params=d)
	#print f.content
	print dicto
	print bencode.bdecode(f.content)

	for peer in peer_list:
		hostandport=peer.split(':')
		reactor.connectTCP(hostandport[0],int(hostandport[1]))


	#P^L\x0bB\xc9\x01\'"\x84\xe90

		




if __name__ == '__main__':
	main()