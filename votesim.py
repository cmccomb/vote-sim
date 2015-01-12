import numpy as np
from itertools import permutations


# Finds maximum value in a dict, returns key
def find_dict_max(some_dict):
    max_key = []
    max_val = -np.inf
  
    for k, v in some_dict.iteritems():
        if v > max_val:
            max_val = v
            max_key = k

    return max_key


# Finds minimum value in a dict, returns key
def find_dict_min(some_dict):
    min_key = []
    min_val = np.inf

    for k, v in some_dict.iteritems():
        if v < min_val:
            min_val = v
            min_key = k

    return min_key


# Returns list of keys in dict, ordered in terms of values
def sort_dict(some_dict, direction='ascending'):
    some_dict = some_dict.copy()

    if direction == 'ascending':
        find_next = find_dict_min
        reset = np.inf
    elif direction == 'descending':
        find_next = find_dict_max
        reset = -np.inf
    else:
        print("Please specify 'ascending' or 'descending'")
        return 0

    ordering = []
    for i in range(len(some_dict.keys())):
        key = find_next(some_dict)
        ordering.append(key)
        some_dict[key] = reset

    return ordering


# Voting Functions
def safe_copy(profile):
    prof = []
    for voter in profile[:]:
        temp = []
        for cand in voter[:]:
            temp.append(cand)
        prof.append(temp)

    return prof


def remove_candidate(profile, candidate):
    # Remove from profiles
    for voter in profile:
        voter.remove(candidate)


def plurality(profile):
    # Make dictionary
    candidates = dict.fromkeys(list(np.unique(profile[0])), 0)

    # Count votes
    for voter in profile:
        candidates[voter[0]] += 1

    # Return winner
    social_preference = sort_dict(candidates, 'descending')

    return social_preference, candidates


def veto(profile):
    # Make dictionary
    candidates = dict.fromkeys(list(np.unique(profile[0])), 0)

    # Count vetos
    for voter in profile:
        candidates[voter[-1]] += 1

    # Return winner
    social_preference = sort_dict(candidates, 'ascending')

    return social_preference, candidates


def borda(profile):
    # Make dictionary
    candidates = dict.fromkeys(list(np.unique(profile[0])), 0)

    # Count score
    for voter in profile:
        for idx, cand in enumerate(voter):
            candidates[cand] += idx

    # Return winner
    social_preference = sort_dict(candidates, 'ascending')

    return social_preference, candidates


def copeland(profile):
    # Make dictionary
    candidates = dict.fromkeys(list(np.unique(profile[0])), 0)
    all_names = candidates.keys()
    m = len(all_names)

    # Compare every pair of candidates
    for i in range(m):
        for j in range(i+1, m):
            # Find list of names for new profile
            names = profile[0][:]
            names.remove(all_names[i])
            names.remove(all_names[j])

            # Make the new profile
            prof = safe_copy(profile)
            for name in names:
                remove_candidate(prof, name)

            # Find winner
            sp, _ = plurality(prof)

            # Tally candidate wins/losses
            candidates[sp[0]] += 1
            candidates[sp[1]] -= 1

    social_preference = sort_dict(candidates, 'descending')

    return social_preference, candidates


def irv(profile):

    # Make new profile for safety
    prof = safe_copy(profile)

    # Get number of voters, alternatives
    m = len(prof[0])

    res = []
    sp = [0]
    social_preference = []
    while m > 1:
        # Find the loser
        sp, sc = plurality(prof)
        res.append(sc)
        social_preference.append(sp[-1])

        # Remove the loser from profiles
        remove_candidate(prof, sp[-1])

        # Get number of voters, alternatives
        m = len(prof[0])

    social_preference.append(sp[0])
    social_preference.reverse()

    return social_preference, res

RULES = [plurality, veto, borda, irv, copeland]


# Preference Profile
class PreferenceProfile(object):

    def __init__(self):
        # Don't do very much
        self.n = 0
        self.m = 0
        self.names = []
        self.profile = []
        self.prob = []

    def make_random_profile(self, n, m):
        # Store characteristics
        self.m = m
        self.n = n

        # Make list of names
        self.names = [format(i, '02d') for i in range(self.m)]

        # Get the profile
        self.profile = []
        for i in range(self.n):
            xn = self.names[:]
            np.random.shuffle(xn)
            self.profile.append(xn)

        # Make the probability comparison matrix
        self.prob = np.zeros([self.m, self.m])
        for voter in self.profile:
            for i, name1 in enumerate(self.names):
                for j, name2 in enumerate(self.names):
                    if voter.index(name1) > voter.index(name2):
                        self.prob[i, j] += 1.0

        self.prob /= len(self.profile)

    def set_profile(self, profile):
        # Store profile and characteristics
        self.profile = profile
        self.m = len(profile[0])
        self.n = len(profile)

        # Make list of names
        self.names = np.unique(profile[0])

        # Make the probability comparison matrix
        self.prob = np.zeros([self.m, self.m])
        for voter in self.profile:
            for i, name1 in enumerate(self.names):
                for j, name2 in enumerate(self.names):
                    if voter.index(name1) > voter.index(name2):
                        self.prob[i, j] += 1.0

        self.prob /= len(self.profile)

    def strategyproof(self, rule):
        # Check ranking as is
        sp, sc = rule(self.profile)
        winner = sp[0]

        # Create all permutations
        options = permutations(self.names)

        # Check all strategies
        for i in range(self.n):
            if self.profile[i][0] != winner:
                prof = safe_copy(self.profile)
                for strategy in options:
                    prof[i] = list(strategy)
                    sp, sc = rule(prof)
                    if self.profile[i].index(sp[0]) < \
                            self.profile[i].index(winner):
                        return False
        else:
            return True

    def unanimity(self, rule):
        # Check ranking as is
        sp, _ = rule(self.profile)

        for i, name1 in enumerate(self.names):
            for j, name2 in enumerate(self.names):
                if self.prob[i, j] == 1.0:
                    if sp.index(name1) < sp.index(name2):
                        return False
        else:
            return True