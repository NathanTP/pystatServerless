# import multiprocessing

import lambdamultiprocessing.lambdamultiprocessing as multiprocessing

def sq(x):
    return x * x

if __name__ == '__main__':
    p = multiprocessing.Pool(3)
    print(p.map(sq, [1,2,3]))
