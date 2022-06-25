def get_new_ratings(player_A_rating, player_B_rating, winner):
    '''
    https://mattmazzola.medium.com/understanding-the-elo-rating-system-264572c7a2b4
    '''
    player_A_win_prob = 1/(1+10**((player_B_rating-player_A_rating)/400))
    player_B_win_prob = 1/(1+10**((player_A_rating-player_B_rating)/400))
    if winner == "A":
	    player_A_new_rating = player_A_rating+15*(1-player_A_win_prob)
	    player_B_new_rating = player_B_rating+15*(0-player_B_win_prob)
    else:
	    player_A_new_rating = player_A_rating+15*(0-player_A_win_prob)
	    player_B_new_rating = player_B_rating+15*(1-player_B_win_prob)
    return [player_A_new_rating, player_B_new_rating]
