# -*- coding: utf-8 -*-
# vStream https://github.com/Kodi-vStream/venom-xbmc-addons
# TODO : resources/art/sites https://w20.filmstreaming.plus/assets/images/logo.png  filmstreaming_plus.png
# source 02 update 04/08/2020 20*633 F12 660  # down 08092020 ?
# return

import re
from resources.lib.gui.hoster import cHosterGui
from resources.lib.gui.gui import cGui
from resources.lib.handler.inputParameterHandler import cInputParameterHandler
from resources.lib.handler.outputParameterHandler import cOutputParameterHandler
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.parser import cParser
from resources.lib.comaddon import progress
from resources.lib.comaddon import VSlog


bVSlog = True
bSearchFilter = False

SITE_IDENTIFIER = 'filmstreaming_plus'
SITE_NAME = 'Filmstreaming plus'
SITE_DESC = ' films en streaming'

URL_MAIN = 'https://w21.filmstreaming.plus/'#URL_MAIN = 'https://w20.filmstreaming.plus/'

MOVIE_MOVIE = (True, 'load')
MOVIE_NEWS = (URL_MAIN, 'showMovies')
MOVIE_GENRES = (True, 'showGenres')

URL_SEARCH = (URL_MAIN + '?s=', 'showMovies')
URL_SEARCH_MOVIES = (URL_SEARCH[0], 'showMovies')
FUNCTION_SEARCH = 'showMovies'


def load():
    oGui = cGui()

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', 'http://venom/')
    oGui.addDir(SITE_IDENTIFIER, 'showSearch', 'Recherche', 'search.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', MOVIE_NEWS[0])
    oGui.addDir(SITE_IDENTIFIER, MOVIE_NEWS[1], 'Films (Derniers ajouts)', 'news.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', MOVIE_GENRES[0])
    oGui.addDir(SITE_IDENTIFIER, MOVIE_GENRES[1], 'Films (Genres)', 'genres.png', oOutputParameterHandler)

    oGui.setEndOfDirectory()


def showSearch():
    oGui = cGui()

    sSearchText = oGui.showKeyBoard()
    if (sSearchText != False):
        sUrl = URL_SEARCH[0] + sSearchText.replace(' ', '+')
        showMovies(sUrl)
        oGui.setEndOfDirectory()
        return


def showGenres():
    oGui = cGui()
    
    liste = []
    liste.append(['Action', URL_MAIN + 'films/action.html'])
    liste.append(['Animation', URL_MAIN + 'films/animation.html'])
    liste.append(['Aventure', URL_MAIN + 'films/aventure.html'])
    liste.append(['Comédie', URL_MAIN + 'films/comedie.html'])
    liste.append(['Drame', URL_MAIN + 'films/drame.html'])
    liste.append(['Guerre', URL_MAIN + 'films/guerre.html'])
    liste.append(['Historique', URL_MAIN + 'films/historique.html'])
    liste.append(['Horreur', URL_MAIN + 'films/horreur.html'])
    liste.append(['Musique', URL_MAIN + 'films/musical.html'])
    liste.append(['Policier', URL_MAIN + 'films/policier.html'])
    liste.append(['Romance', URL_MAIN + 'films/romance.html'])
    liste.append(['Thriller', URL_MAIN + 'films/thriller.html'])
    liste.append(['Science-fiction', URL_MAIN + 'films/science-fiction.html'])

    for sTitle, sUrl in liste :
        oOutputParameterHandler = cOutputParameterHandler()
        oOutputParameterHandler.addParameter('siteUrl', sUrl)
        oGui.addDir(SITE_IDENTIFIER, 'showMovies', sTitle, 'genres.png', oOutputParameterHandler)

    oGui.setEndOfDirectory()


