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
    if operation == 'create_group':
        return create_group(args)

    elif operation == 'create_bet':
        return create_bet(args)

    elif operation == 'participate_bet':
         return participate_bet(args)

    elif operation == 'validate_bet':
         return validate_bet(args)

    elif operation == 'get_storage':
        return get_storage(args)

    elif operation == 'get_height':
        return get_height(args)

    elif operation == 'withdraw_win':
        return withdraw_win(args)

    elif operation == 'withdraw_refund':
        return withdraw_refund(args)

    else:
        returnStr = "Error" 
        returnArray = []
        returnArray.append(returnStr)
        return returnArray

def get_height(args):

    current_block = GetHeight()
    returnArray = []
    returnArray.append(current_block)

    return returnArray

# function to create a new group
def create_group(args):

    #check number of arguments
    if not len(args) % 2 != 0:
        returnStr = "Not right number of arguments" 
        returnArray = []
        returnArray.append(returnStr)
        return returnArray

    # check proposal existence
    group_id = args[len(args) -1]

    if Get(ctx, group_id):
        returnStr = "Already a group with that name" 
        returnArray = []
        returnArray.append(returnStr)
        return returnArray
  
    participants = (len(args) - 1 ) / 2

    # iterate to get participants (address, nicknames)
    group_participants = []
    index = 0

    while index < (len(args) - 1)/2:
        address = args[index]
        if len(address) != 20:
            returnStr = "Bad address format"
            returnArray = []
            returnArray.append(returnStr)
            return returnArray  
        index += 1 

    index = 0
    while index < (len(args) - 1)/2:
        address = args[index]
        nickname = args[index + participants]
        group_participants.append([address, nickname])
        if Get(ctx, address):
            fromStorage = Get(ctx, address)
            participant_groups = Deserialize(fromStorage)
            participant_groups[0].append(group_id)      #[[group_id1, group_id2], [ [bet1], [bet2]], [transactions], total_balance, total_balance sign ( 0 positiv, 1 negative) ]
            participant_storage = Serialize(participant_groups)
        else:
            #create storage for the current address
            participant_groups = []
            participant_groups.append([])
            participant_groups.append([]) 
            participant_groups.append([]) 
            participant_groups.append(0) 
            participant_groups.append(0)
            participant_groups[0].append(group_id) 
            participant_storage = Serialize(participant_groups)
        Put(ctx, address, participant_storage)
        index += 1

    # proposal arguments
    group = []
    group.append(group_participants)    # participants

    group_bet = []
    group.append(group_bet)
  
    # serialize proposal and write to storage
    group_storage = Serialize(group)
    Put(ctx, group_id, group_storage)

    current_block = GetHeight()
    returnStr = "Ok"
    returnArray = []
    returnArray.append(returnStr)
    returnArray.append(current_block)
    return returnArray

def get_storage(args):

    storage = Get(ctx, args[0])
    data = Deserialize(storage)
    returnStr = "Ok"
    current_block = GetHeight()
    returnArray = []
    returnArray.append(returnStr)
    returnArray.append(data)
    returnArray.append(current_block)
    return returnArray

