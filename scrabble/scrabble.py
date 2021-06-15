#! python

import shelve, re, time, random, poplib, smtplib


from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


import os
os.chdir('C:\\Python3.7\\scrabble')


"""

This is an old project, poorly documented. It ultimately worked
as email based scrabble, where you could send a carefully formatted
email to an automated account and it would play the word and then have
the next person play. Messy code, beware. Also my first attempts at object
orientation.


"""

''' how it will work

it will open up the existing board.
the default board should be stored somewhere.


it will check the email. If it has a reply, it will open it up and prepare a
reply with the updated board. if it has a reply that isn't the right turn then
it will ignore it or respond with a WHAT ARE YOU DOING.

when it recieves the reply, it will calculate the points that the reply is worth
--parse the reply by regex, pass the input into the board update function
--if the parse fails, then it will reply to the sender that the parse failed.

format for replies: across[A7]:boogers OR down[C3]:fibbonacc[i]


it will add that to the score, and then give out new letters. it will then toggle
turns to the next person.
--it will compare the reply to the existing board
----determine which letters are existing and which are new
----point values for each
----add to score.
----update board.

it will notify the other players of the moves played.
--send new board to all players, notify turn


On game start, it will write out a startup message with a blank board and say
the order of turns.


'''

class Mailchecker():
    """ THE THING THAT CHECKS THE EMAILS. I'M NOT SURE OF ALL THAT IT DOES."""
    def __init__(self):
        M = poplib.POP3_SSL('pop.gmail.com',995)

        assert False
        M.user('bilbobaggins@gmail.com')# redacted
        M.pass_('jimmyjohns') # redacted

        
        self.regexdictionary={'newgame':re.compile(r'\|(NEWGAME)|(newgame)\|',re.I),'wordplayed':re.compile(r'GID\d{10}', re.I)}
        self.server=M
    
    def list(self,which=None):
        if which:
            return self.server.list(which)
        else:
            return self.server.list()

    def compile_email(self, which):
        email=self.server.retr(which)[1]
        emailout=b''
        for x in email:
            emailout+=x
        emailout=str(emailout, 'UTF-8')
        emailout=emailout.split("You've been put into a new game of Scrabble!")[0]
        return emailout

    def interpret_email(self,email):
        emailtype=None
        for x in self.regexdictionary.items():
            emailtype=x[1].search(email)
            if emailtype:
                emailtype=emailtype.group()
            if emailtype:
                emailtype=x[0]
                break
        return emailtype


    def CHECK_THE_MAAAIIIIIILLLLLL(self):
        emails=self.list()[1]
        if emails:
            email=self.compile_email(1)
            emailtype=self.interpret_email(email)
            print(emailtype)
            try:
                if emailtype=='newgame':
                    game=Game()
                    dictgex=re.compile(r'''\{([a-zA-Z]+:[a-zA-Z0-9\._]+@[a-zA-Z0-9]+\.[a-zA-Z0-9]+,*)*\}''',re.I)
                    playerdict=dictgex.search(email).group().strip('{}')
                    playertups=playerdict.split(',')
                    for x in playertups:
                        pair=x.split(':')
                        game.add_player(pair[0],pair[1])
                    game.begin()

                    smtpObj=smtplib.SMTP('smtp.gmail.com',)
                    smtpObj.ehlo()
                    smtpObj.starttls()
                    smtpObj.login('schmelzerprime@gmail.com','battlefront')
                    fromVar='schmelzerprime@gmail.com'

                    boarddata=game.board.output()
                    html_opener = """\
    <html>
    <font face="Courier New, Courier, monospace">
      <head></head>
      <body>
        <p>SCRABBLE<br><br>
        
           """
                    html_closer = """\
        </p>
      </body>
    </font>
    </html>
    """

                    for x in game.players:
                        text='\n\n'
                        msg = MIMEMultipart('alternative')
                        msg['Subject'] = 'Scrabble: New Game! '+game.id
                        msg['From'] = fromVar
                        msg['To'] = x[1]
                        text+="You've been put into a new game of Scrabble!\n\nThe players are:\n"+('\n'.join(playertups)).replace(':',' : ')
                        html =text.replace('\n','<br>')
                        text+='\n\n'+boarddata[0]+'\n\n'
                        html+=('\n\n'+boarddata[1]+'\n\n').replace('\n','<br>')

                        text+='\n\nFirst to play is: '+game.turn[0].upper()+'\n\n'
                        html+=('\n\nFirst to play is: '+game.turn[0].upper()+'\n\n').replace('\n','<br>')

                        text+='Your hand:\n'+'_'*(len(game.hands[x[0]])+2)+'\n-'+game.hands[x[0]]+'-\n'
                        html+=('Your hand:\n'+'_'*(len(game.hands[x[0]])+2)+'\n-'+game.hands[x[0]]+'-\n').replace('\n','<br>')

                        text+='\n\n To play a word, respond to this email (or future emails) with what you\'d like to play in the following format:\n\n(across[A7]:sandwich)\n\n If you have a blank, format is :\n\n(across[A7]:sa[n]dwich)'
                        html+=('\n\n To play a word, respond to this email (or future emails) with what you\'d like to play in the following format:\n\n(across[A7]:sandwich)\n\n If you have a blank, format is :\n\n(across[A7]:sa[n]dwich)').replace('\n','<br>')

                        htmlTotal=html_opener+html+html_closer
                        part1 = MIMEText(text, 'plain')
                        part2 = MIMEText(html, 'html')
                        msg.attach(part1)
                        msg.attach(part2)

                        
                        smtpObj.sendmail(fromVar,x[1],msg.as_string())
                    smtpObj.quit()

                elif emailtype=='wordplayed':
                    addressgex=re.compile(r'From:[\s\w]+<[\w\d]+@\w+.\w+>',re.I)
                    fromAddress=addressgex.findall(email)[0]
                    trueaddress=re.compile(r'<.*>')
                    trueaddress=trueaddress.findall(fromAddress)[0]
                    fromAddress=trueaddress.strip('<>')
                    HANDLER(email,fromAddress)
                else:
                    self.server.rset()
            except Exception as e:
                print(e,email)
            'pause'
            self.server.rset()
            self.server.quit()
            self.__init__()
            
        
        
        
        

