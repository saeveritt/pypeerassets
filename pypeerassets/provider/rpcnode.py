
'''Communicate with local or remote peercoin-daemon via JSON-RPC'''

from operator import itemgetter

try:
    from peercoin_rpc import Client
except:
    raise EnvironmentError("peercoin_rpc library is required for this to work,\
                            use pip to install it.")

class RpcNode(Client):
    '''JSON-RPC connection to local Peercoin node'''

    def select_inputs(self, total_amount, address=None):
        '''finds apropriate utxo's to include in rawtx, while being careful
        to never spend old transactions with a lot of coin age.
        Argument is intiger, returns list of apropriate UTXO's'''

        utxo = []
        utxo_sum = float(-0.01) ## starts from negative due to minimal fee
        for tx in sorted(self.listunspent(address=address), key=itemgetter('confirmations')):
            
            if self.getaccount(tx['address']) in ['PAprod','PAtest']:
                continue

            utxo.append({
                "txid": tx["txid"],
                "vout": tx["vout"],
                "scriptSig": tx["scriptPubKey"],
                "amount": tx["amount"],
                "address": tx["address"]
            })

            utxo_sum += float(tx["amount"])
            if utxo_sum >= total_amount:
                return {'utxos':utxo, 'total':utxo_sum}

        if utxo_sum < total_amount:
            raise ValueError("Not enough funds.")

    @property
    def is_testnet(self):
        '''check if node is configured to use testnet or mainnet'''

        if self.getinfo()["testnet"] is True:
            return True
        else:
            return False

    @property
    def network(self):
        '''return which network is the node operating on.'''

        if self.is_testnet:
            return "tppc"
        else:
            return "ppc"

    def listunspent(self, minconf=1, maxconf=999999, address=None):
        '''list UTXOs
        modified version to allow filtering by address.
        '''
        if address:
            return [u for u in self.req("listunspent", [minconf, maxconf]) if u["address"] == address]
        else:
            return self.req("listunspent", [minconf, maxconf])

    def getaccount(self, address=None):
        '''list UTXOs
        modified version to allow filtering by address.
        '''
        assert address is not None, 'Input address required.'
        
        return self.req("getaccount", [address])

