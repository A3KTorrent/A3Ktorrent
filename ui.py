from gi.repository import Gtk
#from main import main
filename='path'
class UI:
	def __init__(self):
		self.builder = Gtk.Builder()
		self.builder.add_from_file("layout.glade")
		self.builder.get_object('window1').connect('delete-event',Gtk.main_quit)

		self.dialog=self.builder.get_object('dialog1')
		self.window = self.builder.get_object("window1")
		self.progressbar= self.builder.get_object("progressbar1") #PROGRESSBAR
		self.aboutdialog = self.builder.get_object("aboutdialog1")
	
	def connect(self,handlers):
		self.builder.connect_signals(handlers)
		self.window.show_all()

	def download(self,button):
 		print "Download butoon pressed"
 		print 'FILENAME:',filename
 		if filename == 'path' or filename.split('.',1)[1]!='torrent':
 			print 'PATH'
 			print 'PLEASE ENTER A TORRENT FILE'
	 		response=dialog.run()
	 		#dialog.show_all()
	 		print response
	 		if response == 1:
	 			print 'The OK button was clicked'
	 		elif response == 2:
	 			print 'the cancel button was clicked'
	 		dialog.hide()
		else:
	 		print 'else'
	 		self.set_progressbar(0.7)

	def set_progressbar(self,percentage):
		print percentage
		self.progressbar.set_fraction(percentage)
		#perce
		return			


	def filechoose(self,widget):
		print 'filechoose'
		global filename
		filename=widget.get_filename()
		print 'FILENAME:',filename

def main():
	ui= UI()
	handlers={
		"onDeleteWindow":Gtk.main_quit,
		"onDownloadButtonPressed":ui.download,
		"on_filechooserbutton1_file_set":ui.filechoose
	}
	ui.connect(handlers)
	val=ui.aboutdialog.run()
	# print val
	# x=4
	ui.aboutdialog.destroy()


	Gtk.main()

if __name__ == '__main__':
	main()