def showMovies(sSearch='',word = ''):
    oGui = cGui()
    
    ifVSlog('# filmstreaming plus showMovies')
    if sSearch:
        sUrl = sSearch
        word = sSearch.replace(URL_MAIN + '?s=', '').replace('+', ' ').replace('%20', ' ')
        ifVSlog('word=' + word)
    
    else:
        oInputParameterHandler = cInputParameterHandler()
        sUrl = oInputParameterHandler.getValue('siteUrl')

    
    ifVSlog(sUrl)
    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()

    if URL_MAIN == sUrl:
        if '</h1>' in sHtmlContent:
            sHtmlContent = sHtmlContent[sHtmlContent.find('</h1>'):]

    #url  thumb title  desc
    sPattern ='<div class="moviefilm">.+?href="([^"]*)".+?img src="([^"]*).+?alt="([^"]*)".+?<\/br>(.*?)<(/p)'
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)
    
    if (aResult[0] == False):
        oGui.addText(SITE_IDENTIFIER)

    if (aResult[0] == True):
        total = len(aResult[1])
        progress_ = progress().VScreate(SITE_NAME) 

        for aEntry in aResult[1]:  
            progress_.VSupdate(progress_, total)
            if progress_.iscanceled():
                break
            
            sTitle = ''
            sUrl2 = aEntry[0]
            sTitle = aEntry[2]
            sTitle = sTitle.replace('Film Streaming ' , '')
            sThumb = aEntry[1]
            sDesc  = aEntry[3]
            sDesc = ('[I][COLOR grey]%s[/COLOR][/I] %s') % ('\r\nSynopsis : \r\n', sDesc)

            
            if sSearch and bSearchFilter:
                if not CompareResult(word.lower(),sTitle.lower()):
                    continue
            
            
            if (sDesc == ''):
                sDesc = 'No description'
            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl', sUrl2)
            oOutputParameterHandler.addParameter('sMovieTitle', sTitle)
            oOutputParameterHandler.addParameter('sThumb', sThumb)
            oOutputParameterHandler.addParameter('sDesc', sDesc)
            oGui.addMovie(SITE_IDENTIFIER, 'showHosters', sTitle, '', sThumb, sDesc, oOutputParameterHandler)

        progress_.VSclose(progress_)

    if not sSearch:
        NextPage = __checkForNextPage(sHtmlContent)

        if (NextPage != False):
            sUrlNextPage = NextPage[0]
            sNumLastPage  = NextPage[1]
            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl', sUrlNextPage)
            sPattern = 'filmstreaming.plus.*?page-([^"]*).html'
            aResult = oParser.parse(sUrlNextPage, sPattern)
            if (aResult[0] == True):
                number = str(aResult[1][0])
                oGui.addNext(SITE_IDENTIFIER, 'showMovies', '[COLOR teal]Page ' + number + '/' + sNumLastPage + ' >>>[/COLOR]', oOutputParameterHandler)        
            else:
                oGui.addNext(SITE_IDENTIFIER, 'showMovies', '[COLOR teal]Page >>>[/COLOR]', oOutputParameterHandler)

        oGui.setEndOfDirectory()


def __checkForNextPage(sHtmlContent):
    oParser = cParser()
    sPattern = 'nextpostslink" href="([^"]*)".+?last" .*?page-([^"]*).html'
    Result = oParser.parse(sHtmlContent, sPattern)
    if (Result[0] == True):
        return Result[1][0]
    return False


