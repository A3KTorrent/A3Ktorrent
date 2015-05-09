import sys
import time
import libtorrent as lt

#Create torrent
def create_torrent(file_path,file_name):
	fs = lt.file_storage()
	lt.add_files(fs, file_path)
	t = lt.create_torrent(fs)
	t.add_tracker("udp://tracker.openbittorrent.com:80/announce", 0)
	t.set_creator('libtorrent %s' % lt.version)
	t.set_comment("Test")
	lt.set_piece_hashes(t, ".")
	torrent = t.generate()    
	f = open(file_name, "wb")
	f.write(lt.bencode(torrent))
	f.close()
def main():
	
if __name__ == '__main__':
	main()