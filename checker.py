import csv
import argparse
import yielder as yld

def check_file(file):
    '''Checking file data for further processing. '''
    lines = set()
    line = 0
    l = yld.open_file_lazy(file)
    next(l) # skip header

    for data in l:
        line += 1
        try: 
            if len(data) != 14:
                lines.add(line+1)
            int(data[1]), float(data[3]), float(data[4])
        except ValueError:
            lines.add(line+1)
            continue
    
    if not lines:
        print('All data in file passed correctly for usage with yielder/visualizer/comparer. ')
        print('Document has ', line+1, ' lines and last neuron number is ', data[1])
    else:
        print('Error(s) at line(s)', ' '.join(str(i) for i in lines), '-> delete, or modify rows.')


def cmd_control():
    '''Command line user interface. '''
    parser = argparse.ArgumentParser(description='Checking file data integrity. ')
    parser.add_argument('-fcheck', '--filename_check', 
                        help='Check csv data file for data correctness', 
                        type=str, required=True, dest='source')

    args = parser.parse_args()
    check_file(args.source)


if __name__ == '__main__':
    cmd_control()