def HANDLER(email,address):
    #parse parse parse
    #mail checker passed you the string of the email.
    
    
    #regurgitates definitions and updates.
    gamedic=shelve.open('gamedic')
    idregex=re.compile(r'GID\d{10}')

    
    rawWord=re.compile(r'\(((across)|(down))\[\w\d\]:((\[\w\])|(\w)|(\s))+\)', re.I)

    errors=False

    try:

        try:
            gameID=idregex.findall(email)[0] #is a string
        except:
            gamedic.close()
            raise BaseException("Unable to find game ID. Make sure the Game ID number is in the subject of the email; e.g. GID1234567890.\n\n At the very least, it should be in the email you recieved at the beginning of the game.")
        game=gamedic[gameID]
        gamedic.close()
        try:
            player=None
            for x in game.players:
                if address==x[1]:
                    player=x
            assert player
        except:
            raise Exception("Invalid player, player not found in game.")
        try:
            rawWord=rawWord.search(email).group().strip('()').replace(' ','')
        except:
            raise Exception("Unable to find words to be played. Format is :\n\n (across[A7]:sandwich)\n\n If you have a blank, format is :\n\n(across[A7]:sa[n]dwich)")
        definitions,boarddata=game.play(player,rawWord,game.board)
        gamedic=shelve.open('gamedic')
        gamedic[gameID]=game
        gamedic.close()
    except BaseException as e:
        gamedic.close()
        errors=True
        errmsg=str(e.with_traceback(None))
    except Exception as e:
        gamedic.close()
        errors=True
        errmsg=str(e.with_traceback(None))+'\n\n'+game.id        
        
    response=''
    smtpObj=smtplib.SMTP('smtp.gmail.com',)
    smtpObj.ehlo()
    smtpObj.starttls()
    smtpObj.login('schmelzerprime@gmail.com','battlefront')
    fromVar='schmelzerprime@gmail.com'
    text='\n\n'
    
    html_opener = """\
<html>
<font face="Courier New, Courier, monospace">
  <head></head>
  <body>
    <p>SCRABBLE<br><br>
    
       """
    html_closer = """\
    </p>
  </body>
</font>
</html>
"""





    if errors:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'Scrabble: Turn failed. '
        msg['From'] = fromVar
        msg['To'] = address
        text+="An error occured:"+errmsg+"\n\nPlease try again."
        html =text.replace('\n','<br>')
        htmlTotal=html_opener+html+html_closer

        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(htmlTotal, 'html')
        msg.attach(part1)
        msg.attach(part2)

        
        smtpObj.sendmail(fromVar,address,msg.as_string())
        smtpObj.quit()
        print(errmsg)
    else:

        alert=''
        if not game.bag:
            alert='ALERT: The bag is empty. This is the final round of turns!\n\n'
        text+="Word played successfully.\n\n"+boarddata[0]+"\n\n"
        html="Word played successfully.\n\n"+boarddata[1]+"\n\n".replace('\n','<br>')
        for x in definitions:
            html+=x[0].upper()+' : '+x[1]+'<br>'
            text+=x[0].upper()+' : '+x[1]+'\n'
            
        scoreboardstring=''
        for x in game.scoreboard.keys():
            scoreboardstring+=x.upper().ljust(20)+' : '+str(game.scoreboard[x])+'\n'
        text+=scoreboardstring+'\n\nNext to play is: '+game.turn[0].upper()+'\n\n'
        text+=alert
        html+=(scoreboardstring+'\n\nNext to play is: '+game.turn[0].upper()+'\n\n').replace('\n','<br>')
        html+=alert.replace('\n','<br>')




        
        
        
        pretext=text
        otherplayers=game.players[:]
        otherplayers.remove(player)
        for playertup in otherplayers:
            msg = MIMEMultipart('alternative')

            msg['To']=playertup[1]
            msg['Subject']='Scrabble: Word played: '+rawWord +'. ' + gameID


            text+='Your hand:\n'+'_'*(len(game.hands[playertup[0]])+2)+'\n-'+game.hands[playertup[0]]+'-\n'
            html+=('Your hand:\n'+'_'*(len(game.hands[playertup[0]])+2)+'\n-'+game.hands[playertup[0]]+'-\n').replace('\n','<br>')
            
            htmlTotal=html_opener+html+html_closer
            part1 = MIMEText(text, 'plain')
            part2 = MIMEText(htmlTotal, 'html')
            msg.attach(part1)
            msg.attach(part2)

            
            smtpObj.sendmail(fromVar,playertup[1],msg.as_string())

        #special email to the player that just played
        text=pretext
        text+='Your hand:\n'+'_'*(len(game.hands[player[0]])+2)+'\n-'+game.hands[player[0]]+'-\n'
        html+=('Your hand:\n'+'_'*(len(game.hands[player[0]])+2)+'\n-'+game.hands[player[0]]+'-\n').replace('\n','<br>')
        htmlTotal=html_opener+html+html_closer

        msg = MIMEMultipart('alternative')

        msg['To']=player[1]
        msg['Subject']='Scrabble: Word played successfully: '+rawWord +'. ' + gameID
        
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(htmlTotal, 'html')
        msg.attach(part1)
        msg.attach(part2)

        
        smtpObj.sendmail(fromVar,player[1],msg.as_string())





            
        smtpObj.quit()
        print('HANDLED!')





