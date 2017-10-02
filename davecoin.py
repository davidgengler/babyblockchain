from flask import Flask
from flask import request
import json
import requests
import hashlib as hasher
import datetime as date
node = Flask(__name__)

class Block:
  def __init__(self, index, timestamp, data, previous_hash):
    self.index = index
    self.timestamp = timestamp
    self.data = data
    self.previous_hash = previous_hash
    self.hash = self.hash_block()
  
  def hash_block(self):
    sha = hasher.sha256()
    sha.update(str(self.index).encode('utf-8') + str(self.timestamp).encode('utf-8') + str(self.data).encode('utf-8') + str(self.previous_hash).encode('utf-8'))
    return sha.hexdigest()
		
def create_genesis_block():
	# Manually create the first block of davecoin. Index = 0.
	return Block(0, date.datetime.now(), {
		"proof-of-work": 7,
		"transactions": None
	}, "0")

miner_address = "34h5jk34h5-miner-address-k5j34h5634"
this_nodes_transactions = []

@node.route('/txion', methods=['POST'])
def transaction():
  # On each new POST request,
  # we extract the transaction data
  new_txion = request.get_json()
  # Then we add the transaction to our list
  this_nodes_transactions.append(new_txion)
  # Because the transaction was successfully
  # submitted, we log it to our console
  print("New transaction")
  print("FROM: {}".format(new_txion['from'].encode('ascii','replace')))
  print("TO: {}".format(new_txion['to'].encode('ascii','replace')))
  print("AMOUNT: {}\n".format(new_txion['amount']))
  # Then we let the client know it worked out
  return "Transaction sent successfully.\n"
	
def next_block(last_block):
	this_index = last_block.index + 1
	this_timestamp = date.datetime.now()
	this_data = "Davecoin Block " + str(this_index)
	this_hash = last_block.hash
	return Block(this_index, this_timestamp, this_data, this_hash)
	
blockchain = [create_genesis_block()]
previous_block = blockchain[0]

blocks_to_add_after_genesis = 15

for i in range(0, blocks_to_add_after_genesis):
	block_to_add = next_block(previous_block)
	blockchain.append(block_to_add)
	previous_block = block_to_add
	print("Block #" + str(block_to_add.index) +" has been added to the blockchain.")
	print("Hash: "+ block_to_add.hash)

@node.route('/blocks', methods=['GET'])
def get_blocks():
	chain_to_send = blockchain
	#Convert blocks to dictionary for json
	for block in chain_to_send:
		block_index = str(block.index)
		block_timestamp = str(block.timestamp)
		block_data = str(block.data)
		block_hash = block.hash
		block = {
			"index": block_index,
			"timestamp": block_timestamp,
			"data": block_data,
			"hash": block_hash
		}
		chain_to_send = json.dumps(chain_to_send)
	return chain_to_send

def find_new_chains():
	other_chains = []
	for node_url in peer_nodes:
		block = requests.get(node_url + "/blocks").content
		#convert json to python dictionary
		block = json.loads(block)
		other_chains.append(block)
	return other_chains
	
def consensus():
# get blocks from other nodes
	other_chains = find_new_chains()
	longest_chain = blockchain
	for chain in other_chains:
		if len(longest_chain) < len(chain):
			longest_chain = chain
	blockchain = longest_chain

def proof_of_work(last_proof):
	incrementor = last_proof + 1
	while not (incrementor % 7 == 0 and incrementor % last_proof == 0):
		incrementor += 1
	return incrementor

@node.route('/mine', methods = ['GET'])
def mine():
  # Get the last proof of work
  last_block = blockchain[len(blockchain) - 1]
  last_proof = last_block.data['proof-of-work']
  # Find the proof of work for
  # the current block being mined
  proof = proof_of_work(last_proof)
  # Reward miner for finding block
  this_nodes_transactions.append(
    { "from": "network", "to": miner_address, "amount": 1 }
  )
  # Gather data for new block
  new_block_data = {
    "proof-of-work": proof,
    "transactions": list(this_nodes_transactions)
  }
  new_block_index = last_block.index + 1
  new_block_timestamp = this_timestamp = date.datetime.now()
  last_block_hash = last_block.hash
  # Empty transaction list
  this_nodes_transactions[:] = []
  # Create new block
  mined_block = Block(
    new_block_index,
    new_block_timestamp,
    new_block_data,
    last_block_hash
  )
  blockchain.append(mined_block)
  # Let the client know we mined a block
  return json.dumps({
      "index": new_block_index,
      "timestamp": str(new_block_timestamp),
      "data": new_block_data,
      "hash": last_block_hash
  }) + "\n"
	
node.run()