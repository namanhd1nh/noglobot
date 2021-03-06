#CHARTYPES to use:

from random import shuffle
from utils.vote import Vote

CHARTYPES = [
            "cupd","secg","hunt","witc","prph","vlgr","snpr","mmag","sis1",
            "sis2","ghos","nann","whba","blow","angl","dumb","kngh","dram","nihl",     
            #wolf characters start at index 19
            "wolf","bwlf","lycn","cosp","curs","half","icew","firw","whtw","dumw",
            "savg","bro1","bro2","alph","mage"
            ]
CHARDISPLAYNAMES=[
             "cupid","bảo vệ","thợ săn","phù thủy","tiên tri","dân thường",
             "xạ thủ","pháp sư câm","chị của em","em của chị","ma",
             "hầu gái","trắng dái","thổi kèn bookoo","thiên thần",
             "thằng ngu","kị sĩ","kịch sĩ","chán đời",
              
             "sói","sói con","lycan","sói cosplay","sói nguyền","bán sói",
             "sói băng","sói lửa","sói trắng","sói ngu","con hoang",
             "sói anh", "sói em", "sói đầu đàn","sói pháp sư"
               ]

#a decorator to prefix functions that can only happen during setup time
def game_settingup(func):
    def func_wrapper(*args, **kwargs):
        if args[0].game_inprogress == False and args[0].game_ended == False: 
        # when the game setup is still happening, allow setup functions to occur. 
        # Since this decorator is used with class methods, the "args[0]" represents the "self" passed to each method.
            return func(*args, **kwargs)
        else:
            return "Game đang chơi giữa chừng, không thay đổi setup được!"
    return func_wrapper
    


