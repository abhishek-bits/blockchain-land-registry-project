import hashlib
import json
from functools import reduce
from collections import OrderedDict


# The reward we give to miners (for creating a new block)
REWARD = 10

# list of all blocks in the blockchain
blockchain = []

# list of all properties (both sold and unsold)
properties = []

# list of all participants (both buyer and seller)
participants = []

# Unhandled transactions or transactions those are yet to mine
un_mined_transactions = []

# Admin Database should contain the
# list of both properties and participants
admin_database = OrderedDict(
    [
        ('name', 'Govt'),
        ('id', 0000),
        ('properties', properties),
        ('participants', participants)
    ]
)

# actor is the one who buys and sells the property
actor_database = OrderedDict(
    [
        ('name', 'Abhishek'),
        ('id', 70),
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
            ('name', 'Susheel'),
            ('id', 109),
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
            ('property_address', 'Kolkata'),
            ('property_actor', 'Avishek'),
            ('property_actor_id', 93)
        ]
    )
    property2 = OrderedDict(
        [
            ('property_address', 'Dehradun'),
            ('property_actor', 'Abhishek'),
            ('property_actor_id', 70)
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
            file_content = f.readlines()
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
            un_mined_transactions = updated_transactions
    except IOError:
        print("File not found")


def save_data():
    """Save blockchain + open transactions snapshot to a file."""
    with open('blockchain.txt', mode='w') as f:
        f.write(json.dumps(blockchain))
        f.write('\n')
        f.write(json.dumps(un_mined_transactions))
    print('File saved')


def valid_proof(transactions, last_hash, proof):
    guess = (str(transactions) + str(last_hash) + str(proof)).encode()
    guess_hash = hashlib.sha256(guess).hexdigest()
    print("Hash of Proof: ", guess_hash)
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
    """Calculate and return the balance for a participant."""
    tx_sender = [[tx['amount'] for tx in block['transactions']
                  if tx['sender'] == participant] for block in blockchain]
    open_tx_sender = [tx['amount']
                      for tx in un_mined_transactions if tx['sender'] == participant]
    tx_sender.append(open_tx_sender)
    amount_sent = reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt)
                         if len(tx_amt) > 0 else tx_sum + 0, tx_sender, 0)
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


def add_participant(sender):
    participant = OrderedDict(
            [
                ('name', sender['name']),
                ('id', sender['id']),
                ('properties', []),
                ('past_properties', [])
            ]
    )
    participants.append(participant)


def get_user_choice_int():
    user_input = int(input('input your choice: '))
    return user_input


def get_recipient_details_from_admin_database(index, admin_database):
    return admin_database['participants'][index]


def verify_recipent(user_input_name, user_input_id):
    for i in range(len(participants)):
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


def verify_property_actor(user_details, property_details):
    if property_details['property_actor'] == user_details['name'] and property_details['property_actor_id'] == user_details['id']:
        return True
    else:
        print('property actor invalid')
        return False


def verify_transaction(transaction):
    return True


def update(index, actor_database):
    past_properties = OrderedDict(
        [
            ('property_address', actor_database['properties'][index]['property_address']),
            ('property_next_actor_name', actor_database['properties'][index]['property_actor']),
            ('property_next_actor_id', actor_database['properties'][index]['property_actor_id'])
        ]
    )
    actor_database['past_properties'].append(past_properties)
    actor_database['properties'][index] = 0
    actor_database['properties'].pop(index)
    print('\n sender updated successfully\n')
    print('sender_details: ', actor_database)


def add_transaction(recipient, sender, property_details, amount=1.0, user_choice=-1):
    """ Append a new value as well as the last blockchain value to the blockchain."""
    recipient_name_and_id = OrderedDict(
        [
            ('name', recipient['name']),
            ('id', recipient['id'])
        ]
    )
    sender_name_and_id = OrderedDict(
        [
            ('name', sender['name']),
            ('id', sender['id'])
        ]
    )
    transaction = OrderedDict(
        [
            ('sender', sender_name_and_id),
            ('recipient', recipient_name_and_id),
            ('amount', amount),
            ('property_address', property_details['property_address'])
        ]
    )
    if verify_transaction(transaction):
        un_mined_transactions.append(transaction)
        property_details['property_actor'] = recipient['name']
        property_details['property_actor_id'] = recipient['id']
        recipient['properties'].append(property_details)
        if user_choice != -1:
            print('\n\n transfer_property user_choice', user_choice)
        save_data()
        return True
        
    return False


