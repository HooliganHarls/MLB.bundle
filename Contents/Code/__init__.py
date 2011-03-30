import re, datetime,httplib

####################################################################################################

VIDEO_PREFIX = "/video/harleyball"

NAME          = 'Major League Baseball'
ART           = 'art-default.jpg'
ICON          = 'icon-default.png'

MLB_Games='http://gdx.mlb.com/components/game/mlb/year_'
MLB_URL='http://mlb.mlb.com/index.jsp'
MLB_Video='http://mlb.mlb.com/video/play.jsp?content_id='
MLB_Schedule='http://mlb.mlb.com/mlb/schedule/team_by_team.jsp?tcid=mm_mlb_schedule'
MLB_Standings='http://mlb.mlb.com/mlb/standings/exhibition.jsp?tcid=mm_mlb_standings'
MLB_Scoreboard='http://mlb.mlb.com/mlb/scoreboard/index.jsp?tcid=nav_mlb_scoreboard'
MLB_Teams='http://mlb.mlb.com/team/index.jsp?tcid=nav_mlb_sitelist'
MLB_Search='http://mlb.mlb.com/scripts/club_properties.jsp?responseType=json'
MLB_Login='https://secure.mlb.com/account/topNavLogin.jsp'

####################################################################################################
def Start():

    Plugin.AddPrefixHandler(VIDEO_PREFIX, MainMenu, 'Major League Baseball', ICON, ART)

    Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
    Plugin.AddViewGroup("List", viewMode="List", mediaType="items")

    MediaContainer.art = R(ART)
    MediaContainer.title1 = NAME
    DirectoryItem.thumb = R(ICON)
    
    getPrefs()

####################################################################################################
def MainMenu():
    dir = MediaContainer(viewGroup="List")
    
    dir.Append(Function(DirectoryItem(Scoreboard, "Today's Games"), url = MLB_Games))
    dir.Append(Function(DirectoryItem(getPlaylists, "Videos"), url = MLB_Video))
    dir.Append(Function(DirectoryItem(Scoreboard, "Daily Scoreboard"), url = MLB_Scoreboard))
    #dir.Append(Function(DirectoryItem(Videos, "Teams"), url = MLB_Teams))
    dir.Append(Function(DirectoryItem(StandingsDir, "Standings"), url = MLB_Standings))
    dir.Append(Function(DirectoryItem(Schedule, "Schedule"), url = MLB_Schedule))
    
    dir.Append(PrefsItem("Preferences"))
    return dir

####################################################################################################
def getPrefs():


    
    
    
    if Prefs['mlb_user'] and Prefs['mlb_pass']:
        try:
            
            url='https://secure.mlb.com/account/topNavLogin.jsp'
            req = HTTP.Request(url, values=dict(
            successRedirect = "http://mlb.mlb.com/shared/account/v2/login_success.jsp?callback=l1300638004681",
            errorRedirect = "http://mlb.mlb.com/account/quick_login_hdr.jsp?error=true&successRedirect=http%3A%2F%2Fmlb.mlb.com%2Fshared%2Faccount%2Fv2%2Flogin_success.jsp%253Fcallback%253Dl1300638004681&callback=l1300638004681&stylesheet=%2Fstyle%2Faccount_management%2FmyAccountMini.css&submitImage=%2Fshared%2Fcomponents%2Fgameday%2Fv4%2Fimages%2Fbtn-login.gif&errorRedirect=http://mlb.mlb.com/account/quick_login_hdr.jsp%3Ferror%3Dtrue%26successRedirect%3Dhttp%253A%252F%252Fmlb.mlb.com%252Fshared%252Faccount%252Fv2%252Flogin_success.jsp%25253Fcallback%25253Dl1300638004681%26callback%3Dl1300638004681%26stylesheet%3D%252Fstyle%252Faccount_management%252FmyAccountMini.css%26submitImage%3D%252Fshared%252Fcomponents%252Fgameday%252Fv4%252Fimages%252Fbtn-login.gif",
            emailAddress = Prefs['mlb_user'],
            password = Prefs['mlb_pass'],
            submit="Login"
            ))
            Log(req)
            req=str(req)
            title=req.split('<title>')[-1]
            title=title.split('</title>')[0]
            Log(title)
            if title=="Login Success":
                title=title
                Log("Success")
            else:
                title=title
                Log("Fail")
        except:
            pass
####################################################################################################
def Schedule(sender, url):
    dir= MediaContainer(viewGroup="List")
    dir = MediaContainer(title2=sender.itemTitle)
    
    content=HTML.ElementFromURL(url).xpath('//ul[@id="team_by_team"]/li/ul')
    
    for team in content:
        url=team.xpath('li[2]/a')[0].get('href')
        code=url.split('=')[-1]
        thumb=R('logo-'+code.upper()+'.png')
        name=team.xpath('li/h5/a/img')[0].get('alt')
        dir.Append(Function(DirectoryItem(TeamSched,title=name,thumb=thumb),url=url))
    return dir