#function to create a new bet
def create_bet(args):
    
    #check arguments 
    if len(args) < 11:
        returnStr = "Not right number of arguments" 
        returnArray = []
        returnArray.append(returnStr)
        return returnArray

    creator_id = args[0]
    group_id = args[1]
    bet_text = args[2]
    blocks_accept = args[3]
    blocks_participate = args[4]
    blocks_validate = args[5]
    amount_to_bet = args[6]
    token_used = args[7]
    add_results = args[8]
    results = []

    authorized = CheckWitness(creator_id)
    if not authorized:
        returnStr = 'Not authorized' 
        returnArray = []
        returnArray.append(returnStr)
        return returnArray

    for i in range(9, len(args)):
        results.append(args[i])

    #check address format of sender
    if len(creator_id) != 20:
        returnStr = "Bad address format"
        returnArray = []
        returnArray.append(returnStr)
        return returnArray

    # check arguments format
    if blocks_accept < 0 :
        returnStr = "Error in one argument"
        returnArray = []
        returnArray.append(returnStr)
        return returnArray

    if blocks_validate < 0 :
        returnStr = "Error in one argument"
        returnArray = []
        returnArray.append(returnStr)
        return returnArray

    if blocks_participate < 0 :
        returnStr = "Error in one argument"
        returnArray = []
        returnArray.append(returnStr)
        return returnArray

    if amount_to_bet < 0 :
        returnStr = "Error in one argument"
        returnArray = []
        returnArray.append(returnStr)
        return returnArray
    
    if add_results != 0 and add_results != 1: # '0' : can add proposal, '1' cannot add proposal
        returnStr = "Error in one argument"
        returnArray = []
        returnArray.append(returnStr)
        return returnArray
    
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
    
    # check group existence
    
    group_storage =  Get(ctx, group_id)

    if not group_storage:
        returnStr = "group does not exist"
        returnArray = []
        returnArray.append(returnStr)
        return returnArray
    
    # check if creator is in the group
    
    group = Deserialize(group_storage)
    index = 0
   
    while index < len(group[0]):
        if creator_id == group[0][index][0]:
            in_group = True
        index += 1

    if not in_group:
        returnStr = 'Creator is not in the group'
        returnArray = []
        returnArray.append(returnStr)
        return returnArray

    # check if bet already exists

    bet_id = concat(group_id, bet_text)
    bet_storage = Get(ctx, bet_id)

    if bet_storage:
        returnStr = "Bet already exists"
        returnArray = []
        returnArray.append(returnStr)
        return returnArray

    bet = []
    bet.append(group_id)
    bet.append(bet_text)
    bet.append(creator_id)

    num_participants = len(group[0])

    bet_data = [blocks_accept,blocks_participate,blocks_validate,amount_to_bet,token_used,add_results,num_participants]
    bet_results = [] 

    for i in results:
        bet_results.append([i,[],[],[]]) #(bet_text, [participants], [convalidators], [already payed])

    bet.append(bet_data)
    bet.append(bet_results)

    current_block = GetHeight() #ADD BLOCK WHEN BET IS CREATED

    bet.append(current_block)

    bet_storage = Serialize(bet)
    Put(ctx, bet_id, bet_storage)

    group[1].append(bet_text)
    group_storage = Serialize(group)
    Put(ctx, group_id, group_storage)

    returnStr = "Ok"
    current_block = GetHeight()
    returnArray = []
    returnArray.append(returnStr)
    returnArray.append(current_block)
    return returnArray

