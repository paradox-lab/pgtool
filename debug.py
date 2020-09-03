import argparse

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('integers', metavar='N', type=int, nargs='+',
                    help='an integer for the accumulator')
parser.add_argument('--sum', dest='accumulate', action='store_const',
                    const=sum, default=max,
                    help='sum the integers (default: find the max)')

args = parser.parse_args()
##print(args.accumulate(args.integers))

parser.count = 1
parser.good ='100014349312' #国行健身环大冒险
parser.area = '19_1601_3637_63160'
parser.timer = ""

print(parser.area)
    