####################################################################################################
def TeamSched(sender, url):
    dir= MediaContainer(viewGroup="List")
    dir = MediaContainer(title2=sender.itemTitle)
    
    team_name=url.split('.')[1]
    code=url.split('=')[-1]
    urlbase=url.split('.com/')[0]+'.com'
    url=urlbase+'/'+code+'/components/schedule/y2011/schedule.js'
    content=HTML.ElementFromURL(url)
    content=XML.StringFromElement(content)
    content=content.split('= [')[-1]
    content=content.split('],')
    for item in content:
        try:
            item=item.split('[')[-1]
            list=item.split(',')
            vsTeam=list[3].split("'")[1]
            away=list[20].split("'")[1]
            score=list[6].split("'")[1]
            month=list[21].split("/")[1]
            day=list[21].split("/")[2]
            thumb=R('logo-'+vsTeam.upper()+'.png')
            if away=="away":
                title='@'+vsTeam.upper()+' on '+month+'/'+day+' | '+score
            else:
                title=vsTeam.upper()+' on '+month+'/'+day+' | '+score
            dir.Append(Function(DirectoryItem(TeamSched,title=title,thumb=thumb),url=url))
        except:pass
    return dir
    
####################################################################################################
def StandingsDir(sender, url):
    dir= MediaContainer(viewGroup="List")
    dir = MediaContainer(title2=sender.itemTitle)
    url='http://mlb.mlb.com/components/standings/st_al.js'
    thumb=R('Al-Logo.png')
    dir.Append(Function(DirectoryItem(Standings, "American League", thumb=thumb), url = url))
    url='http://mlb.mlb.com/components/standings/st_nl.js'
    thumb=R('NL-Logo.png')
    dir.Append(Function(DirectoryItem(Standings, "National League",thumb=thumb), url = url))
    return dir
####################################################################################################
def Standings(sender, url):
    dir=MediaContainer(viewGroup="List")
    
    content=HTML.ElementFromURL(url)
    content=XML.StringFromElement(content)
    content=content.split("[")[-1]
    content=content.split("]")[0]
    teams=content.split(', ')
    
    for obj in teams:
        teamobj=JSON.ObjectFromString(obj)
        name=teamobj['team']
        wins=teamobj['w']
        loss=teamobj['l']
        pct=teamobj['pct']
        gb=teamobj['gb']
        code=teamobj['code']
        thumb=R('logo-'+code.upper()+'.png')
        title=name+': '+wins+'-'+loss+' || '+pct+' || '+gb
        dir.Append(Function(DirectoryItem(Standings, title=title,thumb=thumb), url = url))
    return dir