def showHosters():
    oGui = cGui()


    ifVSlog('#')
    ifVSlog('showHosters()')

    oInputParameterHandler = cInputParameterHandler()
    sUrl = oInputParameterHandler.getValue('siteUrl')
    sMovieTitle = oInputParameterHandler.getValue('sMovieTitle')
    sThumb = oInputParameterHandler.getValue('sThumb')
    sDesc = oInputParameterHandler.getValue('sDesc')

    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()
    
    
    oParser = cParser()
    # Durée : 1h 30min, Film : Américain, Réalisé en 2020,
    sPattern = 'synopsis.+?Durée.+?\s+([^,]+).+?(\d{4})' 
    aResult = oParser.parse(sHtmlContent, sPattern)
    if (aResult[0] == True):
        sDesc2 = aResult[1][0][0] + ' ' + aResult[1][0][1]
        sDesc2 = ('[COLOR dimgray]%s[/COLOR] ') % (sDesc2 )
        #sDesc = sDesc2 + '\r\n' + sDesc
        sDesc = sDesc2  + sDesc
    
    
    
    
    sPattern = 'class="player link.+?player="([^"]*)".+?langue-s">(.+?)<.+?name">(.+?)<.+?quality">(.+?)<'
    #g1 requete host   g2 lang   g3 hostname   g4 quality
    oParser = cParser() 
    aResult = oParser.parse(sHtmlContent, sPattern)
    if (aResult[0] == False):
        oGui.addText(SITE_IDENTIFIER)

    b_ADD_TRUEFRENCH = False
    b_ADD_VOSTFR = False
    b_ADD_VO = False
    sTRUEFRENCH = 'TRUEFRENCH'
    sVOSTFR = 'VOSTFR'
    sVO = 'VO'

    if (aResult[0] == True):

        for aEntry in aResult[1]:
            sUrlrequestHost = aEntry[0]  # requete type =URL_MAIN + player.php?p=60&c=VFV...5nPQ==
            sHostname= aEntry[2]
            sLang = aEntry[1]
            sQuality= aEntry[3]

            #Hoster pas résolus, réponse header seulement : pas trouvé infos, code 200#: on évite la recherche
            sBlackHostList = ['gounlimited' , 'upstream', 'ddownload.com']
            #
            #if sHostname not in sBlackHostList or True: #on laisse tout laisser
            if sHostname not in sBlackHostList :

                if  (sLang == sTRUEFRENCH) and (not b_ADD_TRUEFRENCH) :
                    b_ADD_TRUEFRENCH= True
                    oGui.addText(SITE_IDENTIFIER, '[COLOR skyblue]STREAMING VF : [/COLOR]')

                if  (sLang == sVOSTFR) and (not b_ADD_VOSTFR) :
                    b_ADD_VOSTFR= True
                    oGui.addText(SITE_IDENTIFIER, '[COLOR skyblue]STREAMING  VOSTFR : [/COLOR]')

                if  (sLang == sVO) and (not b_ADD_VO) :
                    b_ADD_VO= True
                    oGui.addText(SITE_IDENTIFIER, '[COLOR skyblue]STREAMING  VO : [/COLOR]')

                #sTitle = ('%s (%s) (%s)[COLOR coral]%s[/COLOR]') % (sMovieTitle, sLang,sQuality, sHostname)
                sTitle = ('%s (%s)[COLOR coral]%s[/COLOR]') % (sMovieTitle + ' ' ,sQuality ,' ' + sHostname)
                oOutputParameterHandler = cOutputParameterHandler()
                oOutputParameterHandler.addParameter('siteUrl', sUrlrequestHost )
                oOutputParameterHandler.addParameter('sMovieTitle', sMovieTitle)
                oOutputParameterHandler.addParameter('sThumb', sThumb)
                oOutputParameterHandler.addParameter('Referer', sUrl)
                oGui.addLink(SITE_IDENTIFIER, 'ShowStreamingLink', sTitle, sThumb, sDesc, oOutputParameterHandler)



    #### hoster Download link 
    #non fonctionnel et a debuger
    bWantDebugDownloadLink = True

    if not bWantDebugDownloadLink:
        ifVSlog('host DownloadLink is disabled')
        oGui.setEndOfDirectory()
        return

    ifVSlog('host DownloadLink is enabled')

    sHtmlContent = sHtmlContent[sHtmlContent.find('Liens de téléchargement'):sHtmlContent.find('</html>')]
    if  not sHtmlContent:
        ifVSlog( 'no find start and end string in sHtmlContent')
        oGui.setEndOfDirectory()
        return
    
    sPattern = 'href="([^"]*)".+?<li class="player".+?langue-s">(.+?)<.+?name">(.+?)<.+?quality">(.+?)<'
    #g1 requete host   g2 lang   g3 hostname   g4 quality
    oParser = cParser() 
    aResult = oParser.parse(sHtmlContent, sPattern)
    if (aResult[0] == False):
        oGui.addText(SITE_IDENTIFIER)

    b_ADD_TRUEFRENCH = False
    b_ADD_VOSTFR = False
    b_ADD_VO = False
    sTRUEFRENCH = 'TRUEFRENCH'
    sVOSTFR = 'VOSTFR'
    sVO = 'VO'
    
    if (aResult[0] == True): 
        for aEntry in aResult[1]:        
            sUrlrequestHost = aEntry[0] 
            sHostname= aEntry[2]
            sLang = aEntry[1]
            sQuality= aEntry[3]  
            if  (sLang == sTRUEFRENCH) and (not b_ADD_TRUEFRENCH) :
                b_ADD_TRUEFRENCH= True
                oGui.addText(SITE_IDENTIFIER, '[COLOR skyblue]DOWLOAD VF : [/COLOR]')
                    
            if  (sLang == sVOSTFR) and (not b_ADD_VOSTFR) :
                b_ADD_VOSTFR= True
                oGui.addText(SITE_IDENTIFIER, '[COLOR skyblue]DOWLOAD VOSTFR : [/COLOR]')
                
            if  (sLang == sVO) and (not b_ADD_VO) :
                b_ADD_VO= True
                oGui.addText(SITE_IDENTIFIER, '[COLOR skyblue]DOWLOAD VO : [/COLOR]')

                #sTitle = ('%s (%s) (%s)[COLOR coral]%s[/COLOR]') % (sMovieTitle, sLang,sQuality, sHostname)
                sTitle = ('%s (%s)[COLOR coral]%s[/COLOR]') % (sMovieTitle +' ' , sQuality ,  ' ' + sHostname)         

            # ok
            #ifVSlog('# Dowload ')
            #ifVSlog('url = '+sUrlrequestHost )
            #ifVSlog('host = '+sHostname)
            #ifVSlog('lanq = '+sLang )
            #ifVSlog('q = '+sQuality)
            
            sTitle = ('%s (%s)[COLOR coral]%s[/COLOR]') % (sMovieTitle +' ' , sQuality ,  ' ' + sHostname)
            #goto oOutputParameter ,addlink ShowDownloadLink
            btesteFirstHost=True # 
            if btesteFirstHost:  
                #exemple
                #https://w21.filmstreaming.plus/star-wars-lascension-de-skywalker.html
                #https://shortn.co/f/6017545 hidden
                
                #https://shortn.co/f/6017545 show contains url ok
                #url ok
                #https://uptobox.com/0qj94zm5dnjo

            
                
                # code ici temporaire a enlever 
                # on resoud deja un host obligation du addlink 
                #car requete trop nombreuse pour chaque host
                oRequestHandler = cRequestHandler(sUrlrequestHost)
                oRequestHandler.addHeaderEntry('Referer', sUrl )
                sHtmlHost1 = oRequestHandler.request()
                sHeader=oRequestHandler.getResponseHeader()
    
                # ok ?
                cookies=''
                if False:
                    for iheader in sHeader:
                        if iheader == 'set-cookie':
                            cookies = sHeader.getheader('set-cookie')               
                            break  
                # ok

                cookies = sHeader.getheader('set-cookie') 
                ifVSlog('cookies getheader:' + cookies)
                
                
                if 'set-Cookie' in sHeader:
                    c1 = sHeader.get('set-cookie')
                    c2 = re.findall('(?:^|,) *([^;,]+?)=([^;,]+?);', c1)
                    if c2:
                        cookies = ''
                        for cook in c2:
                            cookies = cookies + cook[0] + '=' + cook[1] + ';'
                            cookies = cookies[:-1]
                      
                ifVSlog('cookies re.findall :' + cookies)
              
                #cookies = sHeader.getheader('set-cookie') 
                sPatternt = "token.+?value='([^']*)"
                _token = re.search(sPatternt,sHtmlHost1 ).group(1)
                pdata ='_token='+_token
                
                surlorigine ='https://shortn.co'
                ifVSlog('cookies :' + cookies)
                ifVSlog('req URL='+ sUrlrequestHost)
                ifVSlog('pdata ='+ pdata)
                
                #pdata ='_token=WPdVEeyOzFN9oBjK307lTClgcRi2XZySUy6KM8qP'
                
                #Failded
                #ERREUR 500 
                #Content-Type: application/x-www-form-urlencoded Upgrade-Insecure-Requests
                
                oRequest = cRequestHandler(sUrlrequestHost )
                oRequest.setRequestType(1)
                oRequest.addHeaderEntry('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:70.0) Gecko/20100101 Firefox/70.0')
                oRequest.addHeaderEntry('Content-Type','application/x-www-form-urlencoded' )
                oRequest.addHeaderEntry('Origine', surlorigine )
                oRequest.addHeaderEntry('Cookie', cookies )
                oRequest.addHeaderEntry('Upgrade-Insecure-Requests', '1')
                
                #oRequest.addHeaderEntry('Referer', sUrl )
                oRequest.addHeaderEntry('Referer', sUrlrequestHost )
                oRequest.addParametersLine(pdata)
                sHtmlHost2 = oRequest.request() 
                
                if '1fichier' not in sHtmlHost2 :
               
                    ifVSlog('Failed !')
                else:
                    ifVSlog('Success !!!!')

                #ifVSlog(sHtmlHost2 )
                #pas acess a la page ou le lien embede  devrait se trouver dans une requete /reponse valide
            
            #oOutputParameter
            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl', sUrlrequestHost )
            oOutputParameterHandler.addParameter('sMovieTitle', sMovieTitle)
            oOutputParameterHandler.addParameter('sThumb', sThumb)
            oOutputParameterHandler.addParameter('Referer', sUrl)
            oGui.addLink(SITE_IDENTIFIER, 'ShowDownloadLink',sTitle, sThumb, sDesc, oOutputParameterHandler)
            ###test premier host #a enlever
            if btesteFirstHost :
                oGui.setEndOfDirectory()
                return
                
    oGui.setEndOfDirectory()
    

