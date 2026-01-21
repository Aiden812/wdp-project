
def calculate_similarity(user_interests, target_interests):
    if not user_interests or not target_interests:
        return 0

    user_set = set(user_interests)
    target_set = set(target_interests)

    common = user_set.intersection(target_set)
    total = user_set.union(target_set)

    return round((len(common) / len(total)) * 100)
