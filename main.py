import hashlib
import json
from functools import reduce
from collections import OrderedDict


# The reward we give to miners (for creating a new block)
MINING_REWARD = 10

# list of all blocks in the blockchain
blockchain = []

# list of all properties (both sold and unsold)
properties = []

# list of all participants (both buyer and seller)
participants = []

# Unhandled transactions or transactions those are yet to mine
un_mined_transactions = []

# Government Database should contain the
# list of both properties and participants
govt_database = OrderedDict(
    [
        ('name', 'Govt'),
        ('id', 0000),
        ('properties', properties),
        ('participants', participants)
    ]
)

# Owner is the one who buys and sells the property
owner_database = OrderedDict(
    [
        ('name', 'Bilal'),
        ('id', 42310236846168),
        ('properties', []),
        ('past_properties', [])
    ]
)


def init_blockchain():
    """initializes the blockchain list with the 'genesis' block."""
    global blockchain
    genesis_block = {
        'previous_hash': '',
        'index': 0,
        'transactions': [],
        'proof': 100
    }
    blockchain.append(genesis_block)


def init_participants():
    """initializes the participants lists with some default participants."""
    global participants
    participant = OrderedDict(
        [
            ('name', 'hamza'),
            ('id', 12345),
            ('properties', []),
            ('past_properties', [])
        ]
    )
    participants.append(participant)


def init_properties():
    """initializes the properties list with some default properties."""
    global properties
    property1 = OrderedDict(
        [
            ('property_address', 'Flat no : 3, Plot no : 7, Street no : 32, Tauheed commercial Area'),
            ('property_owner', 'Faran'),
            ('property_owner_id', 42310236846167)
        ]
    )
    property2 = OrderedDict(
        [
            ('property_address', 'Flat no : 6, Plot no : 3, Street no : 20, Tauheed commercial Area'),
            ('property_owner', 'Bilal'),
            ('property_owner_id', 42310236846168)
        ]
    )
    properties.append(property1)
    properties.append(property2)


def load_data():
    """Initialize blockchain + open transactions data from a file."""
    global blockchain
    global un_mined_transactions
    try:
        with open('blockchain.txt', mode='r') as f:
            # file_content = pickle.loads(f.read())
            file_content = f.readlines()
            # blockchain = file_content['chain']
            # un_handled_transactions = file_content['ot']
            ##print('file_content: \n',file_content)
            if len(file_content) > 0:
                blockchain = json.loads(file_content[0][:-1])
            # We need to convert  the loaded data because Transactions should use OrderedDict
            updated_blockchain = []
            for block in blockchain:
                updated_block = {
                    'previous_hash': block['previous_hash'],
                    'index': block['index'],
                    'proof': block['proof'],
                    'transactions': []
                }
                size = len(block['transactions'])
                i=1

                for tx in block['transactions']:
                    try:
                        senderUnordered = tx['sender'] 
                        sender = OrderedDict(
                            [('name', senderUnordered['name']), ('id', senderUnordered['id'])]
                        )
                        recipientUnordered = tx['recipient'] 
                        recipient = OrderedDict(
                            [('name', recipientUnordered['name']), ('id', recipientUnordered['id'])]
                        )
                    except:
                        sender = tx['sender']
                        recipient = tx['recipient']
                    if(i < size):
                        print("load data: i, tx ", i, tx['property_address']) 
                        """property_address = tx[property_address]"""
                        updated_block['transactions'].append(
                            OrderedDict(
                                [('sender', sender), ('recipient', recipient), ('amount', tx['amount']), ('property_address', tx['property_address'])])
                        )
                    else:
                        updated_block['transactions'].append(
                            OrderedDict(
                                [('sender', sender), ('recipient', recipient), ('amount', tx['amount'])])
                        )
                       
                    i = i + 1


                updated_blockchain.append(updated_block)
            blockchain = updated_blockchain
            if len(file_content) > 0:
                un_mined_transactions = json.loads(file_content[1])
            # We need to convert  the loaded data because Transactions should use OrderedDict
            updated_transactions = []
            for tx in un_mined_transactions:
                updated_transaction = OrderedDict(
                    [('sender', tx['sender']), ('recipient', tx['recipient']), ('amount', tx['amount']), ('property_address', tx['property_address'])])
                updated_transactions.append(updated_transaction)
            #print("updated tx", updated_transactions)
            un_mined_transactions = updated_transactions
    except IOError:
        print("File not found")