def ShowDownloadLink():
    
    oGui = cGui()
    oInputParameterHandler = cInputParameterHandler()
    sUrlrequestHost = oInputParameterHandler.getValue('siteUrl')
    sMovieTitle = oInputParameterHandler.getValue('sMovieTitle')
    sThumb = oInputParameterHandler.getValue('sThumb')
    sUrl = oInputParameterHandler.getValue('Referer')
    
    # inoperant
    oRequestHandler = cRequestHandler(sUrlrequestHost)
    sHtmlHost1 = oRequestHandler.request()
    _token=''
    sPatternt = "token.+?value='([^']*)"
    try :
        #sPattern = "token.+?value='([^']*)"
        _token = re.search(sPatternt,sHtmlHost1 ).group(1)
        ifVSlog('find token='+_token)
    except:
        ifVSlog('except no find token')
        
    pdata ='_token='+_token
    ifVSlog('req URL='+sUrlrequestHost)
    ifVSlog('pdata='+pdata)
    oRequest = cRequestHandler(sUrlrequestHost )
    oRequest.setRequestType(1)
    oRequest.addHeaderEntry('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:70.0) Gecko/20100101 Firefox/70.0')
    oRequest.addHeaderEntry('Referer', sUrlrequestHost )
    #oRequest.addHeaderEntry('Referer', sUrl )
    oRequest.addParametersLine(pdata)
    sHtmlContent = oRequest.request() 
    # error 500
    # nonresolu
    if False:
        sHosterUrl = 'inconnu'

        pattern = 'url=([^"]*)' 
        oParser = cParser()
        aResult = oParser.parse(sHosterUrl, pattern)
        sHosterUrl = str(aResult[1][0])   
    
        oHoster = cHosterGui().checkHoster(sHosterUrl) 
        if (oHoster != False):
            oHoster.setDisplayName(sMovieTitle)
            oHoster.setFileName(sMovieTitle)
            cHosterGui().showHoster(oGui, oHoster, sHosterUrl, sThumb)

    oGui.setEndOfDirectory()   

