import copy


def flush(cards):
    return_value = []
    for suit in ["D", "H", "S", "C"]:
        return_value = []
        count = 0
        for card in cards:
            if card.get_suit() == suit:
                count += 1
                return_value.append(card)
        if count >= 5:
            return_value.sort(reverse=True, key=lambda item: item.get_val())
            return return_value
    return []


def straight(cards):
    temp_cards = [card.get_val() for card in cards]  # Get the values of the cards
    temp_cards = list(set(temp_cards))  # Remove duplicates
    temp_cards.sort()  # Sort the values
    straight_cards = []

    # If there's an Ace (14), add 1 for the Ace low straight (Ace, 2, 3, 4, 5)
    if 14 in temp_cards:
        temp_cards.append(1)

    # Now check for a straight: 5 consecutive values
    for i in range(len(temp_cards) - 4):
        if temp_cards[i] + 1 == temp_cards[i + 1] and temp_cards[i + 1] + 1 == temp_cards[i + 2] and temp_cards[
            i + 2] + 1 == temp_cards[i + 3] and temp_cards[i + 3] + 1 == temp_cards[i + 4]:
            # Found a straight, now return the corresponding cards
            straight_cards.append([card for card in cards if card.get_val() in temp_cards[i:i + 5]])
            straight_cards[len(straight_cards) - 1].sort(key=lambda card: card.get_val(), reverse=True)

    return list(reversed(straight_cards))


def quad_trip_pair(cards):
    quad_list = []
    trip_list = []
    pair_list = []
    temp_cards = cards[:]
    cards.sort(reverse=True, key=lambda item: item.get_val())
    while len(temp_cards) > 0:
        card = temp_cards[0]
        count = 0
        element = [card.get_val(), []]
        for c in temp_cards:
            if card.get_val() == c.get_val():
                count += 1
                element[1].append(c)
        if count == 2:
            pair_list.append(element)
        elif count == 3:
            trip_list.append(element)
        elif count == 4:
            quad_list.append(element)
        for a in temp_cards[:]:
            if a.get_val() == card.get_val():
                temp_cards.remove(a)
    quad_list.sort(reverse=True, key=lambda item: item[0])
    trip_list.sort(reverse=True, key=lambda item: item[0])
    pair_list.sort(reverse=True, key=lambda item: item[0])
    if quad_list:
        return_value = quad_list[0][1]
        i = 0
        while cards[i].get_val() == quad_list[0][0]:
            i += 1
        return 7, return_value.append(cards[i])
    elif trip_list and pair_list:
        return 6, trip_list[0][1] + pair_list[0][1]
    elif trip_list:
        return_value = trip_list[0][1]
        i = 0
        while cards[i].get_val() == trip_list[0][0]:
            i += 1
        return_value.append(cards[i])
        i += 1
        while cards[i].get_val() == trip_list[0][0]:
            i += 1
        return_value.append(cards[i])
        return 3, return_value
    elif pair_list:
        if len(pair_list) > 1:
            return_value = pair_list[0][1] + pair_list[1][1]
            i = 0
            while cards[i].get_val() == pair_list[0][0] or cards[i].get_val() == pair_list[1][0]:
                i += 1
            return_value.append(cards[i])
            return 2, return_value
        else:
            return_value = pair_list[0][1]
            i = -1
            for _ in range(3):
                i += 1
                while cards[i].get_val() == pair_list[0][0]:
                    i += 1
                return_value.append(cards[i])
            return 1, return_value
    else:
        return "", False


def compute_hand(personal, communal):
    cards = personal + communal
    flush_val = flush(cards)
    straight_val = straight(cards)
    quad_trip_pair_val = quad_trip_pair(cards)
    if straight_val:
        if flush_val:
            for s in straight_val:
                if s == flush_val:
                    if s[0].get_val == 14:
                        return 9, s
                    else:
                        return 8, s
    if quad_trip_pair_val[0] == 7:
        return quad_trip_pair_val
    elif quad_trip_pair_val[0] == 6:
        return quad_trip_pair_val
    elif flush_val:
        return 5, flush_val[:5]
    elif straight_val:
        return 4, straight_val[0]
    elif quad_trip_pair_val[0] == 3:
        return quad_trip_pair_val
    elif quad_trip_pair_val[0] == 2:
        return quad_trip_pair_val
    elif quad_trip_pair_val[0] == 1:
        return quad_trip_pair_val
    else:
        cards.sort(reverse=True, key=lambda item: item.get_val())
        return 0, cards[:5]


def compute_winner(players, community):
    hands = []
    compare = []
    names = []
    # Get the hand from each player
    for p in players:
        hands.append(compute_hand(p.get_cards(), community.get_cards()))
        names.append(p.get_name())
    hands_sorted = sorted(hands, reverse=True, key=lambda x: x[0])
    print(hands_sorted)
    # Sort through the hands and make a list of the best hand type
    i = 0
    same_hand = False
    while not same_hand and hands_sorted[i][0] == hands_sorted[0][0]:
        compare.append(hands_sorted[i])
        i += 1
        if i >= len(hands_sorted):
            same_hand = True
    print(same_hand)
    print(compare)
    # Go card by card to see who has the best 5 card hand
    if len(compare) > 1:
        for j in range(5):
            compare_val = []
            for c in compare:
                compare_val.append(c[1][j].get_val())
            print(compare_val)
            max_val = max(compare_val)
            to_remove = []
            for i in range(len(compare_val)):
                if compare_val[i] < max_val:
                    to_remove.append(i)
            for i in reversed(to_remove):
                del compare[i]
            if len(compare) == 1:
                break
    print(compare)
    # return list of all the winners ( usually just one )
    winners = []
    for winning_hand in compare:
        index = hands.index(winning_hand)
        winner = players[index]
        winners.append(winner)
    return winners
