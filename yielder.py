import csv
import argparse

###Yielding, normalizing
def open_file_lazy(file):
    ''' Yielding number of neuron, x and y coordinates. '''
    with open(file, 'r') as f:
        r = csv.reader(f, delimiter=',')
        yield from r


def filter_point_data(file):
    '''Filtering point duplicities - yielding only unique points.'''
    x_crd, y_crd = None, None
    f = open_file_lazy(file)
    next(f)                     # skip header

    for data in f:
        try:                            # if point data not succeed to cast into int/float, continue to next point 
            if (data[3] != x_crd or data[4] != y_crd): # at least one coord not equal in previous member in point
                x_crd, y_crd = data[3], data[4]
                yield (int(data[1]), float(x_crd), float(y_crd))
            else:
                continue
        except ValueError: # bad values
            continue
        except IndexError: # bad line len
            continue

def harvest_neuron_points(neuron, file):
    '''Harvesting neuron points into lists (x/y). '''
    source = filter_point_data(file)
    x_crds, y_crds = list(), list()

    for data in source:           # harvest all neuron points
        if data[0] == neuron: 
            x_crds.append(data[1])
            y_crds.append(data[2])
        elif data[0] > neuron:
            break

    return neuron, x_crds, y_crds


def find_min_and_max_values(x_coords, y_coords, min_x, max_x, min_y, max_y):
    '''Obtaining min and max values from single neuron for optimal graph framing. '''
    if min(x_coords) < min_x: min_x = min(x_coords)
    if max(x_coords) > max_x: max_x = max(x_coords)   
    if min(y_coords) < min_y: min_y = min(y_coords)
    if max(y_coords) > max_y: max_y = max(y_coords)
    return min_x, max_x, min_y, max_y


def transpone_neuron_data(x_crds):
    '''Transpone neuron from  \\ to / for comparer.py. '''
    rotational_edge = max(x_crds)
    x_crds_transponed = [abs(rotational_edge - x) for x in x_crds]
    transponed_min = min(x_crds_transponed)
    return x_crds_transponed, transponed_min


def normalize_point_data(neuron, min_x, min_y, file, transpone):
    '''Normalizing points for specific graph.'''
    neuron, x_crds, y_crds = harvest_neuron_points(neuron, file)

    if transpone:
        print('Transponing...')
        x_crds, min_x = transpone_neuron_data(x_crds)
    
    x_crds_norm = [x - min_x for x in x_crds]         
    y_crds_norm = [y - min_y for y in y_crds]

    return neuron, x_crds_norm, y_crds_norm     # normalized for 0,0 graph axes


### Yielding to csv file
def normalize_point_data_for_csv(file, duplicities):
    '''Nromalizing and optionally filtering data for output csv file. '''
    x_crd, y_crd = None, None
    f = open_file_lazy(file)

    yield next(f)               # yield header for csv file

    for data in f:      
        if not duplicities:
            if data[3] != x_crd or data[4] != y_crd:
                x_crd, y_crd = data[3], data[4]
                yield   (data[0], int(data[1]), data[2], # yield deduplicated
                        float(x_crd), float(y_crd), 
                        data[5], data[6], data[7], data[8],
                        data[9], data[10], data[11], 
                        data[12], data[13])
            else:
                continue
        else:
            yield   (data[0], int(data[1]), data[2], # yield all
                    float(data[3]), float(data[4]), 
                    data[5], data[6], data[7], data[8],
                    data[9], data[10], data[11], 
                    data[12], data[13])


def iterate_for_min_and_max_values(neur_group, file):
    '''Obtaining min and max values from neuron group 
    for optimal graph framing or normalizing data for csv. '''
    min_x, max_x, min_y, max_y = float('inf'), float('-inf'), float('inf'), float('-inf')

    for neuron in neur_group:
        neuron, x_coords, y_coords = harvest_neuron_points(neuron, file)

        if len(x_coords) < 3 and len(y_coords) < 3 and x_coords and y_coords:
            print('Neuron', neuron,'is too short for processing! Contains only', len(x_coords), 'point(s).')
            continue

        try:
            min_x, max_x, min_y, max_y = find_min_and_max_values(x_coords, y_coords, min_x, max_x, min_y, max_y)
            print('Processed neuron:', neuron, 'from file:', file)
        except ValueError:
            print('Neuron not found:', neuron, 'in file:', file)
            continue
    
    return min_x, max_x, min_y, max_y


### Processing data
def save_normalized_data_to_csv(read_file, write_file, last_neuron, allow_duplicities):
    '''Saving deduplicted and normalized data to new file. '''
    with open(write_file, 'w', newline='') as f:
        data = normalize_point_data_for_csv(read_file, allow_duplicities)
        header = next(data)
        writer = csv.writer(f, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(header)

        for neuron in range(1, last_neuron+1):
            min_x, _, min_y, _ = iterate_for_min_and_max_values((neuron, ), read_file)
            
            for row in data:
                if int(row[1]) == neuron:
                    writer.writerow([*row[:3], round(row[3]-min_x, 6), round(row[4]-min_y, 6), *row[5:]])
                else:
                    break


### Control
def cmd_control():
    '''Command line user interface. '''
    parser = argparse.ArgumentParser(description='Providing arguments for normalizing neuron point data for csv file output.')
    parser.add_argument('-fin', '--filename_input', 
                        help='Csv source of data. Structure: second column neuron number, third and fourth x,y coordinates.', 
                        type=str, required=True, dest='source')
    parser.add_argument('-fout', '--filename_output', 
                        help='Csv output.', 
                        type=str, required=True, dest='output')
    parser.add_argument('-n', '--count_of_neurons', 
                        help='Providing number of processed neurons in file', 
                        type=int, required=True, dest='count')
    parser.add_argument('-dup', '--allow_duplicities', 
                        help='Providing number of processed neurons in file', 
                        type=bool, required=False, dest='duplicities', default=False) # implicitlly not allowing dulicities
    args = parser.parse_args()

    save_normalized_data_to_csv(args.source, args.output, args.count, args.duplicities)


if __name__ == '__main__':
    cmd_control()
