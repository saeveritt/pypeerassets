import warnings
from pypeerassets.kutil import Kutil
from pypeerassets.protocol import Deck
from pypeerassets import pavoteproto
from hashlib import sha256
from binascii import unhexlify
from pypeerassets import transactions
from .networks import query, networks


def deck_vote_tag(deck):
    '''deck vote tag address'''

    deck_vote_tag_privkey = sha256(unhexlify(deck.asset_id) + b"vote_init").hexdigest()
    deck_vote_tag_address = Kutil(deck.network, privkey=deck_vote_tag_privkey)
    return deck_vote_tag_address.address


class Vote:

    def __init__(self, version: int, description: str, count_mode: str,
                 start_block: int, end_block: int, choices=[],
                 vote_metainfo=""):
        '''initialize vote object'''

        self.version = version
        self.description = description
        self.choices = choices
        self.count_mode = count_mode
        self.start_block = start_block  # at which block does vote start
        self.end_block = end_block  # at which block does vote end
        self.vote_metainfo = vote_metainfo  # any extra info describing the vote

    @property
    def vote_info_to_protobuf(self):
        '''encode vote into protobuf'''

        vote = pavoteproto.Vote()
        vote.version = self.version
        vote.description = self.description
        vote.count_mode = vote.MODE.Value(self.count_mode)
        vote.start_block = self.start_block
        vote.end_block = self.end_block
        vote.choices.extend(self.choices)

        if not isinstance(self.vote_metainfo, bytes):
            vote.vote_metainfo = self.vote_metainfo.encode()
        else:
            vote.vote_metainfo = self.vote_metainfo

        proto = vote.SerializeToString()

        if len(proto) > 80:
            warnings.warn('\nMetainfo size exceeds maximum of 80 bytes allowed by OP_RETURN.')

        return proto

    @property
    def vote_info_to_dict(self):
        '''vote info as dict'''

        return {
            "version": self.version,
            "description": self.description,
            "count_mode": self.count_mode,
            "start_block": self.start_block,
            "end_block": self.end_block,
            "choices": self.choices
        }


def parse_vote_info(protobuf: bytes) -> dict:
    '''decode vote init tx op_return protobuf message and validate it.'''

    vote = pavoteproto.Vote()
    vote.ParseFromString(protobuf)

    assert vote.version > 0, {"error": "Vote info incomplete, version can't be 0."}

    return {
        "version": vote.version,
        "description": vote.description,
        "count_mode": vote.MODE.Name(vote.count_mode),
        "choices": vote.choices,
        "start_block": vote.start_block,
        "end_block": vote.end_block,
        "metainfo": vote.vote_metainfo
    }


def vote_init(vote: Vote, deck: Deck, inputs: list, change_address: str) -> bytes:
    '''initialize vote transaction, must be signed by the deck_issuer privkey'''

    network_params = query(deck.network)
    deck_vote_tag_address = deck_vote_tag(deck)

    tx_fee = network_params.min_tx_fee  # settle for min tx fee for now

    for utxo in inputs['utxos']:
        utxo['txid'] = unhexlify(utxo['txid'])
        utxo['scriptSig'] = unhexlify(utxo['scriptSig'])

    outputs = [
        {"redeem": 0.01, "outputScript": transactions.monosig_script(deck_vote_tag_address)},
        {"redeem": 0, "outputScript": transactions.op_return_script(vote.vote_info_to_protobuf)},
        {"redeem": float(inputs['total']) - float(tx_fee) - float(0.01),
         "outputScript": transactions.monosig_script(change_address)
         }]

    return transactions.make_raw_transaction(deck.network, inputs['utxos'], outputs)


def find_vote_init(provider, deck):
    '''find vote_inits on this deck'''
    pass


def vote_cast(deck: Deck, deck_vote_tag: str, vote: Vote, inputs: list,
              change_address: str) -> bytes:
    '''vote cast transaction'''
    pass
