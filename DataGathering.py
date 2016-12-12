import re
import httplib2
import urllib2
import time
import json as m_json
from bs4 import BeautifulSoup, SoupStrainer

class Prospect:
    
    def __init__(self, firstName, lastName, position, score = 0):
        self.firstName = firstName
        self.lastName = lastName
        self.position = position
        self.score = score

    def printProspect(self):
        print("%s, %s - %s [%d]" % (self.lastName, self.firstName, self.position,
                                    self.score))

class Team:
    def __init__(self, city, name, pickNum, needs, pick = None):
        self.city = city
        self.name = name
        self.pickNum = pickNum
        self.needs = needs
        self.pick = pick

    def printTeam(self):
        print("%d. %s %s Needs: %s" % (self.pickNum, self.city, self.name,
                                       self.printNeeds()))

    def printNeeds(self):
        needsString = ""
        i = 0
        
        for need in self.needs:
            i = i + 1

            if (i == len(self.needs)):
                needsString = needsString + need
            else:
                needsString = needsString + (need + ", ")
        return needsString

class Predictor:
    def __init__(self, prospects, teams):
        self.prospects = prospect
        self.teams = teams

    def predict():    
        for team in teams:
            best_prospect = prospects[0]
            
            for prospect in prospects:
                if prospect.score >= 75 and prospect.position in team.needs:
                    team.pick = prospect
                    prospects.remove(prospect)
                    break
                elif prospect.score > best_prospect.score:
                    best_prospect = prospect
                    continue
                
            if team.pick == None:
                team.pick = best_prospect
                prospects.remove(best_prospect)

    def display_predictions():
        for team in teams:
            if team.pick == None:
                print("%s %s: None." % team.city, team.name)
            else:
                print("%s %s: %s %s, %s" % team.city, team.name,
                      team.pick.firstName, team.pick.lastName,
                      team.pick.position)

## Returns list of prospect objects.
## List is sorted in terms of the prospects' scores, descending.
def getProspects():
    http = httplib2.Http()
    status, response = http.request(
        'http://www.nfl.com/news/story/0ap3000000641197/article/daniel-jeremiahs-top-50-prospects-for-2016-nfl-draft')
    soup = BeautifulSoup(response, 'html.parser')
    prospects = []
    data = []

    for span in soup.find_all('span', attrs={'class':'team-name'}):
        data.append(span.text)

    for prospect in data:
        metadata = prospect.split(' - ')
        names = metadata[0].split(' ')
        prospects.append(Prospect(names[0], names[1], metadata[1].split(', ')[0]))
    return prospects

## The index of the stats list corresponds to the index of the prospects list.
def getStatisticsScores():
    prospects = getProspects()
    statsScores = []

    for prospect in prospects:
        statsScores.append(getProspectStatsScore(prospect))
    return statsScores

def getProspectStatsScore(prospect): 
    if 'O' in prospect.position or 'C' in prospect.position:
        return 0.0
    
    http = httplib2.Http()
    status, response = http.request(
        'http://www.sports-reference.com/cfb/players/' + prospect.firstName.lower() +
        '-' + prospect.lastName.lower() + '-' + '1.html')
    soup = BeautifulSoup(response, 'html.parser')
    years = 0
    stats = []

    if soup.find('tbody') == None:
        return 0.0

    for tr in soup.find('tbody'):
        years = years + 0.5
    years = int(years)

    footer = soup.find('tfoot')
    rows = footer.findAll('td')

    for td in rows:
        if td.text != "":
            stats.append(str(td.text))
    stats.remove(stats[0])

    if prospect.position == 'QB':
        return calcQBStatsScore(float(stats[8]), float(stats[3]) / years,
                                float(stats[6]) / years, float(stats[7]),
                                float(stats[1]))

    if prospect.position == 'WR':
        return calcWRStatsScore(float(stats[2]), float(stats[1]) / years,
                                float(stats[0]) / years, float(stats[3]) / years)

    if prospect.position == 'RB':
        return calcRBStatsScore(float(stats[2]), float(stats[1]) / years,
                                float(stats[0]) / years, float(stats[3]) / years)

    if prospect.position == 'TE':
        return calcTEStatsScore(float(stats[2]), float(stats[1]) / years,
                                float(stats[0]) / years, float(stats[3]) / years)

    if prospect.position == 'DE' or prospect.position == 'DT':
        return calcDLStatsScore(float(stats[4]) / years, float(stats[2]) / years,
                                prospect.position)

    if prospect.position == 'LB' or prospect.position == 'OLB' or prospect.position == 'ILB':
        return calcLBStatsScore(float(stats[2]) / years, float(stats[4]) / years,
                                prospect.position)

    if prospect.position == 'CB' or prospect.position == 'S':
        return calcDBStatsScore(float(stats[5]) / years, float(stats[2]) / years)
        