#function to participate at the bet
def participate_bet(args):

    #check arguments 
    if len(args) != 4:
        returnStr = "Not right number of arguments" 
        returnArray = []
        returnArray.append(returnStr)
        return returnArray

    better_id = args[0]
    group_id = args[1]
    bet_text = args[2]
    result = args[3]
    
    
    if len(better_id) != 20:
        returnStr = "Bad address format"
        returnArray = []
        returnArray.append(returnStr)
        return returnArray

    # check group existence

    group_storage =  Get(ctx, group_id)

    if not group_storage:
        returnStr = "group does not exist"
        returnArray = []
        returnArray.append(returnStr)
        return returnArray
    
    # check if bet exists
    
    bet_id = concat(group_id, bet_text)
    bet_storage = Get(ctx, bet_id)
    
    if not bet_storage:
        returnStr = "Bet does not exist"
        returnArray = []
        returnArray.append(returnStr)
        return returnArray

    # check if better is in the group
    group = Deserialize(group_storage)
    index = 0
    
    while index < len(group[0]):
        if better_id == group[0][index][0]:
            in_group = True
        index += 1
    
    if not in_group:
        returnStr = 'Better is not in the group'
        returnArray = []
        returnArray.append(returnStr)
        return returnArray
    
    # check if better has already participate

    address_storage = Deserialize(Get(ctx, better_id))

    index = 0
    while index < len(address_storage[1]):
        if address_storage[1][index][0] == bet_text:
            if address_storage[1][index][1] == group_id:
                returnStr = 'Already participated'
                returnArray = []
                returnArray.append(returnStr)
                return returnArray            
        index += 1

    # check if result exists
   
    bet = Deserialize(bet_storage)
    index = 0
    while index < len(bet[4]):
        if bet[4][index][0] == result:
            result_exists = True
            break
        index += 1

    #if player can add a result
    if not result_exists:
        if bet[3][5] == 1:
            bet[4].append([result,[],[],[]])
        else:
            returnStr = 'Cannot bet on that result'
            returnArray = []
            returnArray.append(returnStr)
            return returnArray
    
    # check if bet is still open
    
    current_block = GetHeight()
    block_at_creation = bet[5]

    if current_block > block_at_creation + bet[3][0]:
        returnStr = 'Cannot participate at the bet'
        returnArray = []
        returnArray.append(returnStr)
        return returnArray

    # check if tx is right signed
    if not CheckWitness(better_id):
        returnStr = "You are not who you say"
        returnArray = []
        returnArray.append(returnStr)
        return returnArray

    # check if voter has enough token in its address

    # participate bet
    index = 0
    while index < len(bet[4]):
        if bet[4][index][0] == result:          
            bet[4][index][1].append(better_id)
            break
        index += 1

    bet_storage = Serialize(bet)
    Put(ctx, bet_id, bet_storage)

    #register the flow of token

    address_storage = Deserialize(Get(ctx, better_id))

    if address_storage[4] == 0:
        sign = 1
    else:
        sign = -1
    

    total_balance = address_storage[3] * sign
    new_total_balance = total_balance - bet[3][3]

    if new_total_balance >= 0 :
        address_storage[3] = new_total_balance
        address_storage[4] = 0
    else :
        address_storage[3] = new_total_balance * -1
        address_storage[4] = 1

    current_transaction = []
    current_transaction.append(bet_text)
    current_transaction.append(group_id)
    current_block = GetHeight()
    current_transaction.append(0) # "0" : payment, "1" : winning, "2" : refund
    current_transaction.append(0)
    current_transaction[3] = current_transaction[3] + bet[3][3] 
    address_storage[2].append(current_transaction)

    #save the bet in the personal storage of the better
    current_bet = []
    current_bet.append(bet_text)
    current_bet.append(group_id)
    blocks = []
    blocks.append(0)
    blocks.append(0)
    blocks.append(0)
    blocks[0] = blocks[0] + bet[3][0]
    blocks[1] = blocks[1] + bet[3][1]
    blocks[2] = blocks[2] + bet[3][2]
    current_bet.append(blocks)
    current_bet.append(0)
    current_bet[3] = current_bet[3] + bet[5]
    current_bet.append(0) #"0" : payment, "1" : winning, "2" : refund
    current_bet.append(0)
    current_bet[5] = current_bet[5] + bet[3][3] 
    address_storage[1].append(current_bet)
    Put(ctx, better_id, Serialize(address_storage))

    returnStr = "Ok"
    returnArray = []
    returnArray.append(returnStr)
    returnArray.append(current_block)
    return returnArray