####################################################################################################
def Scoreboard(sender, url):
    Log(Prefs)

    url=url
    
    now = datetime.datetime.now()
    
    year=now.strftime("%Y")
    Log(year)
    month=now.strftime("%m")
    Log(month)
    day=now.strftime("%d")
    Log(day)
    
    dirtitle=sender.itemTitle+' '+month+'/'+day+'/'+year
    
    dir = MediaContainer(title2=dirtitle, httpcookies=HTTP.GetCookiesForURL(url))
    dir=MediaContainer(viewGroup="InfoList")
    cook=HTTP.GetCookiesForURL(url)
    Log(cook)
    url='http://mlb.mlb.com/gdcross/components/game/mlb/year_'+year+'/month_'+month+'/day_'+day+'/master_scoreboard.json'
    Log(url)
    dict=JSON.ObjectFromURL(url, headers={'Referer':'http://mlb.mlb.com'})
    data=dict['data']['games']['game']
    
    for game in data:
        home_name=game['home_team_name']
        away_name=game['away_team_name']
        
        home_city=game['home_name_abbrev']
        away_city=game['away_name_abbrev']
        thumb=R('logo-'+home_city.upper()+'.png')
        
        status=game['status']['status']
        time=game['time_hm_lg']
        tz=game['tz_hm_lg_gen']
        
        Log(status)
        
        if status=="Preview":
            title=away_city+' '+away_name+ ' @ '+ home_city+' '+home_name
            sub='Gametime: '+time+' '+tz
            url=url
            summary=""
            dir.Append(Function(DirectoryItem(Scoreboard, title=title,thumb=thumb,subtitle=sub), url = url))
        elif status=="media archive":
            title=away_city+' '+away_name+ ' @ '+ home_city+' '+home_name
            sub='Highlights'
            summary=""
            id=game['game_media']['media']['calendar_event_id']
            id=id.split('-')[1]
            url='http://mlb.mlb.com/search/media.jsp?game_pk='+id
            dir.Append(Function(DirectoryItem(Videos, title=title,thumb=thumb,subtitle=sub), url = url))
        elif status=="Final":
            title=away_city+' '+away_name+ ' @ '+ home_city+' '+home_name
            sub='Highlights'
            summary=""
            try:
                id=game['game_media']['media']['calendar_event_id']
                id=id.split('-')[1]
                url='http://mlb.mlb.com/search/media.jsp?game_pk='+id  
                dir.Append(Function(DirectoryItem(Videos, title=title,thumb=thumb,subtitle=sub), url = url))  
            except:pass
        elif status=="In Progress":
            inning=game['status']['inning']
            isTop=game['status']['top_inning']
            if isTop=="N":
                top="Bot"
            if isTop=="Y":
                top="Top"
            Log(game)
            Log(game['game_media'])
            try:id=game['game_media']['media']['calendar_event_id']
            except:id=""
            home_score=game['linescore']['r']['home']
            away_score=game['linescore']['r']['away']
            
            home_e=game['linescore']['e']['home']
            away_e=game['linescore']['e']['away']
            
            home_h=game['linescore']['h']['home']
            away_h=game['linescore']['h']['away']
            
            boxscore=game['linescore']['inning']
            
            
            
            title=away_city+' '+away_name+' ' ' @ '+ home_city+' '+home_name
            
            if status=="Final":
                sub=away_city+': '+away_score+' | '+home_city+': '+home_score+' | Final'
            else:
                sub=away_city+': '+away_score+' | '+home_city+': '+home_score+' | '+inning+' '+top
            duration='Inning: '+inning+' '+top
            Log(sub)
            summary=duration+'\n'
            
        ##################Box Score Header########################   
            summary=summary+'Inn   ||'
            i_count=0
            for inning in boxscore:
                i_count=i_count+1
                summary=summary+' '+str(i_count)+' |'
            summary=summary+'| R | H | E |'+'\n'
            summary=summary+'-----------------------------------------------------------'+'\n'
            
         ##################Away Team Box Score########################   
            summary=summary+away_city+' ||'
            i_count=0
            for inning in boxscore:
                try:
                    
                    if boxscore[i_count]['away']=="":
                        summary=summary+' 0 |'
                    else:
                        summary=summary+' '+boxscore[i_count]['away']+' |'
                except:
                    summary=summary+' 0 |'
                
                i_count=i_count+1    
            summary=summary+'| '+away_score+' | '+away_h+' | '+away_e+' | '+'\n'
            
         ##################Home Team Box Score########################      
            summary=summary+home_city+' ||'
            i_count=0
            for inning in boxscore:
                
                try:
                    if boxscore[i_count]['home']=="":
                        summary=summary+' 0 |'
                    else:
                        summary=summary+' '+boxscore[i_count]['home']+' |'

                except:
                    summary=summary+' 0 |'

                i_count=i_count+1
                Log(summary)
            summary=summary+'| '+home_score+' | '+home_h+' | '+home_e+' | '+'\n'
            
            url='http://mlb.mlb.com/flash/mediaplayer/v4.2/R2/MP4.jsp?calendar_event_id='+id+'&content_id=&media_id=&view_key=&media_type=video&source=MLB&sponsor=MLB&clickOrigin=&affiliateId=&team=mlb&'
            dir.Append(WebVideoItem(url, title=title, subtitle=sub,thumb=thumb))
        Log(title)
        Log(url)
             

    return dir
    
####################################################################################################
def Videos(sender, url):
    dir = MediaContainer(title2=sender.itemTitle,httpcookies=HTML.Getcookies(url))
    url=url
    id=url.split('game_pk=')[-1]
    url='http://mlb.mlb.com/ws/search/MediaSearchService?start=0&site=mlb&hitsPerPage=12&hitsPerSite=10&type=json&c_id=&src=vpp&sort=desc&sort_type=custom&game='+id
    
    content=JSON.ObjectFromURL(url , headers={'Referer':'http://mlb.mlb.com'})
    
    for item in content['mediaContent']:
        thumb=item['thumbnails'][1]['src']
        id=item['contentId']
        title=item['title']
        url='http://mlb.mlb.com/video/play.jsp?content_id='+str(id)
        sub=item['blurb']
        duration=item['duration']
        desc=item['bigBlurb']
        Log(title)
        
        dir.Append(WebVideoItem(url, title=title, subtitle=sub,summary=desc,thumb=thumb))  
    return dir
    
