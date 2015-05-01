from bs4 import BeautifulSoup
import requests
import os

def download_torrent(url):
    print url
    fname = os.getcwd() + '/' + url.split('title=')[-1] + '.torrent'
    # http://stackoverflow.com/a/14114741/1302018
    try:
        r = requests.get(url, stream=True)
        f=open(fname,'wb')
        for chunk in r.iter_content(chunk_size=1024):
        	if chunk:
        		f.write(chunk)
        		f.flush()
        f.close()
    except requests.exceptions.RequestException as e:
        print '\n' + str(e)
        sys.exit(1)

    return fname
def main(s):
	url='http://kickass.to/usearch/'+s+'/'
	r=requests.get(url)
	soup=BeautifulSoup(r.content)
	
	al = [s.get_text() for s in soup.find_all('td', {'class':'center'})]
	href = [a.get('href') for a in soup.find_all('a', {'title':'Download torrent file'})]
	size = [t.get_text() for t in soup.find_all('td', {'class':'nobr'}) ] 
	title = [ti.get_text() for ti in soup.find_all('a', {'class':'cellMainLink'})]
	age = al[2::5]      #a[start:end:step]
	seeders = al[3::5]  
	leechers = al[4::5]	
	print 'NUMBER TITLE SIZE SEEDERS LEECHERS'
	for i in range(len(href)):
		print str(i+1)+' '+title[i]+' '+size[i]+' '+seeders[i]+' '+leechers[i]
		print ' '
	choice=raw_input('ENTER NUMBER:')
	#print a
	fname=download_torrent(href[int(choice)-1])
	print fname+'  DOWNLOADED'
		

if __name__ == '__main__':
	s=raw_input('SEARCH:')
	main(str(s))