def save_data():
    """Save blockchain + open transactions snapshot to a file."""
    with open('blockchain.txt', mode='w') as f:
        f.write(json.dumps(blockchain))
        f.write('\n')
        f.write(json.dumps(un_mined_transactions))
        # save_data = {
        #     'chain': blockchain,
        #     'ot': un_mined_transactions
        # }
        # f.write(pickle.dumps(save_data))
        #print('file saved')
    print('file saved')
    #print('Saving failed!')


def valid_proof(transactions, last_hash, proof):
    """Validate a proof of work number and see if it solves the puzzle algorithm (two leading 0s)

    Arguments:
        :transactions: The transactions of the block for which the proof is created.
        :last_hash: The previous block's hash which will be stored in the current block.
        :proof: The proof number we're testing.
    """
    # Create a string with all the hash inputs
    guess = (str(transactions) + str(last_hash) + str(proof)).encode()
    # Hash the string
    # IMPORTANT: This is NOT the same hash as will be stored in the previous_hash. It's a not a block's hash. It's only used for the proof-of-work algorithm.
    guess_hash = hashlib.sha256(guess).hexdigest()
    print("hash of proof: ", guess_hash)
    # Only a hash (which is based on the above inputs) which starts with two 0s is treated as valid
    # This condition is of course defined by you. You could also require 10 leading 0s - this would take significantly longer (and this allows you to control the speed at which new blocks can be added)
    return guess_hash[0:2] == '00'


def proof_of_work():
    """
    Generate a proof of work for the open transactions,
    the hash of the previous block and a random number
    (which is guessed until it fits).
    """
    last_block = blockchain[-1]
    encoded_block = json.dumps(last_block, sort_keys=True).encode()
    last_hash = hashlib.sha256(encoded_block).hexdigest()
    proof = 0
    # Try different PoW numbers and return the first valid one
    while not valid_proof(un_mined_transactions, last_hash, proof):
        proof += 1
    # print(un_mined_transactions)
    print("Proof of Work: ", proof)
    return proof


def get_balance(participant):
    """Calculate and return the balance for a participant.

    Arguments:
        :participant: The person for whom to calculate the balance.
    """
    # Fetch a list of all sent coin amounts for the given person (empty lists are returned if the person was NOT the sender)
    # This fetches sent amounts of transactions that were already included in blocks of the blockchain
    tx_sender = [[tx['amount'] for tx in block['transactions']
                  if tx['sender'] == participant] for block in blockchain]
    # Fetch a list of all sent coin amounts for the given person (empty lists are returned if the person was NOT the sender)
    # This fetches sent amounts of open transactions (to avoid double spending)
    open_tx_sender = [tx['amount']
                      for tx in un_mined_transactions if tx['sender'] == participant]
    tx_sender.append(open_tx_sender)
    ##print("tx_sender", tx_sender)
    amount_sent = reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt)
                         if len(tx_amt) > 0 else tx_sum + 0, tx_sender, 0)
    # This fetches received coin amounts of transactions that were already included in blocks of the blockchain
    # We ignore open transactions here because you shouldn't be able to spend coins before the transaction was confirmed + included in a block
    tx_recipient = [[tx['amount'] for tx in block['transactions']
                     if tx['recipient'] == participant] for block in blockchain]
    amount_received = reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt)
                             if len(tx_amt) > 0 else tx_sum + 0, tx_recipient, 0)
    # Return the total balance
    return amount_received - amount_sent


def get_last_blockchain_value():
    """ Returns the last value of the current blockchain. """
    if len(blockchain) < 1:
        return None
    return blockchain[-1]

"""
def verify_transaction(transaction):
   # Verify a transaction by checking whether the sender has sufficient coins.

    #Arguments:
    #    :transaction: The transaction that should be verified.
    
    sender_balance = get_balance(transaction['sender'])
    return sender_balance >= transaction['amount']
"""
# This function accepts two arguments.
# One required one (transaction_amount) and one optional one (last_transaction)
# The optional one is optional because it has a default value => [1]

#----------------------
def add_participant(sender): #sender = new_user_signed_in #This function must be called at the time of sign up. Here sender is a dictionary
    participant = OrderedDict(
            [ ('name', sender['name']), ('id', sender['id']), ('properties', []), ('past_properties', []) ])
    participants.append(participant)

  
#-------------------------------------------------------------------------