# register property on your name and save it into blockchain (this is a transaction)
def register_property():

    for i in range(len(admin_database['properties'])):
        print('Land # ',i, '=', admin_database['properties'][i]['property_address'])
    
    print('enter the number of property you want to choose')
    user_choice = get_user_choice_int()
    if 0 <= user_choice < len(admin_database['properties']):
        print('address selected is:\n', admin_database['properties'][user_choice]['property_address'])    #This is not needed
        property_details = admin_database['properties'][user_choice]
        recipient_details = actor_database
        sender_details = OrderedDict(
            [
                ('name', admin_database['name']),
                ('id', admin_database['id'])
            ]
        )
        if verify_property_actor(actor_database, property_details):
            print('property verified successfully ')
            if add_transaction(recipient_details, sender_details, property_details, amount=0):
                return True
        else:
            print('property not verified successfully ')
            return False
    else:
        print('user choice is invalid')


def transfer_property():
    print('\n')
    i = -1
    if len(actor_database['properties']) > 0:
        print('Owned Properties:\n')
        for i in range(len(actor_database['properties'])):
            print('Property number:', i, '=', actor_database['properties'][i]['property_address'], '\n')
    if i == -1:
        print('You don\'t have any property so you cannot transfer')
    else:
        print('Enter the number of property you want to choose: ', end='')
        user_choice = get_user_choice_int()
        print('Len of list actor_database[properties] = ', len(actor_database['properties']))
        if 0 <= user_choice < len(actor_database['properties']):
            print('Address selected is: ', actor_database['properties'][user_choice])
            property_details = actor_database['properties'][user_choice]
            x = get_recipient_details_from_user()
            if x != -1:
                recipient_details = get_recipient_details_from_admin_database(x, admin_database)
                amount = get_property_price()
                if add_transaction(recipient_details, actor_database, property_details, amount, user_choice):
                    print('Property sold successfully')
                    return True
                else:
                    print('Failure! Transaction failed')
                    return False
            elif x == -1:
                print('Recipient not registered, ask him to sign up first')
                return False
        else:
            print('user choice is invalid')
            return False


def print_user_details():
    print('user name: ', actor_database['name'])
    print('user id: ', actor_database['id'])
    print('user properties: ', actor_database['properties'])
    print('user past properties: ', actor_database['past_properties'])


def mine_block():
    """Create a new block and add open transactions to it."""
    last_block = blockchain[-1]
    encoded_block = json.dumps(last_block, sort_keys=True).encode()
    hashed_block = hashlib.sha256(encoded_block).hexdigest()
    proof = proof_of_work()
    actor = 'Sidharth'
    reward_transaction = OrderedDict(
        [
            ('sender', 'MINING'),
            ('recipient', actor),
            ('amount', REWARD)
        ]
    )
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
        if block['previous_hash'] != hashlib.sha256(json.dumps(blockchain[index-1], sort_keys=True).encode()).hexdigest():
            print('invalid previous hash at index: ', index)
            return False
        if not valid_proof(block['transactions'][:-1], block['previous_hash'], block['proof']):
            print('\ninvalid reason block transaction, prev hash, proof\n', block['transactions'][:-1], block['previous_hash'], block['proof'])
            print('Proof of work is invalid')
            return False
    return True


def verify_transactions():
    """Verifies all open transactions."""
    return all([verify_transaction(tx) for tx in un_mined_transactions])


def console():
    print('\n+-----------------------------+')
    print('1: Register your property')
    print('2: Sell your property')  # transfers property to Admin
    print('3: Mine a new block')
    print('4: Check Blockchain Validity')
    print('5: Tamper the chain')
    print('6: Display Un-mined Transactions')  # transactions those are open (yet to mine)
    print('7: Display Blockchain Blocks')
    print('8: Display Participants')
    print('9: Display Actor Details')  # displays actor and his/her properties' data.
    print('10: Quit')


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
            if register_property():
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
            if verify_chain():
                print('Blockchain is VALID!')
            else:
                print('Invalid Blockchain')
        elif user_choice == '5':
            # Make sure that you don't try to "hack" the blockchain if it's empty
            if len(blockchain) >= 1:
                # simply change the block at index '0'
                blockchain[0] = {
                    'previous_hash': '',
                    'index': 0,
                    'transactions': [{'sender': 'Chris', 'recipient': 'Max', 'amount': 100.0}]
                }
        elif user_choice == '6':
            print("Un-mined Transactions: ", un_mined_transactions)
        elif user_choice == '7':
            print_blockchain_elements()
        elif user_choice == '8':
            print(participants)
        elif user_choice == '9':
            print('\nProperty records of Actor: ', actor_database['name'])
            print_user_details()
        elif user_choice == '10':
            print('Exiting...')
            break
        else:
            print('Invalid input... Try again!')