#function to validate a result of the bet
def validate_bet(args):

    if len(args) != 4:
        returnStr = "Not right number of arguments" 
        returnArray = []
        returnArray.append(returnStr)
        return returnArray

    validator_id = args[0]
    group_id = args[1]
    bet_text = args[2]
    result = args[3]

    if len(validator_id) != 20:
        returnStr = "Bad address format" 
        returnArray = []
        returnArray.append(returnStr)
        return returnArray

    # check group existence

    group_storage =  Get(ctx, group_id)

    if not group_storage:
        returnStr = "group does not exist" 
        returnArray = []
        returnArray.append(returnStr)
        return returnArray

    # check if bet exists

    bet_id = concat(group_id, bet_text)
    bet_storage = Get(ctx, bet_id)

    if not bet_storage:
        returnStr = "Bet does not exist"
        returnArray = []
        returnArray.append(returnStr)
        return returnArray
    
    # check if validator is in the group
    group = Deserialize(group_storage)
    index = 0
    while index < len(group[0]):
        if validator_id == group[0][index][0]:
            in_group = True
        index += 1
    
    if not in_group:
        returnStr = 'validator is not in the group'
        returnArray = []
        returnArray.append(returnStr)
        return returnArray

    # check if tx is right signed
    if not CheckWitness(validator_id):
        returnStr = "You are not who you say"
        returnArray = []
        returnArray.append(returnStr)
        return returnArray

    #check if is time to validate
    bet = Deserialize(bet_storage)
    current_block = GetHeight()
    block_at_creation = bet[5]

    if current_block > block_at_creation + bet[3][0] + bet[3][1]:
        time_to_validate = True

    if current_block > block_at_creation + bet[3][0] + bet[3][1] + bet[3][2]:
        time_to_validate = False

    if not time_to_validate:
        returnStr = "Cannot validate"
        returnArray = []
        returnArray.append(returnStr)
        return returnArray  

    #check if validated result is one of the chosen
    index = 0
    while index < len(bet[4]):
        if bet[4][index][0] == result: 
            result_exists = True
        index += 1

    if not result_exists:
        returnStr = 'Result does not exists'
        returnArray = []
        returnArray.append(returnStr)
        return returnArray

    index = 0
    while index < len(bet[4]):
        jndex = 0
        while jndex < len(bet[4][index][2]):
            if validator_id == bet[4][index][2][jndex]:
                already_validated = True
                result_validated = bet[4][index][0]
                chosen_index = index  
            jndex += 1
        index += 1 

    if already_validated:
        if result_validated == result:
            returnStr = 'Already validated this result'
            returnArray = []
            returnArray.append(returnStr)
            return returnArray
        else:
            newConvArray = []
            jndex = 0
            while jndex < bet[4][chosen_index][2]:
                if bet[4][chosen_index][2][index] != validator_id:
                    newConvArray.append(bet[4][chosen_index][2][jndex])
                jndex += 1
            bet[4][chosen_index][2] = newConvArray   
            index = 0
            while index < len(bet[4]):
                if bet[4][index][0] == result:
                     bet[4][index][2].append(validator_id)
                index += 1
    
    else:
        index = 0
        while index < len(bet[4]):
            if bet[4][index][0] == result:
                bet[4][index][2].append(validator_id)
            index += 1
    bet_storage = Serialize(bet)
    Put(ctx, bet_id, bet_storage)

    returnStr = "Ok"
    returnArray = []
    returnArray.append(returnStr)
    returnArray.append(current_block)
    return returnArray