#These all func are and should be written before add_transaction
def get_user_choice_int():
    user_input = int(input('input your choice: '))
    return user_input


def get_recipient_details_from_govt_database(index, govt_database):
    return govt_database['participants'][index]


def verify_recipent(user_input_name, user_input_id):   #change it user_verification(name, id)
    for i in range(len(participants)): #use inline func
        if participants[i]['name'] == user_input_name:
            if participants[i]['id'] == user_input_id:
                return i
    return -1


def get_recipient_details_from_user():
    user_input_name = str(input('input the name of recipient to whom you want to sell your property: '))
    user_input_id = int(input('input the recipient id: '))
    x = verify_recipent(user_input_name, user_input_id)
    return x


def get_property_price():
    user_input = int(input('input the price of property: '))
    return user_input
    

def verify_property_owner(user_details, property_details):
    if property_details['property_owner'] == user_details['name'] and property_details['property_owner_id'] == user_details['id']:
        ##print('property verified verify_propert_owner func called')
        return True
    else:
        print('property owner invalid')
        return False


def verify_transaction(transaction):
    # should add verification code here...
    return True


def update(index, owner_database):
    #performing a deep copy manually
    #watch video of deep copy and then correct it
    
    past_properties = OrderedDict(
        [('property_address', owner_database['properties'][index]['property_address']),
        ('property_next_owner_name', owner_database['properties'][index]['property_owner']),
        ('property_next_owner_id', owner_database['properties'][index]['property_owner_id'])
        ]
    )
    
    owner_database['past_properties'].append(past_properties)

    owner_database['properties'][index] = 0
    #owner_database['properties'][index].delete()
    owner_database['properties'].pop(index)
    print('\n sender updated successfully\n')
    print('sender_details: ',owner_database)

#-------------------------
# def register_user():
#     name =  input('Enter name of user\n')
#     id =    input('Enter ID of user\n')
#     properties = []
#
#     past_properties =


# New function of add_tx
def add_transaction(recipient, sender, property_details, amount=1.0, user_choice= -1): #For register property
    """ Append a new value as well as the last blockchain value to the blockchain.

    Arguments:
        :sender: The sender of the Property.
        :recipient: The recipient of the Property.
        :amount: The amount of coins sent with the transaction (default = 1.0)
    """
    #user_choice= -1
    # transaction = {
    #     'sender': sender,
    #     'recipient': recipient,
    #     'amount': amount
    # }
    ##print('user_choice in add_tx ',user_choice)
    recipient_name_and_id = OrderedDict(
        [('name', recipient['name']),
        ('id', recipient['id'])
        ]
    )
    sender_name_and_id =  OrderedDict(
        [('name', sender['name']),
         ('id', sender['id'])
         ]
    )


    transaction = OrderedDict(
        [('sender', sender_name_and_id), ('recipient', recipient_name_and_id), ('amount', amount), ('property_address', property_details['property_address'])])     #this should be handled see prob1   #property_updated_details = property_details

    if verify_transaction(transaction):
        un_mined_transactions.append(transaction)
        #participants.append(sender['name'])
        #participants.append(recipient['name'])
        
        property_details['property_owner'] = recipient['name']
        property_details['property_owner_id'] = recipient['id']
        recipient['properties'].append(property_details)    #property_details['property_address'] later on change it and append only property_address if all property details are not needed
        
        if user_choice != -1:
            print('\n\n transfer_property user_choice', user_choice)
            #use any one method
            #sender['properties']['user_choice'].delete()
            update(user_choice, sender) #index of the property inside owner_database
            """sender['properties']['user_choice'].update(new_owner=recipient_name_and_id)
            """
        #else:
        ##print('\n\nrecipient details : \n', recipient)
        
        ##print('\n\nrecipient properties : \n', recipient['properties'])
        #for i in range(len(properties)):
        #    print(i, '=', properties[i]['property_address'])

        
        ##print('\n\n un_mined_transactions = ', un_mined_transactions)
        save_data()
        return True
        
    return False


