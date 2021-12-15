def get_permutations(a_list):
    perms = []
    get_permutations_helper(perms, [], a_list)
    return perms

def get_permutations_helper(perms, in_progress, a_list):
    # base case
    if len(a_list) == 0:
        perms.append(list(in_progress))
        return
    
    # recursive case
    for item in a_list:
        in_progress_copy = list(in_progress)
        in_progress_copy.append(item)
        a_list_copy = list(a_list)
        a_list_copy.remove(item)
        get_permutations_helper(perms, in_progress_copy, a_list_copy)
    