####################################################################################################
def getPlaylists(sender, url):
    dir = MediaContainer(title2=sender.itemTitle)
    page=url
    
    list=HTML.ElementFromURL(page).xpath('//div[@id="videoBrowseNav"]/ul/li[contains(@class,"topic")]/a')
    
    for playlist in list:
        name=playlist.text
        id=playlist.get('rel')
        Log('id: '+ str(id))
        url='http://mlb.mlb.com/gen/multimedia/topic/'+id+'.xml'
        content=HTML.ElementFromURL(url)
        s_query=content.xpath('//search_query')[0].text

    
        if not s_query:
            
            link=content.xpath('//video_index')[0].get('src')
            thumb=content.xpath('//images/image')[1].get('src')
            url='http://mlb.mlb.com'+link
            Log(url)
            dir.Append(Function(DirectoryItem(XMLList, title=name,thumb=thumb), url=url,topic=id))
        else:
            url='http://mlb.mlb.com/ws/search/MediaSearchService?'+s_query+'&hitsPerPage=200&src=vpp'
            Log(url)
            dir.Append(Function(DirectoryItem(JSONList, title=name), url=url,topic=id))
    
    
    lists=HTML.ElementFromURL(page).xpath('//div[@id="videoBrowseNav"]/ul/li[contains(@class,"category")]')
    
    
    for playlist in lists:
        NestedListDict=dict()
        mainname=playlist.xpath('a')[0].text
        nestedList=playlist.xpath('ul/li/a')
        Log('=================')
        Log(name)
        
        for plist in nestedList:
            name=plist.text
            id=plist.get('rel')
            url='http://mlb.mlb.com/gen/multimedia/topic/'+id+'.xml'
            content=HTML.ElementFromURL(url)
            s_query=content.xpath('//search_query')[0].text

    
            if not s_query:
                
                link=content.xpath('//video_index')[0].get('src')
                thumb=content.xpath('//images/image')[1].get('src')
                url='http://mlb.mlb.com'+link
                Log(url)
                json="false"
            else:
                url='http://mlb.mlb.com/ws/search/MediaSearchService?'+s_query+'&hitsPerPage=200&src=vpp'
                json='true'
                Log(url)
            
            listname=NestedListDict.get(name)
            if listname == None:
                listname=[]
                NestedListDict[name]=listname
            listname.append((name,url,json))
        
        Log(NestedListDict)
            
                
        dir.Append(Function(DirectoryItem(NestedList,title=mainname), PassedDict=NestedListDict,topic=id))
        
    return dir
    
####################################################################################################
def NestedList(sender, PassedDict,topic):
    dir = MediaContainer(title2=sender.itemTitle)     
    NestedListDict=dict()
    NestedListDict=PassedDict
    names=NestedListDict.keys()
    for item in names:
        Log(item)
        url=NestedListDict[item][0][1]
        name=NestedListDict[item][0][0]
        if NestedListDict[item][0][2]=="true":
            dir.Append(Function(DirectoryItem(JSONList, title=name), url=url,topic=topic))
        else:
            dir.Append(Function(DirectoryItem(XMLList, title=name), url=url,topic=topic))
    return dir
    
####################################################################################################
def JSONList(sender, url,topic):
    dir = MediaContainer(title2=sender.itemTitle)  
    topic=topic

#Reads in JSON list
    try:
        dict=JSON.ObjectFromURL(url, headers={'Referer':'http://mlb.mlb.com'})
        vidList=dict['mediaContent']
        for vid in vidList:
            id=vid['contentId']
            name=vid['title']
            sub=vid['blurb']
            sub=sub.split(': ')[-1]
            desc=vid['bigBlurb']
            thumb=vid['thumbnails'][0]['src']
            duration=vid['duration']
            url=MLB_Video+id+'&topic_id='+topic+'&c_id=mlb'
            Log('added item: '+name + ' | '+ sub + ' | '+ desc + ' | '+ thumb + ' | '+ ' | '+ url)

            dir.Append(WebVideoItem(url, title=name, subtitle=sub,summary=desc,thumb=thumb))    
            Log(len(dir))
            Log(dir)
    except: pass
    return dir
####################################################################################################
def XMLList(sender, url,topic):
    dir = MediaContainer(title2=sender.itemTitle)        
    topic=topic
#Reads in XML list

    content=XML.ElementFromURL(url, headers={'Referer':'http://mlb.mlb.com'})
    for vid in content.xpath('./item'):
        id=vid.get('content_id')
        name=vid.xpath('headline')[0].text
        sub=vid.xpath('blurb')[0].text
        desc=vid.xpath('big_blurb')[0].text
        thumb=vid.xpath('images/image')[0].text
        duration=vid.xpath('duration')[0].text
        url=MLB_Video+id+'&topic_id='+topic+'&c_id=mlb'
        Log('added item: '+name + ' | '+ sub + ' | '+ desc + ' | '+ thumb + ' | '+ ' | '+ url)

        dir.Append(WebVideoItem(url, title=name, subtitle=sub,summary=desc,thumb=thumb))    

    return dir