def ShowStreamingLink():

    oGui = cGui()
    oInputParameterHandler = cInputParameterHandler()
    sUrlrequestHost = oInputParameterHandler.getValue('siteUrl')
    sMovieTitle = oInputParameterHandler.getValue('sMovieTitle')
    sThumb = oInputParameterHandler.getValue('sThumb')
    sUrl = oInputParameterHandler.getValue('Referer')
        
    oRequestHandler = cRequestHandler( sUrlrequestHost )
    oRequestHandler.addHeaderEntry('Referer', sUrl) 
    sHosterUrl= oRequestHandler.request()         
                
    if sHosterUrl:
        
        pattern = 'url=([^"]*)' 
        oParser = cParser()
        aResult = oParser.parse(sHosterUrl, pattern)
        sHosterUrl = str(aResult[1][0])   
    
        oHoster = cHosterGui().checkHoster(sHosterUrl) 
        if (oHoster != False):
            oHoster.setDisplayName(sMovieTitle)
            oHoster.setFileName(sMovieTitle)
            cHosterGui().showHoster(oGui, oHoster, sHosterUrl, sThumb)

    oGui.setEndOfDirectory()

def CompareResult(search,result):
    ss = search.split(' ')
    list_rs = []
    list_split = [' ', ':', '&', '\'', ',', '.', ';' , '-']
    for spl in list_split:
        list_rs.append(result.split(spl))
    
    for rs in list_rs:
        for r in rs:
            for s in ss:
                if r == s :
                    return True
    return False

def ifVSlog(log):
    if bVSlog:
        try:  # si no import VSlog from resources.lib.comaddon
            VSlog(str(log))
        except:
            pass
