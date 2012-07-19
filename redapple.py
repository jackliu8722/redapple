
'''
Created on 2012-4-5

@author: jackliu
'''
import sys
import os
import eyeD3
import re
import urllib
class FileErrorException(Exception):
    pass
class RedApple:
    def __init__(self):
        pass
baiduurl = 'http://mp3.baidu.com'
mp3url = "http://mp3.baidu.com/m?f=ms&rf=idx&tn=baidump3lyric&ct=150994944&lf=&rn=10&lm=-1&word=%s"
resultlyrics_r = '<div class="item-lyric">.*?</div>.*?</div>.*?</div>.*?</div>'
lyrics_info = '<span class="title_c">(.*?)</span>.*?<span class="title_c">.*?<a.*?>(.*?)</a>.*?<div class="text-lyric-abstract.*?">(.*?)</div>'
lyrics_info_r = re.compile(lyrics_info,re.I)
next = '<a class=".*?next.*?".*?href="(.*?)">'
next_r = re.compile(next,re.I)
filetypelist = ['mp3','mP3','Mp3','MP3']
class LyricsParser:
    """
    get lyrics from internet
    """
    __mp3Name = "" 
    __artist = ""  
    __lyrics = ""  
    def __init__(self,mp3Name,artist):
        self.__mp3Name = mp3Name
        self.__artist = artist
        self.__lyrics = ""
    def parse(self):
        next_url = mp3url % urllib.quote(self.__mp3Name.encode('gbk','ignore'))
        while next_url is not None:
            #print next_url
            try:
                mp3 = urllib.urlopen(next_url)
            except:
                next_url = None
                continue
            content = mp3.read(); 
            content = content.decode('gbk','ignore');
            content = re.sub('\n+',' ',content)
            result_lyrics= re.findall(resultlyrics_r,content)
            match = next_r.search(content)
            if match:
                next_url = baiduurl+match.group(1)
            else:
                next_url = None
            for lyric_info in result_lyrics:
                lyric_info = re.sub("</?em>","",lyric_info)
                match = lyrics_info_r.search(lyric_info)
                # print lyric_info
                if self.__checkLyric(match):
                    return
        #print 'no lyrics'
        
    def __checkLyric(self,match):
        
        if match:
            #print match.group(1),match.group(2)
            if match.group(1).strip() == self.__mp3Name: 
                lyrics = None
                if match.group(3): 
                    lyrics = re.sub("<br.*?>",'\n',match.group(3))
                if match.group(2).strip() == self.__artist: 
                    if lyrics != None:
                        self.__lyrics = lyrics
                        return True
                else: 
                    if self.__lyrics == '': 
                        self.__lyrics = lyrics
        return False
    def getLyric(self):
        return self.__lyrics
def main():
    if len(sys.argv) == 1:
        print("error: the command like redapple folder|file [folder|file]...")
        print("       Pelease try again")
        return;
    totalMp3File = 0 
    successDownload = 0 
    
    for path in sys.argv[1:]:
        if os.path.isdir(path) or os.path.isfile(path):
            (total,success) = download(path)
            totalMp3File += total
            successDownload += success
        else: 
            print("error: %s is not a folder or file" % path)
    print "Total: {0},success:{1}".format(totalMp3File,successDownload) 
def download(path):
    filelist = []
    success = 0
    maxlen = 0
    if os.path.isdir(path):
        for file in os.listdir(path):
            fullpathname = os.path.join(path,file)
            if fullpathname[-3:] in filetypelist:
                if maxlen < len(fullpathname):
                    maxlen = len(fullpathname)
                filelist.append(fullpathname)
    else:
        fullpathname = path
        if fullpathname[-3:] in filetypelist:
            filelist.append(fullpathname)
    maxlen += 6
    for file in filelist:
        print u"handle file",file,(maxlen - len(file))*'.',
        if downloadLyricsByID3V3(file) or downloadLyricsByFilename(file):
            success += 1
            print u"download success"
        else:
            print u"download failed"
    return len(filelist),success 
def downloadLyricsByID3V3(file):
    tag = eyeD3.Tag()
    tag.link(file)
    tag.encoding = '\x01'
    if tag.getLyrics() and len(tag.getLyrics()[0].lyrics):  
        #print tag.getLyrics()[0].lyrics
        return 1
    else:  
        artist = tag.getArtist()
        title = re.sub("\(.*?\)",'',tag.getTitle())
        lyricsParser = LyricsParser(title,artist)
        lyricsParser.parse()
        lyrics = unicode(lyricsParser.getLyric())
        if len(lyrics) > 0 : 
            tag.addLyrics(lyrics)
            tag.update()
            return 1
        return 0

def downloadLyricsByFilename(file):
    tag = eyeD3.Tag()
    tag.link(file)
    tag.encoding = '\x01'
    if tag.getLyrics() and len(tag.getLyrics()[0].lyrics):
        #print tag.getLyrics()[0].lyrics
        return 1
    else:  
        filename = file[len(os.path.dirname(file))+1:]
        artist,title =filename.rsplit('-',1) 
        artist = artist.strip()
        title = title.strip()[:-4]
        title = re.sub("\(.*?\)",'',title)
        #print artist,title
        lyricsParser = LyricsParser(title.decode('gbk'),artist.decode('gbk'))
        lyricsParser.parse()
        lyrics = unicode(lyricsParser.getLyric())
        if len(lyrics) > 0 : 
            tag.addLyrics(lyrics)
            tag.update()
            return 1
        return 0
        
if __name__ == '__main__':
    main()
    
    