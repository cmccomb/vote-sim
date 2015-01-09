from numpy import dot, unique, max, inf, round, zeros, mean, ones, delete
from numpy.random import shuffle, normal
from random import choice, sample
from itertools import permutations, combinations
from scipy.io import loadmat


# Finds maximum value in a dict, returns key
def find_dict_max(some_dict):
    max_key = []
    max_val = -inf
  
    for k, v in some_dict.iteritems():
        if v > max_val:
            max_val = v
            max_key = k

    return max_key


# Finds minimum value in a dict, returns key
def find_dict_min(some_dict):
    min_key = []
    min_val = inf

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
        reset = inf
    elif direction == 'descending':
        find_next = find_dict_max
        reset = -inf
    else:
        print("Please specify 'ascending' or 'descending'")
        return 0

    ordering = []
    for i in range(len(some_dict.keys())):
        key = find_next(some_dict)
        ordering.append(key)
        some_dict[key] = reset

    return ordering


## Voting Functions
def make_safe_profile(profile):
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
    candidates = dict.fromkeys(list(unique(profile[0])), 0)

    # Count votes
    for voter in profile:
        candidates[voter[0]] += 1

    # Return winner
    social_preference = sort_dict(candidates, 'descending')

    return social_preference, candidates


def veto(profile):
    # Make dictionary
    candidates = dict.fromkeys(list(unique(profile[0])), 0)

    # Count vetos
    for voter in profile:
        candidates[voter[-1]] += 1

    # Return winner
    social_preference = sort_dict(candidates, 'ascending')

    return social_preference, candidates


def borda(profile):
    # Make dictionary
    candidates = dict.fromkeys(list(unique(profile[0])), 0)

    # Count score
    for voter in profile:
        for idx, cand in enumerate(voter):
            candidates[cand] += idx

    # Return winner
    social_preference = sort_dict(candidates, 'ascending')

    return social_preference, candidates


def copeland(profile):
    # Make dictionary
    candidates = dict.fromkeys(list(unique(profile[0])), 0)
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
            prof = make_safe_profile(profile)
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
    prof = make_safe_profile(profile)

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


## Preference Profile
class SubProfile(object):

    def __init__(self, profile):
        self.orig_profile = profile
        self.n = len(self.orig_profile)
        self.m = len(self.orig_profile[0])
        self.names = list(unique(self.orig_profile[0]))

    def make_reduced_profile(self, candidates):
        # Figure out which to remove
        to_remove = list(set(self.names) - set(candidates))

        # Make a new profile
        self.temp_profile = make_safe_profile(self.orig_profile)
        self.temp_names = candidates

        # Remove as appropriate
        for cand in to_remove:
            remove_candidate(self.temp_profile, cand)

        # Make a probability matrix
        m = len(self.temp_profile[0])
        probs = zeros([m, m])
        for voter in self.temp_profile:
            for i, name1 in enumerate(self.temp_names):
                for j, name2 in enumerate(self.temp_names):
                    if voter.index(name1) > voter.index(name2):
                        probs[i,j] += 1.0

        self.temp_probs = probs/len(self.temp_profile)

    def strategyproof(self, rule):
        # Get number of voters, alternatives
        names = list(unique(self.temp_profile[0]))
        m = len(names)
        n = len(self.temp_profile)

        # Check ranking as is
        sp, sc = rule(self.temp_profile)
        winner = sp[0]

        # Create all permutations
        options = permutations(names)

        # Check all strategies
        for i in range(n):
            if self.temp_profile[i][0] != winner:
                prof = make_safe_profile(self.temp_profile)
                for strategy in options:
                    prof[i] = list(strategy)
                    sp, sc = rule(prof)
                    if self.temp_profile[i].index(sp[0]) < \
                            self.temp_profile[i].index(winner):
                        return False
        else:
            return True

    def unanimity(self, rule):
        # Check ranking as is
        sp, _ = rule(self.temp_profile)

        for i, name1 in enumerate(self.temp_names):
            for j, name2 in enumerate(self.temp_names):
                if self.temp_probs[i, j] == 1.0:
                    if sp.index(name1) < sp.index(name2):
                        return False
        else:
            return True


class FullEmpiricalProfile(object):

    def __init__(self, target, delt=0.1):
        MAT = loadmat(target)

        # This loads the predicted ratings, and sorts them.
        ratings = MAT["predicted_ratings"].T
        self.full_mat = MAT["full_mat"]
        self.alpha_mean = MAT["alpha_mean"]
        self.chol_cov = MAT["chol_cov"]
        m = len(ratings[0])
        names = [format(i, '02d') for i in range(m)]
        profile = []
        for voter in ratings:
            temp = [(voter[i], names[i]) for i in range(m)]
            temp2 = sorted(temp, reverse=True)
            ranking = [temp2[i][1] for i in range(m)]
            profile.append(ranking)

        self.profile = profile
        self.n = len(self.profile)
        self.m = len(self.profile[0])
        self.names = list(unique(self.profile[0]))

        probs = delt*ones([self.m, self.m])
        for voter in profile:
            for i, name1 in enumerate(self.names):
                for j, name2 in enumerate(self.names):
                    if voter.index(name1) > voter.index(name2):
                        probs[i, j] += 1.0

        probs /= (self.n+delt)

        self.probs = probs

    def make_random_team(self, n_team, n_cand):
        # Make the new profile
        new_profile = []
        for i in range(n_team):
            x = self.names[:]
            shuffle(x)
            new_profile.append(x)

        # Select some candidates
        new_names = sample(self.names, n_cand)

        p = SubProfile(new_profile)
        p.make_reduced_profile(new_names)

        return p

    def make_empirical_team(self, n_team, n_cand):
        # Make the new profile
        new_profile = []
        for _ in range(n_team):
            j = choice(range(self.n))
            new_profile.append(self.profile[j][:])

        # Select some candidates
        new_names = sample(self.names, n_cand)

        p = SubProfile(new_profile)
        p.make_reduced_profile(new_names)

        return p

    def make_empirical_team2(self, n_team, n_cand):
        # Go through and generate set of ratings
        all_ratings = []
        for i in range(n_team):
            temp = normal(size=7)
            alpha = self.alpha_mean + dot(self.chol_cov, temp)
            rating = dot(self.full_mat, alpha.T)
            all_ratings.append(rating)

        # From ratings, generate rankings
        m = len(all_ratings[0])
        names = [format(i, '02d') for i in range(m)]
        profile = []
        for voter in all_ratings:
            temp = [(voter[i], names[i]) for i in range(m)]
            temp2 = sorted(temp, reverse=True)
            ranking = [temp2[i][1] for i in range(m)]
            profile.append(ranking)

        # Select some candidates
        new_names = sample(self.names, n_cand)

        p = SubProfile(profile)
        p.make_reduced_profile(new_names)

        return p