class Game:
    """The class that stores the entire scrabble game. Score, players, tiles in the bag, everything."""
    def __init__(self):
        #default board
        self.id='GID'+str(int(time.time()))
        self.bag=list('e'*12+'a'*9+'i'*9+'o'*8+'n'*6+'r'*6+'t'*6+'l'*4+'s'*4+'u'*4+'g'*3+'d'*4+'bcmp'*2+'fhvwy'*2+'kjxqz'+'  '.upper())
        self.bag.sort()
        self.bag=''.join(self.bag)
        self.players=[]
        self.scoreboard={}
        self.ongoing=False
        self.hands={}
        self.board=Board()
        self.turncount=0
        self.turn=[] #stored as a player tuple
        self.movehistory=[]
        gamedic=shelve.open('gamedic')
        gamedic[self.id]=self
        gamedic.close()
        
        

    def add_player(self,name,email):
        if not self.ongoing:
            self.players.append((name,email))
            self.scoreboard.setdefault(name,0)
            self.hands.setdefault(name,'')
            gamedic=shelve.open('gamedic')
            gamedic[self.id]=self
            gamedic.close()
        else:
            raise Exception('\n\nThe game has already begun, you cannot add any new players.')


    def begin(self):
        self.ongoing=True
        for player in self.players:
            self.fillhand(player[0])
        random.shuffle(self.players)
        self.turn=self.players[self.turncount%len(self.players)]
        gamedic=shelve.open('gamedic')
        gamedic[self.id]=self
        gamedic.close()
        
    def fillhand(self,player):
        newtiles=min((len(self.bag),7-len(self.hands[player])))
        for x in range(newtiles):
            self.hands[player]+=self.bag[random.randint(0,len(self.bag)-1)]
        self.hands[player]=self.hands[player].upper()
            
    def play(self,player, rawWord,board_obj):
        player=player[0]
        alpha='abcdefghijklmnopqrstuvwxyz'.upper()
        wordtup=rawWord.upper().strip().split(':')
        if 'ACROSS' == wordtup[0][:6]:
            direction='ACROSS'
        elif 'DOWN' == wordtup[0][:4]:
            direction='DOWN'
        else:
            raise Exception("\n\nInvalid input: direction uncertain.")
        startgex=re.compile(r'\[\w\d*\]',re.I)
        start=startgex.findall(wordtup[0])[0].strip('[]')
        if not start[0].isalpha() or not start[1].isdecimal():
            raise Exception("\n\nInvalid input: starting tile uncertain.")
        start=(start[0],int(start[1:])-1)
        if direction=="ACROSS":
            if len(wordtup[1].replace('[','').replace(']',''))>15:
                raise Exception("\n\nInvalid input: word is longer than the board.")
            elif int(alpha.index(start[0]))+len(wordtup[1])>=15:
                raise Exception("\n\nInvalid input: word goes off of the board.")
        elif direction=='DOWN':
            if len(wordtup[1].replace('[','').replace(']',''))>15:
                raise Exception("\n\nInvalid input: word is longer than the board.")
            elif start[1]+len(wordtup[1])>=15:
                raise Exception("\n\nInvalid input: word goes off of the board.")
        else:
            raise Exception('\n\nDirection is supposed to be figured out by now, c\'mon')


        ################################
        blankFinder=re.compile(r'\[\w\]',re.I)
        blanksInWord=blankFinder.findall(wordtup[1])
        lettersOfWords=wordtup[1]
        lettersBurned=lettersOfWords
        for x in blanksInWord:
            lettersBurned=lettersBurned.replace(x,' ',1)
            lettersOfWords=lettersOfWords.replace('[','',1).replace(']','',1)
        emptySpaces=['  ','3L','2L','3W','2W']

        potentialBoard={x:board_obj.board[x][:] for x in list(board_obj.board.keys())}

        relevant_tiles=[]
        if direction=='ACROSS':
            for x in range(len(lettersOfWords)):
                location=alpha[alpha.index(start[0])+x]+str(start[1])
                existing_value=potentialBoard[location[0]][int(location[1:])]
                relevancy='down'
                if existing_value==' '+lettersOfWords[x]:
                    relevancy='irrel'
                    lettersBurned=lettersBurned.replace(lettersOfWords[x],'',1)
                tile=(location,' '+lettersOfWords[x],existing_value,relevancy)
                if x==0:
                    relevant_tiles.append(tuple(list(tile)[:-1]+['ACROSS']))
                if not (potentialBoard[location[0]][int(location[1:])] in emptySpaces or lettersOfWords[x]==potentialBoard[location[0]][int(location[1])].strip()):
                    raise Exception('\n\nInvalid input: word placement disagrees with existing words.')
                else:
                    potentialBoard[location[0]][int(location[1:])]=' '+lettersOfWords[x]
                    relevant_tiles.append(tile)
        elif direction=='DOWN':
            for x in range(len(lettersOfWords)):
                location=start[0]+str(start[1]+x)
                existing_value=potentialBoard[location[0]][int(location[1:])]
                relevancy='ACROSS'
                if existing_value==' '+lettersOfWords[x]:
                    relevancy='irrel'
                    lettersBurned=lettersBurned.replace(lettersOfWords[x],'',1)
                tile=(location,' '+lettersOfWords[x],existing_value,relevancy)
                if x==0:
                    relevant_tiles.append(tuple(list(tile)[:-1]+['down']))
                if not (potentialBoard[location[0]][int(location[1:])] in emptySpaces or lettersOfWords[x]==tile[2].strip()):
                    raise Exception('\n\nInvalid input: word placement disagrees with existing words.')
                else:
                    potentialBoard[location[0]][int(location[1:])]=' '+lettersOfWords[x]
                    relevant_tiles.append(tile)



        #board parsing
        centered=False
        words_for_later=[]
        for x in relevant_tiles:
            if x[3]=='irrel':
                continue
            if x[0]=='H7':
                centered=True
            line=[]
            direction=x[3]
            if direction=='ACROSS':
                tile=('A',int(x[0][1]))
                while tile[0]!='P':#end condition
                    tup=(tile,potentialBoard[tile[0]][tile[1]],board_obj.board[tile[0]][tile[1]])#(location, letter, previous,
                    line.append(tup)
                    tile=(alpha[alpha.index(tile[0])+1],tile[1])#move to the next        
            else:
                tile=(x[0][0],0)
                while tile[1]!=15:#end condition
                    tup=(tile,potentialBoard[tile[0]][tile[1]],board_obj.board[tile[0]][tile[1]])#(location, letter, previous,
                    line.append(tup)
                    tile=tile[0],tile[1]+1#move to the next
            #now we have the whole line


            words=[]
            word=[]
            for y in line:
                if y[1] in emptySpaces:
                    words.append(word)
                    word=[]
                else:
                    word.append(y)
            words.append(word)
            words=list(filter(lambda x:len(x)>1,words))
            for word in words:
                for lettertup in word:
                    if lettertup[1]!=lettertup[2]:
                        words_for_later.append(word)
                        break
        if self.turncount==0 and not centered:
            raise Exception("Invalid input:\n\nThe first played word must go through the center of the board, specifically H7.")
        if not words_for_later:
            raise Exception("Invalid input:\n\nNo new words were found.")
        


        
            #now we need to make each word into a legit string, a definition, and a point value.
        scoredict={'A': 1, 'B': 3, 'C': 3, 'D': 2, 'E': 1, 'F': 4, 'G': 2, 'H': 4, 'I': 1, 'J': 8, 'K': 5, 'L': 1, 'M': 3, 'N': 1, 'O': 1, 'P': 3, 'Q': 10, 'R': 1, 'S': 1, 'T': 1, 'U': 1, 'V': 4, 'W': 4, 'X': 8, 'Y': 4, 'Z': 10}
        final_word_list=[]
        multre=re.compile(r'\d\w',re.I)
        connected=False
        for word in words_for_later:
            wordString=''
            score=0
            multiplier=1
            for lettertup in word:
                if lettertup[1]==lettertup[2]:
                    connected=True
                wordString+=lettertup[1].strip()
                score+=scoredict[lettertup[1].strip()]
                bonusgex=re.compile(r'\d\w')
                bonus=bonusgex.fullmatch(lettertup[2])
                if bonus:
                    bonus=bonus.group()
                    if 'W' in bonus:
                        multiplier*=int(bonus[0])
                    elif 'L' in bonus:
                        score+=scoredict[lettertup[1].strip()]*(int(bonus[0])-1)
            score*=multiplier
            isWord=False
            try:
                relDict=open(wordString[:2]+'.txt')
                relDict=relDict.readlines()
                for y in range(len(relDict)):
                    relDict[y]=relDict[y].split('\t')
                for y in relDict:
                    if wordString==y[0]:
                        isWord=True
                        defn=y[1].strip('\n\'"')
                if not isWord:
                    raise Exception("Invalid input:\n\nPlayed word is not a word --- "+wordString+'.')
            except:
                raise Exception("Invalid input:\n\nPlayed word is not a word --- "+wordString+'.')
            final_word_list.append((wordString,defn,score))


        if not connected and self.turncount!=0:
            raise Exception("Invalid input:\n\nWord played is not connected to the other words on the board.")
        turnscore=sum([x[2] for x in final_word_list])
        
        if len(lettersBurned)==7:
            turnscore+=50
            
        for x in lettersBurned:
            if x not in self.hands[player]:
                raise Exception("Invalid input:\n\nYour hand doesn't have the letters needed to play that word.")
            self.hands[player]=self.hands[player].replace(x,'',1)
        self.fillhand(player)

        


        self.scoreboard[player]+=turnscore
        words_n_defs=[x[:2] for x in final_word_list]
        
        self.board.board=potentialBoard
        self.turncount+=1
        turn=self.turncount%len(self.players)
        self.turn=self.players[turn]
        self.movehistory.append((player,lettersOfWords,turnscore))
        

        return words_n_defs, self.board.output()
        
        
