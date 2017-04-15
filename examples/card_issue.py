'''
Issue cards for new deck.
'''

import pypeerassets as pa
from binascii import hexlify
import random
provider = pa.RpcNode(testnet=True)
change_addr = "mhPuRGwWRyhXRhzSfzgfoPPFHPXgAyZVSz" 

deck = pa.Deck(**deck) # use deck from deck_spawn.py example

## utxo must be owned by the deck issuer
utxo = provider.select_inputs(0.02, deck.issuer)

# generate 9 receiver addresses
receivers = [pa.Kutil(network="tppc").address for i in range(9)]
# amounts for the receivers
amounts = [random.randint(1, 999) for i in range(9)]

issue = pa.CardTransfer(deck, receivers, amounts) # CardTransfer instance

raw_issue = hexlify(pa.card_issue(deck, issue, utxo, change_addr)).decode()

signed = provider.signrawtransaction(raw_issue)

provider.sendrawtransaction(signed["hex"]) # send the tx