class Masoi:
    def __init__(self, gamemastermember):
        self.config = { 
        "assign_randomly":True,
        "entered_members":[], #list of members who entered game to play
        "allowed_chars":[], #list of allowed characters to be used when auto assigning. 
        # repeated entries allowed to show number of each character allowed.
        }
        self.gamemaster = gamemastermember #this is who the quản trò will be
        self.roster = dict()
        self.dead_players = []
        self.dead_today = []
        #the vars above which store members will hold objects of type discord.Member 
        
        self.current_day = 0
        self.is_night = False
        
        self.game_inprogress = False
        self.game_ended = False
        
        #self.night_action_queue = [] <-- this is not necessary if we're just using the bot as a helper for the gamemaster
            
    @game_settingup
    def game_addconfig(self, configname, value):
        #default expectedtype for wrong entries lol
        returnmsg = ""
        expectedtype = str
        if configname == "entered_members" or configname == "allowed_chars":
            expectedtype = list
            returnmsg = "Đã cập nhật danh sách người chơi, gồm {} người."
        elif configname == "assign_randomly":
            expectedtype = bool
            
        if isinstance(value, expectedtype):
            if configname == "allowed_chars":
                value = [char for char in value if (char in CHARTYPES)]
                returnmsg = "Đã cập nhật danh sách nhân vật, gồm {} nhân vật."
            self.config[configname] = value
            return returnmsg.format(str(len(value)))
        else:
            return "Giá trị không hợp lệ đối với mục setup "+configname+"!"
           
    @game_settingup
    def roster_add(self, member, charcode):
        self.roster[member] = charcode
        
    @game_settingup
    def roster_randomassign(self):
        returnmsg = ""
        if len(self.config["allowed_chars"]) != len(self.config["entered_members"]):
            returnmsg = "Số người chơi không khớp với số nhân vật được phân bố!" 
            returnmsg += "Sửa lại danh sách nhân vật cho game này, hoặc thêm bớt người chơi sao cho khớp."
        else:
            chars = self.config["allowed_chars"][:]
            shuffle(chars)
            for c in range(len(chars)):
                self.roster_add(self.config["entered_members"][c], chars[c])
            returnmsg = "Đã phân vai cho mỗi người chơi."
        return returnmsg
        
    def game_printdebug(self):
        print("config dict: "+ str(self.config))
        print("roster dict: "+ str(self.roster))
        print("dead players list: "+str(self.dead_players))
        print("dead today list: "+str(self.dead_today))
        print("current day: "+str(self.current_day))
        print("inprogress: "+str(self.game_inprogress))
    
    
    def roster_getsummary(self, revealroles):
        summarymsg = "" #preamble for the summary message. to be added later.
        counter = 1
        for p in self.roster:
            p_ded = (p in self.dead_players)
            displayname = CHARDISPLAYNAMES[CHARTYPES.index(self.roster[p])]
            summarymsg += p_ded*"~~" + str(counter) + ". " + str(p) + " " + min((revealroles+p_ded),1)*displayname + p_ded*"~~" + "\n" 
            #add the tildes to strikethrough the name if the player is dead. Also, the min thing is to show role if dead.
            counter += 1
        return summarymsg
    
    def listcharactercodes(self):
        return "``` \n"+"\n".join([disp+": "+char for disp, char in zip(CHARDISPLAYNAMES,CHARTYPES)])+"\n ```"
    
    def game_start(self):
        self.game_inprogress = True
        return self.game_day_new()
    
    def game_detect_end(self, manual):
        wolfchars = CHARTYPES[19:]
        alive_characters = [self.roster[p] for p in self.roster.keys() if p not in self.dead_players]
        wolfcount = 0
        humancount = 0
        for c in alive_characters:
            if c in wolfchars:
                wolfcount += 1
            else:
                humancount += 1
        if not manual:
            #if the only players alive are wolves/humans
            if humancount == 0:
                #end the game, winners are wolves
                return self.game_end(["Ma sói", "người"])
            elif wolfcount == 0:
                #end the game, winners are humans.
                return self.game_end(["Con người", "ma sói"])
            else:
                return ""
        else:
            #using cmd to end the game manually before the detection conditions are met
            if humancount > wolfcount:
                return self.game_end(["Con người", "ma sói"])
            elif wolfcount > humancount:
                return self.game_end(["Ma sói", "người"])
            elif humancount == wolfcount:
                return self.game_end(["Không phe nào", "phe nào.** Số người và ma sói bằng nhau. **It's a tie"])
    
    def game_end(self, winners):
        self.game_inprogress = False
        self.game_ended = True
        return "\n \n \n -------------------- \n Game đã xong! Sau **{}** ngày đêm, ".format(self.current_day-1) + "**{0}** đã giết hết **{1}**! GG.".format(*winners)
  
  
    def game_day_new(self):
        if (self.current_day > 0 and self.is_night == False):
            return "Vẫn đang là ban ngày của ngày thứ "+str(self.current_day)+"! Quản trò xong chuyện đêm đã rồi mới sang ngày mới được."
        else:
            returnmsg = ""
            self.is_night = False
            self.current_day += 1
            deadtodayreport = self.dead_today #TODO: fix that print on the deadtoday report. Write a func to output the proper mentions instead of just printing the list.
            self.dead_today = []
            returnmsg += "Bắt đầu ngày thứ "+str(self.current_day)
            returnmsg += "! \n \n **Các người chơi hiện tại** (gạch chéo là đã ded): \n"+self.roster_getsummary(False)
            if (self.current_day > 1):
                returnmsg += "\n Đêm qua có thêm "+str(len(deadtodayreport))+" người chơi chết, là "+str([str(p) for p in deadtodayreport])
                returnmsg += self.game_detect_end(False)
            return returnmsg
            
    def game_day_night(self):
        if (self.is_night == True):
            return "Đang là ban đêm rồi."
        self.is_night = True
        return "Màn đêm thứ "+str(self.current_day)+" đã bắt đầu!"
        
    def game_kill(self, player):
        if (player in self.roster) and (player not in self.dead_players):
            self.dead_players.append(player)
            self.dead_today.append(player)
            
    def game_rezz(self, player):
        if (player in self.dead_players):
            self.dead_players.remove(player)
            if (player in self.dead_today):
                self.dead_today.remove(player)
                
                
    # def vote_make_message(self, emojilist):
    #     msg = "React để vote kill!"
    #     #emojilist will be a list of Emoji objects from discord.py, output from list(client.get_all_emojis())
    #     emojicounter=0
    #     emoji_to_candidate_dict = dict()
    #     for p in self.roster:
    #         if p not in self.dead_players:
    #             msg += "\n"+str(emojilist[emojicounter])+": "+str(p) #replace this with a proper mention <@{}> if this is not satisfactory.
    #             emoji_to_candidate_dict[emojilist[emojicounter]] = p
    #             emojicounter+=1
        
    #     self.emoji_to_candidate_dict = emoji_to_candidate_dict
    #     return msg, emojicounter
        
    # def vote_kill_start(self, winratio):
    #     if self.voting == False:
    #         #eligibles = list(set(self.roster.keys())-set(self.dead_players)) --awful line lol, fixed to be more pythonic below
    #         eligibles = [p for p in self.roster.keys() if p not in self.dead_players]
    #         self.voting = Vote(eligibles, self.game_kill, [], winratio, len(eligibles), True)
    #     else:
    #         return "Đang có vote giữa chừng!"
        
    # def vote_kill_add(self, player):
    #     if self.voting != False: #if there is a vote in progress
    #         return self.voting.ballot_add(player)
    #     else:
    #         return "Không có vote nào đang diễn ra."
        
