def binSearch(nUsersNonAllocated):
    left = 0
    right = nUsersNonAllocated
    while left < right:
        mid = (left + right) // 2
        if mid == left:
            break
        return mid
        left = mid
    return right

def calc(x):
    if x <= 65:
        print(f'{x} is valid')
        return True
    else:
        raise ValueError('x is not 65')
def test():
    maxC = 100
    result = 0
    left = 0
    right = maxC
    lastException = 0
    while left <= right:
        try:
            result = (left + right) // 2
            calc(result)
            # if no exception was raised:
            left = result
            if result == lastException-1:
                break
        except ValueError:
            right = result
            lastException = result
            print('Please enter a valid integer')
    
    print("RESULT->", result)

test()