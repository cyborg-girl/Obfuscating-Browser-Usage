from random import randrange
from urllib2 import urlopen
from BeautifulSoup import *
from bs4 import BeautifulSoup
from urlparse import urljoin
from pysqlite2 import dbapi2 as sqlite

#Create a list of words to ignore
ignorewords=set(['the','of','to','and','a','in','is','it'])

class crawler:
    # Initialize the crawler with the name of database
    def __init__(self,dbname):
        self.con=sqlite.connect(dbname)
        self.trackers = {'Google Analytics':[['js','src'],'http://www.google-analytics.com/urchin.js',\
                                                 '//www.google-analytics.com/analytics.js',\
                                                 'http://www.google-analytics.com/ga.js',\
                                                 'google-analytics.com/ga.js'],
                         'Twitter':[['js','src'],'http://platform.twitter.com/widgets.js'],
                         'Google +1':[['js','src'],'https://apis.google.com/js/plusone.js'],
                         'Facebook Like':[['js','src'],'www.facebook.com/widgets/like.php'],
                         'abine.stub.Google Analytics':[['script','id'],'abine.stub.Google Analytics'],
                         'abine.stub.Facebook Connect':[['script','id'],'abine.stub.Facebook Connect'],
                         'abine.stub.Google Adsense':[['script','id'],'abine.stub.Google Adsense'],
                         'abine.stub.Microsoft Atlas':[['script','id'],'abine.stub.Microsoft Atlas']}
    def __del__(self):
        self.con.close()
    def dbcommit(self):
        self.con.commit()

    # Return true if this url is already indexed
    def isindexed(self,url):
        u=self.con.execute \
            ("select rowid from urllist where url='%s'" % url).fetchone( )
        if u!=None:
            return True
        return False
    
    def findTrackers(self,soup):
        tracklist = set()
        for tracker in self.trackers:
            trackType = self.trackers[tracker][0]
            trackSearch = self.trackers[tracker][1:]
            if trackType[0] == 'js':
                #print soup.text[:10]
                scripts = soup.find_all('script',{'type' : 'text/javascript'})
                if scripts:
                    for script in scripts:
                        try:
                            if [x for x in trackSearch if str(script).find(x)!=-1] or script[trackType[1]] in trackSearch:
                                tracklist.add(tracker)
                                print 'Found %s... Dirty Bastards!' % (tracker)
                        except Exception,e:
                            #print str(e)
                            continue
           #elif trackType[0] == 'script': finding other scripts
               
                                                        
        return tracklist

    def addUrl(self,url,tracking,trackers):
        print url + ' ' + tracking + ' ' + trackers
        self.con.execute("insert into urllist(url,tracking,trackers) \
                             values ('%s','%s','%s')" % (url,tracking,trackers))
    
    def crawl(self,pages,depth=3):
        while 1:
            newpages=set( )
            for page in pages:
                try:
                    #print page
                    soup=BeautifulSoup(urlopen(page),'html')
                except:
                    print "Could not open %s" % page
                    continue
                #print soup.text[:10]
                links=soup('a')
                for link in links:
                    if ('href' in dict(link.attrs)) and soup:
                        url=urljoin(page,link['href'])
                        if url.find("'")!=-1: continue
                        url=url.split('#')[0] # remove location portion
                        if url[0:4]=='http' and not self.isindexed(url):
                            newpages.add(url)
                            trackers = self.findTrackers(soup)
                            if trackers:
                                trackers = ','.join(trackers)
                                self.addUrl(url,'yes',trackers)
                            else:
                                self.addUrl(url,'no','N/A')
                self.dbcommit( )
            pages=newpages
            if not pages:
                pages = ["https://duckduckgo.com/?t=lm&q=%s" % (str(''.join([chr(randrange(20,127))\
                                                                                 for i in range(5)])))]
            
    def createindextables(self):
        self.con.execute('create table urllist(url,tracking,trackers)')
        self.dbcommit()