def calcQBStatsScore(rating, pys, ptds, interceptions, attempts):
    ratingScore = rating - 55
    pysScore = pys / 38
    ptdsScore = ptds * 2.75
    intScore = abs((interceptions / attempts) * 100 - 100)
    return (ratingScore + pysScore + ptdsScore + intScore) / 4

def calcRBStatsScore(avgy, yards, carries, tds):
    avgyScore = avgy * 15
    yardsScore = yards / 14
    carriesScore = carries / 2.5
    tdsScore = tds * 6
    return (avgyScore + yardsScore + carriesScore + tdsScore) / 4

def calcWRStatsScore(avgy, yards, receptions, tds):
    avgyScore = avgy * 6
    yardsScore = yards / 12
    receptionsScore = receptions + 25
    tdsScore = tds * 7
    return (avgyScore + yardsScore + receptionsScore + tdsScore) / 4

def calcTEStatsScore(avgy, yards, receptions, tds):
    avgyScore = avgy * 6
    yardsScore = yards / 7.5
    receptionsScore = receptions * 2.5
    tdsScore = tds * 14
    return (avgyScore + yardsScore + receptionsScore + tdsScore) / 4

## Probably needs to be adjusted
def calcDLStatsScore(sacks, tackles, position = "DT"):
    if position == "DE":
        sacksScore = sacks * 8
    else:
        sacksScore = sacks * 10

    tacklesScore = tackles * 2
    return (sacksScore + tacklesScore) / 2

## Probably needs to be adjusted, at least for the 'S' position.
def calcDBStatsScore(interceptions, tackles):
    interceptionsScore = interceptions * 20
    tacklesScore = tackles * 2.5
    return (interceptionsScore + tacklesScore) / 2

## Probably needs to be adjusted.
def calcLBStatsScore(tackles, sacks, position = "LB"):
    if position == "OLB":
        sacksScore = sacks * 8
        tacklesScore = tackles * 2
    else:
        sacksScore = sacks * 12      
        tacklesScore = tackles / 1.25
        
    return (tacklesScore + sacksScore) / 2

## From NFL.com, returns list of combine results for each prospect.
## The index of the results list corresponds to the index of the prospects list.
def getCombineResults():
    prospects = getProspects()
    combineScores = []
	
    for prospect in prospects:
        query = prospect.firstName + '+' + prospect.lastName + '+combine+results'
        url = 'http://www.google.com/search?q=*&tbs=qdr:h'.replace("*", query)
        headers = {'User-Agent':'Chrome'}
        req = urllib2.Request(url, None, headers)
        pageString = urllib2.urlopen(req).read()

        ## unsure how to get the first url in search result.
        ##combineScores.append(getProspectCombineScore(results[0]))
        time.sleep(5)

## Returns the score for a player's combine
def getProspectCombineScore(url):
    http = httplib2.Http()
    status, response = http.request(url)
    soup = BeautifulSoup(response, 'html.parser')
    grade = f = b = v = br = c = t = s = 0.0
    events = 0

    grade = soup.find('span', attrs={'class':'grade'})
    if grade != None:
        grade = float(grade.em.text)

    f = getEventResult('forty-yard-dash', url)
    
    if f != None:
        events = events + 1

    b = getEventResult('bench-press', url)

    if b != None:
        events = events + 1

    v = getEventResult('vertical-jump', url)

    if v != None:
        events = events + 1

    br = getEventResult('broad-jump', url)

    if br != None:
        events = events + 1

    c = getEventResult('three-cone-drill', url)

    if c != None:
        events = events + 1

    t = getEventResult('twenty-yard-shuttle', url)

    if t != None:
        events = events + 1

    s = getEventResult('sixty-yard-shuttle', url)

    if s != None:
        events = events + 1

    return calcCombineScore(grade, f, b, v, br, c, t, s, events)

## Grabs the result of a player's event
def getEventResult(eventName, url):
    http = httplib2.Http()
    status, response = http.request(url)
    soup = BeautifulSoup(response, 'html.parser')

    result = soup.find('li', attrs={'class':eventName})
    if result != None:
        result = float(result.h5.text.split(' ')[0])
    else:
        result = soup.find('li', attrs={'class':eventName + ' top-performer'})
        if result != None:
            result = float(result.h5.text.split(' ')[0])
    return result

## Calculates a player's combine score based on each event and their grade
def calcCombineScore(grade, fourty_time, reps, verticalInches, broadInches,
                     cone_time, twenty_time, sixty_time, totalEvents):
    gradeScore = grade * 18
    fourtyScore = fourty(fourty_time)
    benchScore = bench(reps)
    verticalScore = vertical(verticalInches)
    broadScore = broad(broadInches)
    coneScore = cone(cone_time)
    twentyScore = twentyShuttle(twenty_time)
    sixtyScore = sixtyShuttle(sixty_time)
    return (fourtyScore + benchScore + verticalScore + broadScore + coneScore +
            twentyScore + sixtyScore +  gradeScore) / (totalEvents + 1.5)