# register property on your name and save it into blockchain (this is a transaction)
def registering_property():

    for i in range(len(govt_database['properties'])):
        print('Land # ',i, '=', govt_database['properties'][i]['property_address'])
    
    print('enter the number of property you want to choose')
    user_choice = get_user_choice_int()
    ##print('len of list govt_database[properties] = ', len(govt_database['properties']))
    #Add a while loop which will prompt values again and again if user inputs wrong value, press -1 to exit
    if user_choice >= 0 and user_choice < len(govt_database['properties']):
        print('address selected is:\n', govt_database['properties'][user_choice]['property_address'])    #This is not needed
            
        #Verifying the registered property
        
        property_details = govt_database['properties'][user_choice]
        
        ##print(property_details.keys())
        
        recipient_details = owner_database
        sender_details = OrderedDict(
            [('name', govt_database['name']),
            ('id', govt_database['id'])
            ]
        )
        if verify_property_owner(owner_database, property_details):
            print('property verified successfully ')
            if add_transaction(recipient_details, sender_details, property_details, amount=0):
                ##print('property registered successfully: inside func')
                return True
        else:
            print('property not verified successfully ')
            return False
    else:
        print('user choice is invalid')


def transfer_property():

    ##print('\nowner_database ', owner_database.keys())
    print('\n')
    i = -1
    if len(owner_database['properties']) > 0:
        print('The properties you own are:\n')
        for i in range(len(owner_database['properties'])):
            print('property number:',i, '=', owner_database['properties'][i]['property_address'], '\n')
            #print(i, '=', owner_database['properties'][i]['property_address'])  # this code runs fine
    if i==-1:
        print('You dont have any property so you cannot transfer, have a nice day sir ')
    else:
        print('enter the number of property you want to choose')
        user_choice = get_user_choice_int()
        print('len of list owner_database[properties] = ', len(owner_database['properties']))
        #Add a while loop which will prompt values again and again if user inputs wrong value, press -1 to exit
        if user_choice >= 0 and user_choice < len(owner_database['properties']):
            print('address selected is: ', owner_database['properties'][user_choice])    #This is not needed
                
            #Verifying the registered property
            
            property_details = owner_database['properties'][user_choice]  # ['property_address'] 
            
            ##print('\nproperty_details inside transfer_property func ',property_details) #.keys()
            
            """recipient_details_tuple = get_recipient_details_from_user()    #verify from database(blockchain_participants or govt_database['participants'])
            (recipient_name, recipient_id) = recipient_details_tuple   #tuple unpacking
            """
            x = get_recipient_details_from_user()
            if x != -1:
                recipient_details = get_recipient_details_from_govt_database(x, govt_database)
        
                """this recipient, we are making on runtime, but later on we will search the system for recipient details 
                so that we can get his property details as well after his verification (we will do this part 
                inside recipient_verification() ) """
                """
                recipient_details = {    
                        'name' : recipient_name,
                        'id' : recipient_id,
                        'properties' : []
                }
                """
                """
                The recipient should already have signed up into the so that we could verify his details or credentials
                """
                
                amount=100 #amount of property sold at
                amount = get_property_price()
                #if verify_property_owner_2(property_details, govt_database):  (owner_database, property_details)
                #in this new function we gotta search that property in govt_database and then pass property_details = govt_database['properties'][searched] in verify_property_owner() function
                if add_transaction(recipient_details, owner_database, property_details, amount, user_choice):
                    print('property transfered successfully ')
                    return True
                else:
                    print('property not transfered successfully ')
                    return False
            elif x == -1:
                print('recipient not registered, ask him to sign up first')
                return False
        else:
            print('user choice is invalid')
            return False
        #add_transaction(recipient_details, sender_details, amount=0, property_details, user_choice)


def print_user_details():
    print('user name: ', owner_database['name'])
    print('user id: ', owner_database['id'])
    print('user properties: ', owner_database['properties'])
    print('user past properties: ', owner_database['past_properties'])


def mine_block():
    """Create a new block and add open transactions to it."""
    # Fetch the currently last block of the blockchain
    last_block = blockchain[-1]
    #print(last_block)
    # Hash the last block (=> to be able to compare it to the stored hash value)

    #hashed_block = hashlib.sha256(last_block).hexdigest()
    encoded_block = json.dumps(last_block, sort_keys=True).encode()
    hashed_block = hashlib.sha256(encoded_block).hexdigest()
    proof = proof_of_work()
    owner = 'Max'
    # Miners should be rewarded, so let's create a reward transaction
    # reward_transaction = {
    #     'sender': 'MINING',
    #     'recipient': owner,
    #     'amount': MINING_REWARD
    # }
    reward_transaction = OrderedDict(
        [('sender', 'MINING'), ('recipient', owner), ('amount', MINING_REWARD)])
    # Copy transaction instead of manipulating the original un_mined_transactions list
    # This ensures that if for some reason the mining should fail, we don't have the reward transaction stored in the open transactions
    copied_transactions = un_mined_transactions[:]
    copied_transactions.append(reward_transaction)
    block = {
        'previous_hash': hashed_block,
        'index': len(blockchain),
        'transactions': copied_transactions,
        'proof': proof
    }
    blockchain.append(block)
    return True