#function to withdraw winning
def withdraw_win(args):

    if len(args) != 3:
        returnStr = "Not right number of arguments" 
        returnArray = []
        returnArray.append(returnStr)
        return returnArray

    winner_id = args[0]
    group_id = args[1]
    bet_text = args[2]
    
    if len(winner_id) != 20:
        returnStr = "Bad address format" 
        returnArray = []
        returnArray.append(returnStr)
        return returnArray
    
    if not CheckWitness(winner_id):
        returnStr = "You are not who you say"
        returnArray = []
        returnArray.append(returnStr)
        return returnArray
   
    # check if you are in the group
    winner_data = Get(ctx,  winner_id)
    inGroup = False
    if winner_data:
        winner_storage = Deserialize(winner_data)

        index = 0
        while index < len(winner_storage[0]):
            if winner_storage[0][index] == group_id:
                inGroup = True
            index += 1
    
    if not inGroup:
        returnStr = "Not in the group"
        returnArray = []
        returnArray.append(returnStr)
        return returnArray

    bet_id = concat(group_id, bet_text)
    bet_storage = Get(ctx, bet_id)
   
    if not bet_storage:
        returnStr = "Bet does not exist"
        returnArray = []
        returnArray.append(returnStr)
        return returnArray
    
    bet = Deserialize(bet_storage)
    current_block = GetHeight()
    bet_status = get_bet_status(bet, current_block)

    if bet_status != "validated":
        returnStr = "validation not closed" 
        returnArray = []
        returnArray.append(returnStr)
        return returnArray    

  
    player_status = get_player_status(bet, current_block, winner_id)
    winningProposal = get_winning_proposal(bet, current_block)    
   
    if winningProposal != 0 and winningProposal != 1: 
        
        if player_status[0][0] == "n":
            returnStr = "You did not participated" 
            returnArray = []
            returnArray.append(returnStr)
            return returnArray           
        else:
            
            if player_status[0][1] != winningProposal:
                returnStr = "Sorry you lost" 
                returnArray = []
                returnArray.append(returnStr)
                return returnArray 
        
    elif winningProposal == 1:
        returnStr = "There isn't any winning proposal" 
        returnArray = []
        returnArray.append(returnStr)
        return returnArray              
    index = 0

    winning_fee = 0 

    total_betters = 0
    index = 0
    while index < len(bet[4]):
        total_betters += len(bet[4][index][1])
        if bet[4][index][0] == winningProposal: 
            number_winners = len(bet[4][index][1])
            bet[4][index][3].append(winner_id)
        index += 1

    total_bet_amount = total_betters * bet[3][3] 
    amount_to_winner = total_bet_amount / number_winners
    withdrawal_amount = (amount_to_winner * (100  - winning_fee)) / 100
    dapp_amount = amount_to_winner - withdrawal_amount
    if winner_storage[4] == 0:
        sign = 1
    else:
        sign = -1
    

    total_balance = winner_storage[3] * sign
    new_total_balance = total_balance + withdrawal_amount

    if new_total_balance >= 0 :
        winner_storage[3] = new_total_balance
        winner_storage[4] = 0
    else :
        winner_storage[3] = new_total_balance * -1
        winner_storage[4] = 1

    current_transaction = []
    current_transaction.append(bet_text)
    current_transaction.append(group_id)
    current_transaction.append(1) # "0" : payment, "1" : winning, "2" : refund
    current_transaction.append(0)
    current_transaction[3] = current_transaction[3] + withdrawal_amount
    winner_storage[2].append(current_transaction)
    index = 0
    while index < len(winner_storage[1]): 
        if winner_storage[1][index][0] == bet_text:
            if winner_storage[1][index][1] == group_id:
                if  winner_storage[1][index][4] == 1:
                    returnStr = "Already Payed" 
                    returnArray = []
                    returnArray.append(returnStr)
                    return returnArray
                else:
                    winner_storage[1][index][4] = 1
        index += 1
    Put(ctx, winner_id, Serialize(winner_storage))
    bet_storage = Serialize(bet)
    Put(ctx, bet_id, bet_storage)
    returnArray = []

    returnStr = "OK"
    returnArray.append(returnStr)
    returnArray.append(current_block)

    return returnArray

