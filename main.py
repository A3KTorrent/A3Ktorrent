
from os import path, mkdir, remove, rename
from bencode import *
from ConfigParser import ConfigParser
from time import time
from bitstring import BitArray
from hashlib import sha1
from struct import pack, unpack
import requests
from twisted.internet import reactor, task, defer
from torrent import torrent
from messages import Handshake, Request, KeepAlive, bytes_to_number
from pieces import TorrentFile
from bittorrenter import BittorrentFactory
import constants
import sys
from random import randrange
import socket
import urllib, urllib2
from progress_lib import update_progress
from blessings import Terminal
term = Terminal()

from gi.repository import Gtk, GObject
import thread
import getpass #for username
import multiprocessing
import scrape   
#sys.path.append(path.abspath("scraping"))
import scrape_test

#from twisted.internet import gtk3reactor
#gtk3reactor.install()


class UI(object):
    def __init__(self):
        self.filename='path'
        self.builder = Gtk.Builder()
        self.builder.add_from_file("layout.glade")
        self.builder.get_object('window1').connect('delete-event',Gtk.main_quit)

        self.dialog=self.builder.get_object('dialog1')
        self.dialog2=self.builder.get_object('dialog2')
        self.window = self.builder.get_object("window1")
        self.progressbar= self.builder.get_object("progressbar1") #PROGRESSBAR
        self.aboutdialog = self.builder.get_object("aboutdialog1")
        self.label = self.builder.get_object("label1")
        self.search_field = self.builder.get_object("search_field")
        self.dow_label = self.builder.get_object("dow_speed")
        #self.popup_menu = self.builder.get_object("menu5")
    
    def connect(self,handlers):
        self.builder.connect_signals(handlers)
        self.window.show_all()

    def search(self,button):
        print 'search clicked'
        print 'search clicked'
        self.popup_menu=Gtk.Menu()
        i1 = Gtk.MenuItem("Leechers seeders size")
        self.popup_menu.append(i1)
        i2 = Gtk.MenuItem("Item 2")
        self.popup_menu.append(i2)
        self.popup_menu.show_all()
        self.popup_menu.popup(None, None, None, None, 0, Gtk.get_current_event_time())
        #self.popup_menu.popup(None, None, None, None, None, 0,0)
#self.popup_for_device(None, parent_menu_shell, parent_menu_item, func, data, button, activate_time)

        s=self.search_field.get_text()
        thread.start_new_thread(scrape_test.main,(s,))

    def download(self,button): #when download button is pressed!
        #self.progressbar.set_fraction(0.7)
        
        print "Download button pressed"
        print 'FILENAME:',self.filename
        a=self.filename.split('.')
        if self.filename == 'path' or a[len(a)-1]!='torrent':
            print 'PATH'
            print 'PLEASE ENTER A TORRENT FILE'
            response=self.dialog.run()
            #dialog.show_all()
            print response
            if response == 1:
                print 'The OK button was clicked'
            elif response == 2:
                print 'the cancel button was clicked'
            self.dialog.hide()
        else:
            print 'else'
            button.set_sensitive(False) # so that user can not press download button again!
            
            
            # for i in range(1,len(sys.argv)):
            #    torrent_list=torrent_list.append(sys.argv[i])
            #torrent_list.append(sys.argv[1])

            thread.start_new_thread(self.start_download,())
            #p=multiprocessing.Process(target=self.start_download)
            #p.start()
            

    def start_download(self):
        # change this for changing writing directory
        username=getpass.getuser()
        writing_dir='/home/'+username+'/Downloads/a3k'
        ###############################################
        print writing_dir
        torrent_list=[]
        torrent_list.append(self.filename)
        print '*'*50
        #print sys.argv[1]
        print torrent_list
        active_torrent_list = []    
        for torrent in torrent_list:
            print 'torrent: ' + torrent
            t = ActiveTorrent(self,torrent, writing_dir)
            t.connect()
            print t.peers
            active_torrent_list.append(t)
            l_expired = task.LoopingCall(t.check_for_expired_requests)
            l_expired.start(constants.PENDING_TIMEOUT) #run every x seconds
            l_send_keep_alives = task.LoopingCall(t.check_for_keep_alives)
            l_send_keep_alives.start(constants.KEEP_ALIVE_TIMEOUT/2)

        l_check_for_done = task.LoopingCall(check_for_done, active_torrent_list)
        l_check_for_done.start(20)  #checks every x secondsif all torrents have finished downloading

        reactor.run()


    def set_progressbar(self,percentage,download_speed):
        #print percentage
        #Gtk.main()
        print percentage
        self.progressbar.set_fraction(percentage)
        self.dow_label.set_text(str(download_speed))
        if percentage >= 1.0:
            #gtk_label_set_text(self.label,"TORRENT FILE 50% DOWNLOADED")
            self.label.set_text("TORRENT FILE 100% DOWNLOADED")
            self.dialog=self.builder.get_object('dialog1')
            v=self.dialog.run()
            if v==1:
                self.dialog.destroy()
                Gtk.main_quit()

    def filechoose(self,widget):
        print 'filechoose'
        self.filename=widget.get_filename()
        print 'FILENAME:',self.filename

