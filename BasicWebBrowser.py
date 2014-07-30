#!/usr/bin/env python
import sys, threads
import gtk
import webkit
import warnings
from time import sleep
from optparse import OptionParser
 
warnings.filterwarnings('ignore')
 
class WebView(webkit.WebView):
    def get_html(self):
        self.execute_script('oldtitle=document.title;document.title=document.documentElement.innerHTML;')
        html = self.get_main_frame().get_title()
        self.execute_script('document.title=oldtitle;')
        return html
 
class Crawler(gtk.Window):
    def __init__(self, url, file):
        gtk.gdk.threads_init()
        gtk.Window.__init__(self)
        self._url = url
        self._file = file
 
    def crawl(self):
        view = WebView()
        view.open(self._url)
        view.connect('load-finished', self._finished_loading)
        self.add(view)
        gtk.main()
 
    def _finished_loading(self, view, frame):
        with open(self._file, 'w') as f:
            f.write(view.get_html())
        gtk.main_quit()
 
def main():
    options = get_cmd_options()
    crawler = Crawler(options.url, options.file)
    crawler.crawl()
 
def get_cmd_options():
    """
        gets and validates the input from the command line
    """
    usage = "usage: %prog [options] args"
    parser = OptionParser(usage)
    parser.add_option('-u', '--url', dest = 'url', help = 'URL to fetch data from')
    parser.add_option('-f', '--file', dest = 'file', help = 'Local file path to save data to')
 
    (options,args) = parser.parse_args()
 
    if not options.url:
        print 'You must specify an URL.',sys.argv[0],'--help for more details'
        exit(1)
    if not options.file:
        print 'You must specify a destination file.',sys.argv[0],'--help for more details'
        exit(1)
 
    return options
 
if __name__ == '__main__':
    main()