#function to withdraw refund
def withdraw_refund(args):

    if len(args) != 3:
        returnStr = "Not right number of arguments" 
        returnArray = []
        returnArray.append(returnStr)
        return returnArray

    player_id = args[0]
    group_id = args[1]
    bet_text = args[2]

    if len(player_id) != 20:
        returnStr = "Bad address format" 
        returnArray = []
        returnArray.append(returnStr)
        return returnArray

    if not CheckWitness(player_id):
        returnStr = "You are not who you say"
        returnArray = []
        returnArray.append(returnStr)
        return returnArray

    # check if you are in the group
    player_data = Get(ctx,  player_id)
    inGroup = False
    if player_data:
        player_storage = Deserialize(player_data)

        index = 0
        while index < len(player_storage[0]):
            if player_storage[0][index] == group_id:
                inGroup = True
            index += 1

    if not inGroup:
        returnStr = "Not in the group"
        returnArray = []
        returnArray.append(returnStr)
        return returnArray

    bet_id = concat(group_id, bet_text)
    bet_storage = Get(ctx, bet_id)

    if not bet_storage:
        returnStr = "Bet does not exist"
        returnArray = []
        returnArray.append(returnStr)
        return returnArray

    bet = Deserialize(bet_storage)
    current_block = GetHeight()

    bet_status = get_bet_status(bet, current_block)

    if bet_status != "validated":
        returnStr = "validation not closed" 
        returnArray = []
        returnArray.append(returnStr)
        return returnArray      

   
    player_status = get_player_status(bet, current_block, player_id)
    winningProposal = get_winning_proposal(bet, current_block)
    if winningProposal == 1: 
        if player_status[0][0] == "n":
            returnStr = "You did not participated" 
            returnArray = []
            returnArray.append(returnStr)
            return returnArray                   

    else:
        returnStr = "There isn't any refund" 
        returnArray = []
        returnArray.append(returnStr)
        return returnArray              

    refund_fee = 0 # 1%
    withdrawal_amount = (bet[3][3] * (100  - refund_fee)) / 100
    dapp_amount = bet[3][3]  - withdrawal_amount

    print(withdrawal_amount)

    if player_storage[4] == 0:
        sign = 1
    else:
        sign = -1
    

    total_balance = player_storage[3] * sign
    new_total_balance = total_balance + withdrawal_amount

    if new_total_balance >= 0 :
        player_storage[3] = new_total_balance
        player_storage[4] = 0
    else :
        player_storage[3] = new_total_balance * -1
        player_storage[4] = 1

    current_transaction = []
    current_transaction.append(bet_text)
    current_transaction.append(group_id)
    current_transaction.append(2) # "0" : payment, "1" : winning, "2" : refund
    current_transaction.append(0)
    current_transaction[3] = current_transaction[3] + withdrawal_amount
    player_storage[2].append(current_transaction)

    index = 0
    if len(player_storage[1]) > 0:
        while index < len(player_storage[1]): 
            if player_storage[1][index][0] == bet_text:
                if player_storage[1][index][1] == group_id:
                    if  player_storage[1][index][4] == 2:
                        returnStr = "Already Payed" 
                        returnArray = []
                        returnArray.append(returnStr)
                        return returnArray
                    else:
                        player_storage[1][index][4] = 2
            index += 1
    Put(ctx, player_id, Serialize(player_storage))
    
    jndex = 0
    while jndex < len(bet[4]):
        if bet[4][jndex][0] == player_status[0][1]:
            bet[4][jndex][3].append(player_id)
            break
        jndex += 1
    bet_storage = Serialize(bet)
    Put(ctx, bet_id, bet_storage)
    returnArray = []

    returnStr = "OK"
    returnArray.append(returnStr)
    returnArray.append(current_block)

    return returnArray


def get_bet_status(bet, current_block):
    
    if current_block < bet[5] + bet[3][0]:
        returnStr = "open"

    elif current_block < bet[5] + bet[3][0] + bet[3][1]:
        returnStr = "closed"

    elif current_block < bet[5] + bet[3][0] + bet[3][1] + bet[3][2]:
        returnStr = "onvalidation"

    else:
        returnStr = "validated"
    
    return returnStr

def get_winning_proposal(bet, current_block):
    if current_block > bet[5] + bet[3][0] + bet[3][1] + bet[3][2]:
        if bet[3][6] % 2 == 0:
            magic_number = 1 + (bet[3][6]  / 2)
        else: 
            magic_number = (bet[3][6] + 1) / 2

        index = 0

        while index < len(bet[4]):
            if len(bet[4][index][2]) >= magic_number:
                returnStr = bet[4][index][0]
                return returnStr
            index += 1
        return 1

        
    else:
        return 0

def get_player_status(bet, current_block, current_address):

    player_status  = []
    index = 0
    while index < len(bet[4]):
        jndex = 0
        while jndex < len(bet[4][index][1]):
            if current_address == bet[4][index][1][jndex]:
                participated_bet = []
                participated_bet.append("y")
                participated_bet.append(bet[4][index][0])
            jndex += 1
        jndex = 0
        while jndex < len(bet[4][index][2]):
            if current_address == bet[4][index][2][jndex]:
                validated_bet = []
                validated_bet.append("y")
                validated_bet.append(bet[4][index][0])
            jndex += 1
        index += 1
    if participated_bet:
        player_status.append(participated_bet) # ["n", ] or ["y", participated proposal]
    else:
        player_status.append(["n",""])
    if validated_bet:
        player_status.append(validated_bet) # ["n", ] or ["y", validated proposal]
    else:
        player_status.append(["n",""])
    player_status.append(["nc"]) # nc not validated, w winning, l loseing, r refund

    winningProposal = get_winning_proposal(bet, current_block)
    if winningProposal == 1:
        player_status[2] = "r"

    elif winningProposal != 0 :
        if player_status[0][0] != "n":
            if player_status[0][1] == winningProposal:
                player_status[2] = "w"
            else:
                player_status[2] = "l"

    return player_status