class ActiveTorrent(object):
    def __init__(self,ui, torrent_file, writing_dir):
        self.ui=ui
        self.torrent_info = self.get_torrent(torrent_file)
        self.peers = self.get_peers()
        self.file_downloading = TorrentFile(self.torrent_info.overall_length, self.torrent_info.piece_length)
        #print 'oye'
        print 'no. of pieces',self.file_downloading.number_pieces
        self.pieces=0
        self.requested_blocks = self.bitarray_of_block_number()
        self.have_blocks = self.bitarray_of_block_number()
        self.writing_dir = writing_dir
        self.pending_timeout = dict()
        self.factory = BittorrentFactory(self)
        self.blocks_per_full_piece = self.torrent_info.piece_length / constants.REQUEST_LENGTH 
        self.setup_temp_file()
        self.done = False
        self.start_time=time()                 #for download speed

    def bitarray_of_block_number(self):
        block_number = 0
        for piece in self.file_downloading.piece_list:
            block_number += piece.block_number
        #print 'block_number',block_number
        return BitArray(block_number)

    def get_torrent(self,torrent_file):
        f = open(torrent_file, 'r')
        metainfo = bdecode(f.read())  #return a dictionary
        f.close()
        torrent_info = torrent(metainfo)
        return torrent_info

    def setup_temp_file(self):
        folder_name = self.torrent_info.folder_name.rsplit('.',1)[0] #if a single file, this takes off the extension
        self.folder_directory = path.join(self.writing_dir, folder_name)
        self.temp_file_path = path.join(self.folder_directory, folder_name + '.temp')
        #assumption that writing_dir exists already, since this is passed in
        try:
            mkdir(self.folder_directory)
        #if can't create dir, it probably already exists and file has been partially downloaded before
        except:
            if path.exists(self.temp_file_path):
                open(self.temp_file_path, 'w').close() #clears file of all contents if exists; this is for testing with files multiple times
        self.tempfile = open(self.temp_file_path, 'wb') #open only once 

    def connect(self):
        number_connections = 0
        for peer in self.peers:
            if number_connections < constants.NUMBER_PEERS:
                hostandport = peer.split(':')
                print hostandport[0] + ':' + hostandport[1]
                reactor.connectTCP(hostandport[0], int(hostandport[1]), self.factory)
                number_connections += 1

    def parse_response_from_tracker(self,r): #for tcp
        '''Input: http response from our request to the tracker
           Output: a list of peer_ids
           Takes the http response from the tracker and parses the peer ids from the 
           response. This involves changing the peer string from unicode (binary model)
           to a network(?) model(x.x.x.x:y). From the spec: 'First 4 bytes are the IP address and
           last 2 bytes are the port number'
        '''
        response = bdecode(r.content)
        peers = response['peers']
        peer_address = ''
        peer_list = []
        for i,c in enumerate(peers):
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
        return peer_list

    def get_peers(self):
        print self.torrent_info.announce_url
        '''Input: metainfo file (.torrent file)
           Output: a list of peer_ids (strings) returned from the tracker
           Calls methods to send an http request to the tracker, parse the returned
           result message and return a list of peer_ids
        '''
        if "udp://" in self.torrent_info.announce_url:
            url=self.torrent_info.announce_url
            self.track_url=url.split('//',1)[1].split(':',1)[0]
            self.track_port=url.split('//',1)[1].split(':',1)[1].split('/',1)[0]
            print self.track_url
            print self.track_port
            print 'ITS UDP TRACKER'
            result = self.udp_connection_request()
            print result
            return result
        else:
            print 'HTTP'
            r = requests.get(self.torrent_info.announce_url, params=self.torrent_info.param_dict)
            peers = self.parse_response_from_tracker(r)
            print peers
            return peers

    def udp_connection_request(self):
        self.clisocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.clisocket.connect((self.track_url,int(self.track_port)))
        #print 'oye udp'
        connection_id = 0x41727101980
        transaction_id = randrange(1, 65535)              # transaction id is a random number
        action = 0                                        #0 is for connect
        #packet = pack(">QLL", connection_id, action, transaction_id)             #packed binary data of 16 byte!
        
        buf = pack("!q", connection_id) #first 8 bytes is connection id
        buf += pack("!i", action) #next 4 bytes is action
        buf += pack("!i", transaction_id)
        #self.clisocket.sendto(packet, (self.track_url, int(self.track_port)))
        self.clisocket.send(buf)

        res = self.clisocket.recv(16)
        print 'NOW RECv'
        parsed_res = unpack(">LLQ", res)

        print parsed_res
        if parsed_res[0] == 0 and parsed_res[1] == transaction_id:  #Check:transaction ID is equal to the one you chose nad action is connect (0).
            print 'CORRECT RESPONSE FROM UDP'
            peers = self.udp_announce_request(parsed_res)
            return peers
        else:
            return "Garbage Response from UDP tracker connection response"

    def udp_announce_request(self,connection_resp):
        #print 'F@'
        action, transaction_id, connection_id = connection_resp
        info_hash = self.torrent_info.sha_info.hexdigest()
        info_hash = info_hash.decode('hex')
        #print info_hash
        #print self.torrent_info.sha_info.digest()
        peer_id = self.torrent_info.peer_id
        downloaded = 0
        left = 0
        uploaded = 0
        event = 2
        ip = 0
        key = 0
        num_want = 50
        port = 9999
        #action id announce i.e, equal to 1
        announce_pack = pack(">QLL20s20sQQQLLLLH", connection_id, 1, transaction_id, info_hash, 
                peer_id, downloaded, left, uploaded, event, ip, key, num_want, port
                )
        self.clisocket.sendto(announce_pack, (self.track_url, int(self.track_port)))
        res = self.clisocket.recv(1024)
        #print len(res)
        action = unpack("!LL", res[:8])
        print action
        if action[0] == 1 and action[1] == transaction_id:
            index=20     #28
            peers=[]
            while index < len(res):
                ip = socket.inet_ntoa(pack('!L', (unpack("!L", res[index:index+4])[0]))) # res[26:30];res[32:36]
                port = unpack("!H", res[index+4:index+6])[0] # res[30:32];res[36:38]
                peers.append(ip+':'+str(port))     #conversion from string ip address to numeric ip address

                index = index + 6
            return peers
        else:
            return "Garbage Response from UDP tracker announce response"



        
        

    def handshake(self, torrent_obj):
        '''Input: ip:port of a peer with the torrent files of interest
           Output: <fill this in>
           <fill this in>
        '''
        info_hash = torrent_obj.info_hash
        peer_id = torrent_obj.peer_id
        handshake = Handshake(info_hash, peer_id)
        return handshake

    def reset_blocks(self,block_num):
        del self.pending_timeout[block_num]
        self.requested_blocks[block_num] = 0

    def check_for_expired_requests(self):
        now = time()
        pairs = [(k,v) for (k,v) in self.pending_timeout.iteritems()]
        for k,v in pairs:
            #if value more than x seconds before now, remove key and set pending_requests to 0 for key
            if (now - v) > constants.PENDING_TIMEOUT:
                self.reset_blocks(k)
                piece_num, block_bytes_in_piece = self.determine_piece_and_block_nums(k) 
                block_index_in_piece = block_bytes_in_piece / constants.REQUEST_LENGTH
                block_num_overall = self.piece_and_index_to_overall_index(block_index_in_piece, piece_num)
                request = self.format_request(piece_num, block_bytes_in_piece) 
                for protocol in self.factory.protocols:
                    if protocol.interested and not protocol.choked:
                        protocol.transport.write(str(request))
                        protocol.message_timeout = time()
                        self.requested_blocks[block_num_overall] = 1
                        self.pending_timeout[block_num_overall] = time()


    def write_piece(self, piece, piece_num):         #wrting to file
        piece_offset = piece_num * self.torrent_info.piece_length
        for i,block in enumerate(piece.block_list):
            self.tempfile.seek(piece_offset + i * constants.REQUEST_LENGTH)
            self.tempfile.write(block.bytestring)
        piece.written = True
        self.check_if_done()

    def check_if_done(self):
        #print 'Checking if complete'
        if all(self.have_blocks):
            print '\nTorrent completely downloaded!\n'
            self.tempfile.close()
            self.done = True

    def write_multiple_files(self, info):
        print 'multiple files. creating files and folders.'
        f_read = open(self.temp_file_path,'rb')
        for element in info['files']:
            path_list = element['path']
            i = 0
            #make sure directory structure exists
            sub_folder = self.folder_directory
            while i + 1 < len(path_list):  #create directory structure
                sub_folder = path.join(sub_folder, path_list[i])
                if not path.isdir(sub_folder): #folder does not exist yet
                    mkdir(sub_folder)
                i += 1
            final_file_path = path.join(sub_folder, path_list[-1])
            f_write = open(final_file_path, 'wb')
            f_write.write(f_read.read(element['length']))
            #cleanup:
            f_write.close()
        f_read.close()
        remove(self.temp_file_path)

    def write_all_files(self):
        info = self.torrent_info.info
        if 'files' in info:
            self.write_multiple_files(info)
        else:
            print 'single file. renaming'
            extension = self.torrent_info.folder_name.rsplit('.',1)[1]
            rename(self.temp_file_path, self.temp_file_path[:-4]+extension)  #just rename file with correct extension

    def format_request(self, piece_num, block_byte_offset):
        block_num_in_piece = block_byte_offset / constants.REQUEST_LENGTH 
        piece = self.file_downloading.piece_list[piece_num]
        request_len = piece.block_list[block_num_in_piece].expected_length
        index_pack = pack('!l',piece_num)
        begin_pack = pack('!l', block_byte_offset)
        length_pack = pack('!l',request_len) 
        #print 'generating request for piece: ' + str(piece_num)+' and block: ' + str(block_byte_offset / constants.REQUEST_LENGTH)
        request = Request(index=index_pack, begin=begin_pack, length=length_pack)
        return request

    def clear_data(self, piece, piece_num):
        #write piece's blocks to empty (do a debug if_full check to verify)
        #set have and requested blocks for piece to 0
        print 'clear_data called because hashes did not match'
        for block_num, block in enumerate(piece.block_list):
            piece.write(block_num, '')
            block_num_overall = self.piece_and_index_to_overall_index(block_num, piece_num) 
            self.have_blocks[block_num_overall] = 0
            self.requested_blocks[block_num_overall] = 0
        print 'after clearing, is the piece full? (should be False) ' + piece.check_if_full()

    def check_hash(self, piece, piece_num):            #check piece hash when piece is fuly downloaded
        #print 'piece ' + str(piece_num) + ' is full!'
        
        self.time=time()-self.start_time #toal time
        self.pieces+=1 #it holds no. of pieces downloaded
        #print self.pieces
        #print 'PACKET SIZE:',self.torrent_info.piece_length
        #print "DOWNLOAD SPEED:",
        downloaded=(float(self.torrent_info.piece_length)*.008*self.pieces)/(float(self.time))
        #,'Kbps'
        #print 'total pieces',self.file_downloading.number_pieces
        percentage=float(self.pieces)/float(self.file_downloading.number_pieces)
        
        #self.ui.set_progressbar(percentage)
        GObject.idle_add(self.ui.set_progressbar,percentage,downloaded) 
        #thread-safe# to call gtk methods from diff. threads
        
        #update_progress(percentage,100)
        #print 'PERCENTAGE DOWNLOADED',percentage,'%'
        #sys.stdout.write('\r DOWNLOADED->'+str(percentage)+'%'+'        DOWNLOAD-SPEED->'+str(downloaded))
        # sys.stdout.write('\r')
        # sys.stdout.write("[%-50s] %f%%" % ('='*int(percentage*50), percentage*100))
        print ('\r'),
        print (term.bright_red + term.on_black +"[%-50s] %f%%" % ('='*int(percentage*50), percentage*100)+term.normal),
        #calculate percentage
        #print self.have_blocks


        #calculate percentage
        piece_string = ''
        for block in piece.block_list:
            piece_string += block.bytestring
        #piece_string = [piece_string + block.bytestring for block in piece.block_list]
        if sha1(piece_string).digest() == self.torrent_info.pieces_array[piece_num]:
            #print 'hashes matched, writing piece'
            self.write_piece(piece,piece_num)
        else:
            print 'HASHES DID NOT MATCH'
            self.clear_data(piece,piece_num)
        return percentage

    def write_block(self,block):                             # called by bittorrenter!
        block_num_in_piece = bytes_to_number(block.begin) / constants.REQUEST_LENGTH
        piece_num = bytes_to_number(block.index)
        mypiece = self.file_downloading.piece_list[piece_num]
        block_num_overall = self.piece_and_index_to_overall_index(block_num_in_piece, piece_num) 
        if not self.have_blocks[block_num_overall]:
            mypiece.write(block_num_in_piece, block.block)
            self.have_blocks[block_num_overall] = 1  #add block to have list
            #print '\npiece ' + str(piece_num) +' and block '+ str(block_num_in_piece) + ' received'
        if block_num_overall in self.pending_timeout: #remove block from timeout pending dict
            del self.pending_timeout[block_num_overall]
        if mypiece.check_if_full() and not mypiece.written:
            percentage=self.check_hash(mypiece,piece_num)# check hash value of piece when piece is downloaded fuly
            return percentage

    def determine_piece_and_block_nums(self, overall_block_num):
        piece_num, block_index_in_piece  = self.overall_index_to_piece_and_index(overall_block_num)
        block_byte_offset = self.block_index_to_bytes(block_index_in_piece)
        return piece_num, block_byte_offset

    def piece_and_index_to_overall_index(self, block_piece_index, piece_num):
        return block_piece_index + piece_num * self.blocks_per_full_piece

    def overall_index_to_piece_and_index(self, overall_block_index):
        piece_num = overall_block_index / self.blocks_per_full_piece
        block_index_in_piece = overall_block_index % self.blocks_per_full_piece
        return piece_num, block_index_in_piece

    def block_index_to_bytes(self, block_index):
        return block_index * constants.REQUEST_LENGTH

    def check_for_keep_alives(self):
        for protocol in self.factory.protocols:
            now = time()
            if (now - protocol.message_timeout) > constants.KEEP_ALIVE_TIMEOUT:
                print 'Keep Alive message sent'
                protocol.transport.write(str(KeepAlive()))
                protocol.message_timeout = time()

