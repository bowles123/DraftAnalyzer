class Prospect:   
    def __init__(self, name, position, stats, combine, score = 0.0):
        self.name = name
        self.position = position
        self.stats = stats
        self.combine = combine
        self.score = score

    def printProspect(self):
        print("%s - %s [%f]" % (self.name, self.position, self.score))

    def equals(self, prospect):
        if prospect == None:
            return False
        
        if self.name == prospect.name:
            if self.position == prospect.position:
                return True
        return False

class Team:
    def __init__(self, name, pickNum, needs, pick = None):
        self.name = name
        self.pickNum = pickNum
        self.needs = needs
        self.pick = pick

    def printTeam(self):
        print("%d. %s, Needs: %s" % (self.pickNum, self.name, self.printNeeds()))

    def printNeeds(self):
        return ''.join(self.needs)

class NaivePredictor:
    def __init__(self, teams, prospects):
        self.teams = teams
        self.prospects = prospects
        self.combineAverages = []
        self.statsAverages = []

    def calculateStatsAverages(self):
        rate = py = ptds = intp = avgRush = rushY = carries = rushtds = 0.0
        avgCatch = catchY = receptions = catchtds = tackles = sacks = 0.0
        ints = pd = ff = 0.0
        ratei = pyi = ptdsi = intpi = avgRi = ryi = ci = rtdsi = avgCi = 0
        cyi = ri = ctdsi = ti = si = intsi = pdi = ffi = 0

        for prospect in self.prospects:
            if len(filter(lambda num: num != '0', prospect.stats)) == 0:
                continue
            
            if prospect.position == 'QB':
                ratei = pyi = ptdsi = intpi = ratei + 1

                rate = rate + float(prospect.stats[0])
                py = py + float(prospect.stats[1])
                ptds = ptds + float(prospect.stats[2])
                intp = intp + float(prospect.stats[3])

            if prospect.position == 'WR' or prospect.position == 'RB':
                avgRi = ryi = ci = rtdsi = avgCi = cyi = ri = ctdsi = avgRi + 1

                avgRush = avgRush + float(prospect.stats[4])
                rushY = rushY + float(prospect.stats[5])
                carries = carries + float(prospect.stats[6])
                rushtds = rushtds + float(prospect.stats[7])
                avgCatch = avgCatch + float(prospect.stats[8])
                catchY = catchY + float(prospect.stats[9])
                receptions = receptions + float(prospect.stats[10])
                catchtds = catchtds + float(prospect.stats[11])

            if prospect.position == 'TE':
                avgCi = cyi = ri = ctdsi = avgCi + 1

                avgCatch = avgCatch + float(prospect.stats[8])
                catchY = catchY + float(prospect.stats[9])
                receptions = receptions + float(prospect.stats[10])
                catchtds = catchtds + float(prospect.stats[11])

            else:
                ti = si = intsi = pdi = ffi = ti + 1

                tackles = tackles + float(prospect.stats[12])
                sacks = sacks + float(prospect.stats[13])
                ints = ints + float(prospect.stats[14])
                pd = pd + float(prospect.stats[15])
                ff = ff + float(prospect.stats[16])

        self.statsAverages.append(rate / ratei)
        self.statsAverages.append(py / pyi)
        self.statsAverages.append(ptds / ptdsi)
        self.statsAverages.append(intp / intpi)
        self.statsAverages.append(avgRush / avgRi)
        self.statsAverages.append(rushY / ryi)
        self.statsAverages.append(carries / ci)
        self.statsAverages.append(rushtds / rtdsi)
        self.statsAverages.append(avgCatch / avgCi)
        self.statsAverages.append(catchY / cyi)
        self.statsAverages.append(receptions / ri)
        self.statsAverages.append(catchtds / ctdsi)
        self.statsAverages.append(tackles / ti)
        self.statsAverages.append(sacks / si)
        self.statsAverages.append(ints / intsi)
        self.statsAverages.append(pd / pdi)
        self.statsAverages.append(ff / ffi)

    def calculateCombineAverages(self):
        grades = forties = benches = verts = broads = cones = twenties = sixties = 0.0
        fi = bi = vi = bri = ci = ti = si = 0
        
        for prospect in self.prospects:
            grades = grades + float(prospect.combine[0])

            if float(prospect.combine[1]) != 0.0:
                fi = fi + 1
                forties = forties + float(prospect.combine[1])

            if float(prospect.combine[2]) != 0.0:
                bi = bi + 1
                benches = benches + float(prospect.combine[2])

            if float(prospect.combine[3]) != 0.0:
                vi = vi + 1
                verts = verts + float(prospect.combine[3])

            if float(prospect.combine[4]) != 0.0:
                bri = bri + 1
                broads = broads + float(prospect.combine[4])

            if float(prospect.combine[5]) != 0.0:
                ci = ci + 1
                cones = cones + float(prospect.combine[5])

            if float(prospect.combine[6]) != 0.0:
                ti = ti + 1
                twenties = twenties + float(prospect.combine[6])

            if float(prospect.combine[7]) != 0.0:
                si = si + 1
                sixties = sixties + float(prospect.combine[7])
            
        self.combineAverages.append(grades / len(self.prospects))
        self.combineAverages.append(forties / fi)
        self.combineAverages.append(benches / bi)
        self.combineAverages.append(verts / vi)
        self.combineAverages.append(broads / bri)
        self.combineAverages.append(cones / ci)
        self.combineAverages.append(twenties / ti)
        self.combineAverages.append(sixties / si)

    def calculateCombineScore(self, prospect):
        i = 0
        combineScore = 0.0

        for score in prospect.combine:
            score = min(float(score) / self.combineAverages[i], 1.0)
            combineScore = combineScore + score
            i = i + 1
            
        return combineScore / len(filter(
            lambda num: num != '0', prospect.combine))

    def calculateStatsScore(self, prospect):
        i = 0
        statsScore = 0.0
            
        for score in prospect.stats:
            score = min(float(score) / self.statsAverages[i], 1.0)
            statsScore = statsScore + score
            i = i + 1
        if len(filter(lambda num: num != '0', prospect.stats)) == 0:
            return 0
        return statsScore / len(filter(
            lambda num: num != '0', prospect.stats))

    def calculateScores(self, combine, stats):
        self.calculateCombineAverages()
        self.calculateStatsAverages()
        
        for prospect in self.prospects:
            if stats:
                statsScore = self.calculateStatsScore(prospect)
            else:
                statsScore = 0.0

            if combine:
                combineScore = self.calculateCombineScore(prospect)
            else:
                combineScore = 0.0

            if combine and stats:
                prospect.score = ((statsScore * 3) + (combineScore * 2)) / 5
            elif not combine:
                prospect.score = statsScore
            else:
                prospect.score = combineScore

    def predict(self, combine, stats):        
        self.calculateScores(combine, stats)
        self.prospects.sort(key=lambda prospect: prospect.score, reverse = True)
        
        for team in self.teams:
            best_prospect = self.prospects[0]
            
            for prospect in self.prospects:
                if prospect.score >= 0.85 and prospect.position in team.needs:
                    team.pick = prospect
                    self.prospects.remove(prospect)
                    break
                
            if team.pick == None:
                team.pick = best_prospect
                self.prospects.remove(best_prospect)
        self.display_predictions()
        print("%d%% of picks in team needs." % self.calculateAccuracy())

    def calculateAccuracy(self):
        inNeeds = 0
        i = 0
        
        for team in self.teams:
            if team.pick.position in team.needs:
                inNeeds = inNeeds + 1
            i = i + 1
        return (float(inNeeds) / float(len(self.teams))) * 100.0

    def display_predictions(self):
        for team in self.teams:
            if team.pick == None:
                print("%s: None." % (team.name))
            else:
                print("%d. %s: %s %s" % (team.pickNum, team.name, team.pick.position,
                      team.pick.name))
            
def initializePredictor(fileName):
    data = []
    fullTeams = []
    fullProspects = []
    
    with open(fileName) as inFile:
        data = inFile.readlines()
    year = data[0].split(' ')[1][1:-3]
    data.remove(data[0])

    string = ''.join(data)
    data = string.split('\n\nTeams (2016):\n\t')
    teams = data[1].split('\n\t')
    prospects = data[0].split('\n\t')
    prospects[0] = prospects[0][1:]

    for team in teams:
        teamData = team.split('. ')
        team = Team(teamData[1], int(teamData[0]), teamData[2])
        fullTeams.append(Team(teamData[1], int(teamData[0]), teamData[2]))

    for prospect in prospects:
        prospectData = prospect.split('. ')
        prospectData[3] = prospectData[3][1:-1]
        prospectData[4] = prospectData[4][1:-1]
        fullProspects.append(Prospect(prospectData[1], prospectData[2],
                                      prospectData[3].split(', '),
                                      prospectData[4].split(', ')))

    return NaivePredictor(fullTeams, fullProspects)
