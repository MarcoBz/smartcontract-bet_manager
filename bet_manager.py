"""
Bet Manager
===================================
Author: MarcoBz
Date: 2018
"""

#from neocore.Cryptography.Crypto import Crypto
from boa.interop.Neo.Storage import Get, Put
from boa.interop.Neo.Runtime import CheckWitness, Serialize, Deserialize
from boa.interop.Neo.Blockchain import GetHeight
from boa.builtins import concat

ctx = GetContext()

def Main(operation, args):
    """
    :param operation: str The name of the operation to perform (07)
    :param args: list of arguments along with the operation (10)
    :return: bool, result of the execution (01)
    """
    if operation == 'create_league':
        return create_league(args)

    elif operation == 'create_bet':
        return create_bet(args)

    # elif operation == 'partecipate_bet':
    #     return partecipate_bet(args)

    # elif operation == 'convalidate_bet':
    #     return convalidate_bet(args)

    elif operation == 'get_storage':
        return get_storage(args)
    elif operation == 'get_league':
        return get_league(args)

    # elif operation == 'get_bet_info':
    #     return get_bet_info(args)

    else:
        return False

def create_league(args):

    if not len(args) % 2 != 0:
        return "Not right number of arguments"

    # check proposal existence
    league_id = args[len(args) -1]

    if Get(ctx, league_id):
        return "Already a League with that name" 
  
    partecipants = (len(args) - 1 ) /2
    # iterate to get partecipants (address, nicknames)
    league_partecipants = []
    index = 0
    while index < (len(args) - 1)/2:

        address = args[index]
        nickname = args[index + partecipants]
        # check address format
        if len(address) != 20:
            return "Bad address format"

        league_partecipants.append([address, nickname])
        partecipant_group = address
        if Get(ctx, partecipant_group):
        	fromStorage = Get(ctx, partecipant_group)
        	partecipant_leagues = Deserialize(fromStorage)
        	partecipant_leagues.append([league_id])      #[league_id, [bet1_id, bet2_id, ..]]
        	partecipant_storage = Serialize(partecipant_leagues)
        else:
        	partecipant_leagues = []
        	partecipant_leagues.append([league_id])
        	partecipant_storage = Serialize(partecipant_leagues)
        Put(ctx, partecipant_group, partecipant_storage)
        index += 1

    # proposal arguments
    league = []
    league.append(league_partecipants)    # partecipants

    league_bet = []
    league.append(league_bet)

    league.append(0)          # num bet
    # ... other league parameter
  
    # serialize proposal and write to storage
    league_storage = Serialize(league)
    Put(ctx, league_id, league_storage)


    return "Ok"

def get_storage(args):
	name = concat(args[0], 'Group')
	print(name)
	storage = Get(ctx, args[0])
	print(storage)
	data = Deserialize(storage)
	index = 0
	while index < len(data):
		print(data[index])
		index += 1
	return True

def get_league(args):

    if len(args) != 2:
        return "Not right number of arguments"

    asker_id = args[0]
    league_id = args[1]

    if len(asker_id) != 20:
        return 'Bad address format'
    # check league existence

    league_storage =  Get(ctx, league_id)
    
    if not league_storage:
        return "League does not exist"

    # check if asker is in the league

    league = Deserialize(league_storage)
    index = 0
    while index < len(league[0]):
        if asker_id == league[0][index][0]:
            in_league = True
            break
        index += 1

    if not in_league:
        return 'Who wants the information is not in the league'

    index = 0
    while index < len(league[0]):
        print(league[0][index][0])
        print(league[0][index][1])
        index += 1

    index = 0
    while index < len(league[1]):
        print(league[1][index])
        index += 1

    return "Ok"

def create_bet(args):
    """
    Register a New prosal
    :param args: list of arguments [ ]
    :return: bool, result of the execution
    """
    
    if len(args) < 11:
        return "Not right number of arguments"

    creator_id = args[0]
    league_id = args[1]
    bet_text = args[2]
    blocks_accept = args[3]
    blocks_partecipate = args[4]
    blocks_convalidate = args[5]
    amount_to_bet = args[6]
    token_used = args[7]
    add_results = args[8]
    results = []

    authorized = CheckWitness(creator_id)
    if not authorized:
    	return 'Not authorized'

    for i in range(9, len(args)):
        print(i)
        results.append(args[i])

    if len(creator_id) != 20:
        return 'Bad address format'

    # check if int
    if blocks_accept < 0 :
        return "Error in one argument"

    if blocks_convalidate < 0 :
        return "Error in one argument"

    if blocks_partecipate < 0 :
        return "Error in one argument"

    if amount_to_bet < 0 :
        return "Error in one argument"
    
    if add_results != "y" and add_results != "n":
        return "Error in one argument"
    
    """
    # sistemare il check del token

    usable_token = ["602c79718b16e442de58778e148d0b1084e3b2dffd5de6b7b16cee7969282de7"] #capire se serve 0x
    
    for i in range(len(usable_token)):
        if usable_token[i] == token_used:
            right_token = True
            break

    if not right_token:
        return False
    """
    
    # check league existence
    
    league_storage =  Get(ctx, league_id)

    if not league_storage:
        return "League does not exist"
    
    # check if creatore is in the league
    
    league = Deserialize(league_storage)
    index = 0
   
    while index < len(league[0]):
        if creator_id == league[0][index][0]:
            in_league = True
        index += 1

    if not in_league:
        return 'Creator is not in the league'
    # check if bet already exists

    bet_id = concat(league_id, bet_text)
    bet_storage = Get(ctx, bet_id)

    if bet_storage:
        return "Bet already exists"

    bet = []
    bet.append(league_id)
    bet.append(bet_text)
    bet.append(creator_id)

    bet_data = [blocks_accept,blocks_partecipate,blocks_convalidate,amount_to_bet,token_used,add_results]
    bet_results = [] #[result, betters, convalidators]

    for i in results:
        bet_results.append([i,[],[]])

    bet.append(bet_data)
    bet.append(bet_results)

    current_block = GetHeight()#ADD BLOCK WHEN BET IS CREATED

    bet.append(current_block)

    bet_payed = True
    bet.append(bet_payed)

    bet_storage = Serialize(bet)
    Put(ctx, bet_id, bet_storage)

    league[1].append(bet_text)
    league_storage = Serialize(league)
    Put(ctx, league_id, league_storage)

    string = "Ok Bet created at : " + current_block
    
    return string