# Normalizes forty-yard-dash time
def fourty(time):
    if time == None:
        return 0
    return (4.24 / time) * 100

# Normalizes number of bench-presses
def bench(reps):
    if reps == None:
        return 0
    return reps * 3

# Normalizes height for vertical-jump
def vertical(inches):
    if inches == None:
        return 0
    return inches * 2.2

# Normalizes height for broad-jump
def broad(inches):
    if inches == None:
        return 0
    return inches / 1.5

# Normalize three-cone-drill time
def cone(time):
    if time == None:
        return 0
    return (6.4 / time) * 100

# Normalizes twenty-yard-shuttle time
def twentyShuttle(time):
    if time == None:
        return 0
    return (3.81 / time) * 100

# Normalizes sixty-yard-shuttle time
def sixtyShuttle(time):
    if time == None:
        return 0
    return (10.72 / time) * 100

## Returns list of teams sorted by pick number, descending.
def getDraftOrder():
    http = httplib2.Http()
    status, response = http.request(
        'http://www.nfl.com/news/story/0ap3000000551301/article/2016-nfl-draft-order-and-needs-for-every-team')
    soup = BeautifulSoup(response, 'html.parser')
    teams = []

    for b in soup.find_all('b'):
        if b.a != None:
            teams.append(b.a.text)

    status, response = http.request(
        'http://www.nfl.com/news/story/0ap3000000572264/article/2016-nfl-draft-order-and-needs-nos-1120')
    soup = BeautifulSoup(response, 'html.parser')

    for b in soup.find_all('b'):
        if b.a != None:
            teams.append(b.a.text)

    status, response = http.request(
        'http://www.nfl.com/news/story/0ap3000000572265/article/2016-nfl-draft-order-and-needs-playoff-teams')
    soup = BeautifulSoup(response, 'html.parser')

    for b in soup.find_all('b'):
        if b.a != None:
            teams.append(b.a.text)
    return teams

## Returns a list of Team objects with all their given information
def getTeams():
    http = httplib2.Http()
    status, response = http.request(
        'http://www.nfl.com/news/story/0ap3000000551301/article/2016-nfl-draft-order-and-needs-for-every-team')
    soup = BeautifulSoup(response, 'html.parser')
    teams = getDraftOrder()
    fullTeam = []
    fullTeams = []
    needs = []
    shortNeeds = []
    i = 1

    for team in teams:
        topNeed = ''
        otherNeeds = ''
        
        if i == 11:
            status, response = http.request(
                'http://www.nfl.com/news/story/0ap3000000572264/article/2016-nfl-draft-order-and-needs-nos-1120')
            soup = BeautifulSoup(response, 'html.parser')
        if i == 21:
            status, response = http.request(
                'http://www.nfl.com/news/story/0ap3000000572265/article/2016-nfl-draft-order-and-needs-playoff-teams')
            soup = BeautifulSoup(response, 'html.parser')

        for p in soup.find_all('p'):
            if team in p.getText() and team == teams[i - 1]:
                for b in p:
                    if 'Top need:' in b:
                        topNeed = next(b.next_siblings)
                    elif 'Other needs:' in b:
                        otherNeeds = next(b.next_siblings)
                        
        needs.append(topNeed)
        needs.extend(otherNeeds.split(','))

        for need in needs:
            temp = need.upper().split(' ')
            temp = [space for space in temp if space != '']

            if len(temp) == 2:
                if 'BACK' in temp[1] and temp[1] != 'BACK':
                    need = temp[0][0] + temp[1][0] + 'B'
                else:
                    need = temp[0][0] + temp[1][0]

            if len(temp) == 1:
                if 'BACK' in temp[0]:
                    need = temp[0][0] + 'B'
                else:
                    need = temp[0][0]

            if need == 'ER':
                need = 'DE'
            if need == 'PR':
                need = 'DL'

            shortNeeds.append(need)
        
        fullTeam = team.split(' ')
        fullTeams.append(Team(fullTeam[0], fullTeam[1], i, shortNeeds))
        shortNeeds = []
        needs = []
        i = i + 1

    return fullTeams

## Scores the prospect based on stats and combine results
## Stats account for 60% of the score while the combine accounts for 40%
def scoreProspects():
    stats = getStatisticsScores()
    combine = getCombineResults()
    prospects = getProspects()
    i = 0

    for prospect in prospects:
        prospect.score = ((stats[i] * 3) + (combine[i] * 2)) / 7
        i = i + 1
