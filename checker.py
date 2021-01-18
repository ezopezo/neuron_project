import csv
import argparse
import yielder as yld
from collections import Counter

def check_file(file):
    '''Checking file data for further processing. '''
    bad_lines = set()
    bad_neurons = set()
    x_crd, y_crd = None, None
    line = 0
    l = yld.open_file_lazy(file)

    next(l) # skip header
    neuron_points_number = Counter() 

    for data in l:
        line += 1
        try: 
            if len(data) != 14:
                bad_lines.add(line+1)

            if (data[3] != x_crd or data[4] != y_crd): 
                x_crd, y_crd = data[3], data[4]              # deduplication 
                int(data[1]), float(data[3]), float(data[4]) # chcking casting
                neuron_points_number[int(data[1])] += 1      # adding only passed points

        except ValueError: # bad value in line
            bad_lines.add(line+1)
            continue
        except IndexError: # bad line len 
            bad_lines.add(line+1)
            continue
    
    for neuron, num_of_points in neuron_points_number.items():
        if num_of_points < 3: 
            bad_neurons.add(neuron)
    
    if not bad_lines and not bad_neurons:
        print('All data in file passed correctly for usage with yielder/visualizer/comparer. ')
        print('Document has ', line+1, ' lines and last neuron number is ', data[1])
        print('Listing neurons and number of points... ')
        for neuron, num_of_points in neuron_points_number.items():
            print('Neuron number:',neuron ,'number of points (deduplicated):', num_of_points)
    elif bad_neurons or bad_lines:
        if bad_neurons:
            for bad_neuron in bad_neurons:
                print('Neuron number with length lower than 3 points:', bad_neuron, '-> delete, or modify neuron.')
        if bad_lines:
            for bad_line in bad_lines:
                print('Error at line', bad_line, '-> delete, or modify rows.')
    else:
        print('Undefined error with file.')


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