class Board:
    """ The board. Holds all played moves in a dictionary, will have functions for playing words
and stuff."""
    def __init__(self):
        self.board={'A': ['3W', '  ', '  ', '2L', '  ', '  ', '  ', '3W', '  ', '  ', '  ', '2L', '  ', '  ', '3W'], 'B': ['  ', '2W', '  ', '  ', '  ', '3L', '  ', '  ', '  ', '3L', '  ', '  ', '  ', '2W', '  '], 'C': ['  ', '  ', '2W', '  ', '  ', '  ', '2L', '  ', '2L', '  ', '  ', '  ', '2W', '  ', '  '], 'D': ['2L', '  ', '  ', '2W', '  ', '  ', '  ', '2L', '  ', '  ', '  ', '2W', '  ', '  ', '2L'], 'E': ['  ', '  ', '  ', '  ', '2W', '  ', '  ', '  ', '  ', '  ', '2W', '  ', '  ', '  ', '  '], 'F': ['  ', '3L', '  ', '  ', '  ', '3L', '  ', '  ', '  ', '3L', '  ', '  ', '  ', '3L', '  '], 'G': ['  ', '  ', '2L', '  ', '  ', '  ', '2L', '  ', '2L', '  ', '  ', '  ', '2L', '  ', '  '], 'H': ['3W', '  ', '  ', '2L', '  ', '  ', '  ', '2W', '  ', '  ', '  ', '2L', '  ', '  ', '3W'], 'I': ['  ', '  ', '2L', '  ', '  ', '  ', '2L', '  ', '2L', '  ', '  ', '  ', '2L', '  ', '  '], 'J': ['  ', '3L', '  ', '  ', '  ', '3L', '  ', '  ', '  ', '3L', '  ', '  ', '  ', '3L', '  '], 'K': ['  ', '  ', '  ', '  ', '2W', '  ', '  ', '  ', '  ', '  ', '2W', '  ', '  ', '  ', '  '], 'L': ['2L', '  ', '  ', '2W', '  ', '  ', '  ', '2L', '  ', '  ', '  ', '2W', '  ', '  ', '2L'], 'M': ['  ', '  ', '2W', '  ', '  ', '  ', '2L', '  ', '2L', '  ', '  ', '  ', '2W', '  ', '  '], 'N': ['  ', '2W', '  ', '  ', '  ', '3L', '  ', '  ', '  ', '3L', '  ', '  ', '  ', '2W', '  '], 'O': ['3W', '  ', '  ', '2L', '  ', '  ', '  ', '3W', '  ', '  ', '  ', '2L', '  ', '  ', '3W']}

    def show(self):
        alpha='abcdefghijklmno'.upper()
        firstline='   -'+'- - '.join(alpha)
        secondline='_'*len(firstline)
        print(firstline,secondline,sep='\n')
        for y in range(15):
            line=[]
            for x in list(self.board.keys()):
                line.append(self.board[x][y])
            line=str(y+1).rjust(2)+'|'+'   '.join(line)+'\n'
            print(line)

    def output(self):
        emptySpaces=['  ','3L','2L','3W','2W']
        alpha='abcdefghijklmno'.upper()
        html='<table><tr><th></th><th><b>'+'</b></th><th><b>'.join(alpha)+'</b></th></tr>'
        firstline='   -'+'- - '.join(alpha)
        secondline='_'*len(firstline)
        linelist=firstline+'\n'+secondline+'\n'
        for y in range(15):
            htmlline='<tr><th>'+str(y+1)+'</th>'
            line=[]
            for x in list(self.board.keys()):
                tilevalue=self.board[x][y]
                line.append(tilevalue)
                if tilevalue not in emptySpaces:
                    htmlline+='<td><b>'+tilevalue+'</b></td>'
                else:
                    htmlline+='<td>'+tilevalue+'</td>'
            line=str(y+1).rjust(2)+'|'+'   '.join(line)
            linelist+=line+'\n\n'
            htmlline+='</tr>'
            html+=htmlline
        html+='</table>'
        return linelist,html
        

