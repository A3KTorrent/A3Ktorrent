import bencode
import hashlib
import random
import string

PEER_ID_START = '-KB1000-' #for random generating peer id
LOCAL_PORT = 59696

class torrent(object):
	def __init__(self,metainfo):

		#getting params
		self.metainfo=metainfo
		self.announce_url=self.metainfo['announce']
		if self.metainfo['announce-list']:
			self.announce_list=self.metainfo['announce-list']
			print self.announce_list
		self.announce_url = self.announce_list[2][0]
		self.info=self.metainfo['info']
		self.sha_info=hashlib.sha1(bencode.bencode(self.info))
		self.info_hash=self.sha_info.digest()                  #returns the result of sha1 encodeing
		self.peer_id=self.generate_peer_id()
		self.uploaded=0 
		self.downloaded=0
		self.overall_length=self.length_of_file()
		#left:The number of bytes this client still has to download in base ten ASCII
		self.left=self.overall_length
		#Setting this to 1 indicates that the client accepts a compact response
		self.compact=1
		self.no_peer_id=0
		self.event="started"
		self.port=LOCAL_PORT
		self.param_dict={'info_hash':self.info_hash,'peer_id':self.peer_id,'port':self.port,'uploaded':self.uploaded,'downloaded':self.downloaded, 'left':self.left,'compact':self.compact, 'no_peer_id':self.no_peer_id, 'event':self.event}
		if 'name' in self.info:
			#if only one file is there
			self.folder_name=self.info['name']
		else:
			self.folder_name="Your File is here"
		self.piece_length=self.info['piece length']      #size in bytes
		print 'packet-size:',self.piece_length
		pieces_hash=self.info['pieces']
		self.pieces_array=[]
		while len(pieces_hash)>0:
			self.pieces_array.append(pieces_hash[0:20])
			pieces_hash=pieces_hash[20:]
	def length_of_file(self):
		info=self.metainfo['info']
		length=0
		if 'length' in info:
			length=info['length']
		else:
			files=info['files']
			for fileDict in files:
				length+=fileDict['length']
		return length
	def generate_peer_id(self):
		N=20-len(PEER_ID_START)
		end=''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(N))
		peer_id=PEER_ID_START+end
		return peer_id
def main():
	f=open('book2.torrent')

if __name__ == '__main__':
	main()


