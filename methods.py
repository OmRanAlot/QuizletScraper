def findLongest(arr):
    longest = 0
    for i in arr:
        if len(i) > longest:
            longest = len(i)
    
    return longest