def generate_board():
    board={}
    alpha='abcdefghijklmno'.upper()
    for x in range(15):
        board.setdefault(alpha[x],['  ' for g in range(15)])
    for x in range(15):
        board[alpha[x]][x]='2W'
        board[alpha[14-x]][x]='2W'
    for x in ['A','H','O']:
        for y in [0,7,14]:
            board[x][y]='3W'
    for x in ['F','J']:
        for y in [1,5,9,13]:
            board[x][y]='3L'
    for x in ['B','N']:
        for y in [5,9]:
            board[x][y]='3L'
    for x in ['D','L']:
        for y in [0,7,14]:
            board[x][y]='2L'
    for x in ['C','M','G','I']:
        for y in [6,8]:
            board[x][y]='2L'
    for x in ['G','I']:
        for y in [2,12]:
            board[x][y]='2L'
    for x in ['A','H','O']:
        for y in [3,11]:
            board[x][y]='2L'
    board['H'][7]='2W'
    return board

    
bravo='ABCDEFGHIJKLMNOPQRSTUVWXYZ'
global alpha
alpha=list()
for x in range(26):
    for y in range(26):
        alpha.append(bravo[x]+bravo[y])

def build_dictionary_textfiles():
    try:
        open('AA.txt')
    except:
        global alpha
        text=open('Collins Scrabble Words (2015) with definitions.txt')
        go=True
        letter=0
        current_text_file=open(alpha[0]+'.txt','w')
        while go:
            line=text.readlines(1)
            if line:
                line=line[0]
            else:
                current_text_file.close()
                print('Jobs Finished!')
                go=False
                break
            if line[:2]==alpha[letter]:
                current_text_file.write(line)
            elif letter+1<len(alpha) and line[:2]==alpha[letter+1]:
                letter+=1
                current_text_file.close()
                current_text_file=open(alpha[letter]+'.txt','a')
                current_text_file.write(line)
            elif line[:2] in alpha:
                current_text_file.close()
                letter=alpha.index(line[:2])
                current_text_file=open(alpha[letter]+'.txt','a')
                current_text_file.write(line)
            else:
                current_text_file.close()
                raise Exception("\n\nSomething happened: here are the details: \nLetter: "+alpha[letter])
                go=False
    return None


build_dictionary_textfiles()

def RUN():
    while True:
        m=Mailchecker()
        print('.',end='')
        m.CHECK_THE_MAAAIIIIIILLLLLL()
        time.sleep(60)


'''
game=Game()
game.add_player('andrew','doesnt matter')
game.begin()
print(game.hands['andrew'])
'''
    

RUN()












