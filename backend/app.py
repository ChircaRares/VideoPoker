import random
import flask
from flask import Flask, request
import json
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

player = None
deck = None
POINTS = 1000


@app.route("/cards/")
def deal_cards():
    nr_of_cards = int(request.args.get("number"))
    which_deal = request.args.get("deal")
    pos = 0
    global player
    global deck

    if which_deal == "first_deal":
        player = Player()
        deck = Deck()
        deck.shuffle()
    else:
        pos = int(request.args.get("pos"))

    for i in range(nr_of_cards):
        if which_deal == "first_deal":
            player.add_card(deck.deal())
        elif which_deal == "another_deal":
            player.insert_card(deck.deal(), pos)
            player.remove_card(pos+1)
        else:
            pass
    cards_list = list()
    for card in player.cards:
        card_data = json.loads(json.dumps(str(card)))
        cards_list.append(card_data)

    return flask.jsonify(cards_list)


@app.route("/points")
def get_points():
    global POINTS
    mode = request.args.get("mode")
    hand_cost = 20

    if mode == "new_deal":
        POINTS -= hand_cost
    else:
        pass
    return str(POINTS)


@app.route("/win")
def winning_hand():
    final_cards = request.args.get("finalCards").split(',')
    msg = won_hand(final_cards)
    return msg


class Card(object):
    RANKS = (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14)

    SUITS = ("♠", "♢", "♡", "♣")

    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

    def __repr__(self):
        if self.rank == 14:
            rank = 'A'
        elif self.rank == 13:
            rank = 'K'
        elif self.rank == 12:
            rank = 'Q'
        elif self.rank == 11:
            rank = 'J'
        else:
            rank = self.rank
        return str(rank) + self.suit


class Deck(object):
    def __init__(self):
        self.deck = []
        for suit in Card.SUITS:
            for rank in Card.RANKS:
                card = Card(rank, suit)
                self.deck.append(card)

    def shuffle(self):
        random.shuffle(self.deck)

    def deal(self):
        return self.deck.pop(0)


class Player(object):
    def __init__(self):
        self.cards = []

    def add_card(self, card):
        self.cards.append(card)

    def insert_card(self, card, pos):
        self.cards.insert(pos, card)

    def remove_card(self, pos):
        self.cards.pop(pos)


class PokerHand(object):
    def __init__(self, cards):
        self.cards = cards

    def straight(self):
        vals = get_vals(self.cards)

        if vals[4] == 14 and vals[0] == 2 and vals[1] == 3 and vals[2] == 4 and vals[3] == 5:
            return 5
        if not vals[0] + 1 == vals[1]:
            return False
        if not vals[1] + 1 == vals[2]:
            return False
        if not vals[2] + 1 == vals[3]:
            return False
        if not vals[3] + 1 == vals[4]:
            return False

        return vals[4]

    def flush(self):
        suits = []
        for card in self.cards:
            suits.append(card.suit)
        if len(set(suits)) == 1:
            return True
        return False

    def pairs(self):
        pairs = []
        vals = get_vals(self.cards)
        for value in vals:
            if vals.count(value) == 2 and value not in pairs:
                pairs.append(value)
        return pairs

    def four_of_a_kind(self):
        vals = get_vals(self.cards)
        for value in vals:
            if vals.count(value) == 4:
                return True
        return False

    def full_house(self):
        vals = get_vals(self.cards)

        rank1 = vals[0]
        rank2 = vals[-1]
        nr_rank1 = vals.count(rank1)
        nr_rank2 = vals.count(rank2)
        if (nr_rank1 == 3 and nr_rank2 == 2) or (nr_rank1 == 2 and nr_rank2 == 3):
            return True
        return False

    def three_of_a_kind(self):
        vals = get_vals(self.cards)
        for value in vals:
            if vals.count(value) == 3 and len(set(vals)) == 3:
                return True
        return False


def won_hand(final_cards):
    global POINTS
    player_cards = []

    for cards in final_cards:
        if cards[0] != '1':
            rank = cards[0]
            if rank == "A":
                rank = 14
            if rank == "K":
                rank = 13
            if rank == "Q":
                rank = 12
            if rank == "J":
                rank = 11
            suit = cards[1]
            player_cards.append(Card(int(rank), suit))
        else:
            rank = cards[0] + cards[1]
            suit = cards[2]
            player_cards.append(Card(int(rank), suit))

    score = PokerHand(player_cards)
    is_straight = score.straight()
    is_flush = score.flush()
    is_three_of_a_kind = score.three_of_a_kind()
    is_pairs = score.pairs()
    is_four_of_a_kind = score.four_of_a_kind()
    is_full_house = score.full_house()

    if is_straight and is_flush and is_straight == 14:
        msg = "Royal flush: +10000points"
        POINTS += 10000
    elif is_straight and is_flush:
        msg = "Straight flush: +2500points"
        POINTS += 2500
    elif is_four_of_a_kind:
        msg = "Four of a kind: +1000points"
        POINTS += 1000
    elif is_full_house:
        msg = "Full house: +500points"
        POINTS += 500
    elif is_flush:
        msg = "Flush: +250points"
        POINTS += 250
    elif is_straight:
        msg = "Straight: +200points"
        POINTS += 200
    elif is_three_of_a_kind:
        msg = "Three of a kind: +75points"
        POINTS += 75
    elif len(is_pairs) == 2:
        msg = "Two pairs: +50points"
        POINTS += 50
    elif is_pairs and is_pairs[0] >= 11:
        msg = "Jacks or better: +10points"
        POINTS += 10
    else:
        msg = "Better luck next hand"

    return msg


def get_vals(cards):
    vals = []
    for card in cards:
        vals.append(card.rank)
    vals.sort()
    return vals
