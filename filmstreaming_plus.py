# -*- coding: utf-8 -*-
# vStream https://github.com/Kodi-vStream/venom-xbmc-addons
# TODO : resources/art/sites https://w20.filmstreaming.plus/assets/images/logo.png  filmstreaming_plus.png
# milki source 2

from resources.lib.gui.hoster import cHosterGui
from resources.lib.gui.gui import cGui
from resources.lib.handler.inputParameterHandler import cInputParameterHandler
from resources.lib.handler.outputParameterHandler import cOutputParameterHandler
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.parser import cParser
from resources.lib.comaddon import progress
from resources.lib.comaddon import VSlog


#[COLOR coral]%s[/COLOR]
SITE_IDENTIFIER = 'filmstreaming_plus'
SITE_NAME = '[COLOR skyblue]Filmstreaming plus[/COLOR]'
SITE_DESC = ' films en streaming'

#URL_MAIN = 'https://w19.filmstreaming.plus/'  # marche mais liens vers https://w20.filmstreaming.plus/ 
URL_MAIN = 'https://w20.filmstreaming.plus/'

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
    liste.append(['Action', URL_MAIN + 'films/action.html'] )
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


def showMovies(sSearch=''):
    oGui = cGui()
    
    if sSearch:
        sUrl = sSearch
    else:
        oInputParameterHandler = cInputParameterHandler()
        sUrl = oInputParameterHandler.getValue('siteUrl')

    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()

    sPattern ='<div class="moviefilm">.+?href="([^"]*)".+?img src="([^"]*).+?alt="([^"]*)".+?<\/br>(.*?)<(/p)'
    #g1 url  g2 thumb g3 title  g4 desc
    
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
            sTitle=''
            sUrl2  = aEntry[0]
            sTitle = aEntry[2]
            sTitle = sTitle.replace('Film Streaming ' , '')
            sThumb = aEntry[1]
            sDesc  = aEntry[3]
            sDesc = ('[COLOR coral]%s[/COLOR] %s') % ('\r\nSYNOPSIS : \r\n\r\n', sDesc)
            
            if (sDesc==''):
                sDesc='No description'
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
                number=str(aResult[1][0])
                oGui.addNext(SITE_IDENTIFIER, 'showMovies', '[COLOR teal]Page ' + number +'/'+ sNumLastPage +' >>>[/COLOR]', oOutputParameterHandler)        
            else:
                #VSlog('error parse next page '+ sUrlNextPage )
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

    oInputParameterHandler = cInputParameterHandler()
    sUrl = oInputParameterHandler.getValue('siteUrl')
    sMovieTitle = oInputParameterHandler.getValue('sMovieTitle')
    sThumb = oInputParameterHandler.getValue('sThumb')
    
    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()
    
    sPattern = 'class="player link.+?player="([^"]*)".+?langue-s">(.+?)<.+?name">(.+?)<.+?quality">(.+?)<'
    #g1 requete host   g2 lang   g3 hostname   g4 quality
    oParser = cParser() 
    aResult = oParser.parse(sHtmlContent, sPattern)

    if (aResult[0] == False):
        oGui.addText(SITE_IDENTIFIER)

    if (aResult[0] == True): 
        
        for aEntry in aResult[1]:        
            sUrlrequestHost = aEntry[0]  # requete type =URL_MAIN + player.php?p=60&c=VFV...5nPQ==
            sHostname= aEntry[2]
            sLang = aEntry[1]
            sQuality= aEntry[3]           
            
            #Hoster pas résolus, réponse header seulement : pas trouvé infos, code 200#: on évite la recherche
            sBlackHostList = ['gounlimited' , 'upstream', 'ddownload.com']
            #mystream
            bResponse=False
            if sHostname not in sBlackHostList  or True:
                  
                oRequestHandler = cRequestHandler( sUrlrequestHost )
                oRequestHandler.addHeaderEntry('Referer', sUrl) 
                sHosterUrl=oRequestHandler.request()         
                if not sHosterUrl=='':
                    #revoir methode
                    pattern='url=([^"]*)' 
                    oParser = cParser()
                    aResult = oParser.parse(sHosterUrl, pattern)
                    sHosterUrl=str(aResult[1][0])
                    bResponse=True
                    #VSlog('sHostname = '+sHostname +' ;  sHosterUrl = '+sHosterUrl)             
            
            #if (bResponse== False ) :
                    #VSlog('Error find embed file request='+str(sUrlrequestHost)) 
                    #continue
            
            sTitle = ('%s (%s) %s') % (sMovieTitle , sLang, sQuality )
            #sTitle = ('%s (%s) [COLOR coral]%s[/COLOR]') % (sMovieTitle, sLang, sQuality)
            
            oHoster = cHosterGui().checkHoster(sHosterUrl )
            if (oHoster != False):
                oHoster.setDisplayName(sTitle)
                oHoster.setFileName(sMovieTitle)
                cHosterGui().showHoster(oGui, oHoster, sHosterUrl, sThumb)
    
    oGui.setEndOfDirectory()


    