def check_for_done(active_torrents):
    #if all torrents finished
    if all([t.done for t in active_torrents]):
        print 'All torrents finished downloading. Stopping reactor loop'
        reactor.stop()
        #self.connector.disconnect()
        [t.write_all_files() for t in active_torrents]

def main():
    GObject.threads_init()
    ui= UI()
    handlers={
        "onDeleteWindow":Gtk.main_quit,
        "onDownloadButtonPressed":ui.download,
        "on_filechooserbutton1_file_set":ui.filechoose,
        "search_clicked":ui.search
    }
    ui.connect(handlers)
    val=ui.aboutdialog.run()
    # print val
    # x=4
    ui.aboutdialog.destroy()
    Gtk.main()

   #  writing_dir='/home/kritesh/Music'
   #  torrent_list=[]
   # # for i in range(1,len(sys.argv)):
   #  #    torrent_list=torrent_list.append(sys.argv[i])
   #  #torrent_list.append(sys.argv[1])
   #  torrent_list.append(filename)
   #  print '*'*50
   #  #print sys.argv[1]
   #  print torrent_list
   #  active_torrent_list = []
   #  for torrent in torrent_list:
   #      print 'torrent: ' + torrent
   #      t = ActiveTorrent(torrent, writing_dir)
   #      t.connect()
   #      print t.peers
   #      active_torrent_list.append(t)
   #      l_expired = task.LoopingCall(t.check_for_expired_requests)
   #      l_expired.start(constants.PENDING_TIMEOUT) #run every x seconds
   #      l_send_keep_alives = task.LoopingCall(t.check_for_keep_alives)
   #      l_send_keep_alives.start(constants.KEEP_ALIVE_TIMEOUT/2)

   #  l_check_for_done = task.LoopingCall(check_for_done, active_torrent_list)
   #  l_check_for_done.start(20)  #checks every x secondsif all torrents have finished downloading

   #  reactor.run()

if __name__ == "__main__":
    main()