def get_transaction_value():
    """ Returns the input of the user (a new transaction amount) as a float. """
    # Get the user input, transform it from a string to a float and store it in user_input
    tx_recipient = input('Enter the recipient of the transaction: ')
    tx_amount = float(input('Your transaction amount please: '))
    return tx_recipient, tx_amount


def print_blockchain_elements():
    """ Output all blocks of the blockchain. """
    # Output the blockchain list to the console
    i = 0
    for block in blockchain:
        print('Outputting Block ', i)
        print(block)
        i += 1
    else:
        print('-' * 20)


def verify_chain():
    """ Verify the current blockchain and return True if it's valid, False otherwise."""
    for (index, block) in enumerate(blockchain):
        if index == 0:
            continue
        # ORIGINAL
        if block['previous_hash'] != hashlib.sha256(json.dumps(blockchain[index-1], sort_keys=True).encode()).hexdigest():
        # ##
        # # AVI
        # last_block = blockchain[-1]
        # # hashed_block = hashlib.sha256(last_block).hexdigest()
        # encoded_block = json.dumps(last_block, sort_keys=True).encode()
        # last_hash = hashlib.sha256(encoded_block).hexdigest()
        # ##
            print('invalid previous hash at index: ', index)
            return False
        if not valid_proof(block['transactions'][:-1], block['previous_hash'], block['proof']):
            print('\ninvalid reason block transaction, prev hash, proof\n', block['transactions'][:-1], block['previous_hash'], block['proof'])
            print('Proof of work is invalid')
            return False
    return True


# print(blockchain[1]['transactions'][-2])   #we can use tansactions[:-2] if we don't wanna include the mining reward transaction

def verify_transactions():
    """Verifies all open transactions."""
    return all([verify_transaction(tx) for tx in un_mined_transactions])


def console():
    print('\n+-----------------------------+')
    print('1: Register your property')
    print('2: Sell your property')  # transfers property to government
    print('3: Mine a new block')
    print('4: Check Transaction Validity')
    print('5: Check Blockchain Validity')
    print('6: Manipulate the chain')
    print('7: Display Un-mined Transactions')  # transactions those are open (yet to mine)
    print('8: Display Blockchain Blocks')
    print('9: Display Participants')
    print('10: Display User Details')  # displays user and his/her properties' data.
    print('11: Quit')


def init():
    init_blockchain()
    init_participants()
    init_properties()


if __name__ == '__main__':
    init()
    while True:
        console()
        user_choice = input('Enter your choice: ')
        if user_choice == '1':
            if registering_property():
                print('Property registered successfully')
            else:
                print('Registering failed')
        elif user_choice == '2':
            if transfer_property():
                print('Property transferred successfully')
            else:
                print('Property transfer failure')
        elif user_choice == '3':
            if mine_block():
                un_mined_transactions = []
                save_data()
        elif user_choice == '4':
            if verify_transactions():
                print('All transactions are valid')
            else:
                print('There are invalid transactions')
        elif user_choice == '5':
            if verify_chain():
                print('Blockchain is VALID!')
            else:
                print('Invalid Blockchain')
        elif user_choice == '6':
            # Make sure that you don't try to "hack" the blockchain if it's empty
            if len(blockchain) >= 1:
                # simply change the block at index '0'
                blockchain[0] = {
                    'previous_hash': '',
                    'index': 0,
                    'transactions': [{'sender': 'Chris', 'recipient': 'Max', 'amount': 100.0}]
                }
        elif user_choice == '7':
            print("Un-mined Transactions: ", un_mined_transactions)
        elif user_choice == '8':
            print_blockchain_elements()
        elif user_choice == '9':
            print(participants)
        elif user_choice == '10':
            print('\nProperty records of user: ', owner_database['name'])
            print_user_details()
        elif user_choice == '11':
            print('Exiting...')
            break
        else:
            print('Invalid input... Try again!')

        # print('Balance of {}: {:6.2f}'.format('Max', get_balance('Max')))
