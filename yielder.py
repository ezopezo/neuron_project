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
    next(f) # skip header
    for data in f:
        try:                      
            if data[3] != x_crd and data[4] != y_crd:
                x_crd, y_crd = data[3], data[4]
                yield (int(data[1]), float(x_crd), float(y_crd))
            else:
                continue
        except ValueError: # invalid_points (bad type) are silenced for neuron continuity
            continue
    


def filter_point_data_for_csv(file, duplicities):
    '''Filtering point duplicities - yielding only unique points.'''
    x_crd, y_crd = None, None
    f = open_file_lazy(file)
    yield next(f)
    for data in f:                      
        if not duplicities:
            if data[3] != x_crd and data[4] != y_crd:
                x_crd, y_crd = data[3], data[4]
                yield   (data[0], data[1], data[2], 
                        float(x_crd), float(y_crd), 
                        data[5], data[6], data[7], data[8],
                        data[9], data[10], data[11], 
                        data[12], data[13])
            else:
                continue
        else:
            yield   (data[0], data[1], data[2], 
                    float(data[3]), float(data[4]), 
                    data[5], data[6], data[7], data[8],
                    data[9], data[10], data[11], 
                    data[12], data[13])



def harvest_neuron_points(neuron, file):
    '''Harvesting neuron points into lists. '''
    source = filter_point_data(file)
    x_crds, y_crds = list(), list()

    for data in source:                 # harvest all neuron points
        if data[0] == neuron: 
            x_crds.append(data[1])
            y_crds.append(data[2])
        elif data[0] > neuron:
            break

    return neuron, x_crds, y_crds


def find_min_and_max_values(x_coords, y_coords, min_x, max_x, min_y, max_y):
    '''Obtaining min and max values from data for optimal graph framing. '''
    if min(x_coords) < min_x: min_x = min(x_coords)
    if max(x_coords) > max_x: max_x = max(x_coords)   
    if min(y_coords) < min_y: min_y = min(y_coords)
    if max(y_coords) > max_y: max_y = max(y_coords)
    return min_x, max_x, min_y, max_y


def normalize_point_data(neuron, min_x, min_y, file):
    '''Normalizing points for specific graph.'''
    neuron, x_crds, y_crds = harvest_neuron_points(neuron, file)

    x_crds_norm = [x - min_x for x in x_crds]         
    y_crds_norm = [y - min_y for y in y_crds]
    return neuron, x_crds_norm, y_crds_norm     # normalized for 0,0 graph axes


def iterate_for_min_and_max_values(neur_group, file):
    '''Obtaining min and max values from neuron group for optimal graph framing. '''
    min_x, max_x, min_y, max_y = float('inf'), float('-inf'), float('inf'), float('-inf')

    for neuron in neur_group:
        try:
            neuron, x_coords, y_coords = harvest_neuron_points(neuron, file)
            min_x, max_x, min_y, max_y = find_min_and_max_values(x_coords, y_coords, min_x, max_x, min_y, max_y)
            print('Processed neuron:', neuron, 'from file:', file)
        except ValueError:
            print('Neuron not found:', neuron, 'in file:', file)
            continue
    
    return min_x, max_x, min_y, max_y


### Processing data
def save_normalized_and_deduplicated_data_to_csv(read_file, write_file, last, duplicities):
    '''Saving deduplicted and normalized data to new file. '''
    with open(write_file, 'w', newline='') as f:
        data = filter_point_data_for_csv(read_file, duplicities)
        header = next(data)
        writer = csv.writer(f, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(header)
        for neuron in range(1, last+1):
            min_x, _, min_y, _ = iterate_for_min_and_max_values((neuron, ), read_file)
            for i in data:
                if int(i[1]) == neuron:
                    writer.writerow([*i[:3], round(i[3]-min_x, 6), round(i[4]-min_y, 6), *i[5:]])
                else:
                    break


def cmd_control():
    '''Command line user interface. '''
    parser = argparse.ArgumentParser(description='Providing arguments for normalizing neuron point data.')
    parser.add_argument('-fs', '--filename_source', 
                        help='Csv source of data. Structure: second column neuron number, third and fourth x,y coordinates.', 
                        type=str, required=True, dest='source')
    parser.add_argument('-fo', '--filename_output', 
                        help='Csv output.', 
                        type=str, required=True, dest='output')
    parser.add_argument('-n', '--count_of_neurons', 
                        help='Providing number of processed neurons in file', 
                        type=int, required=True, dest='count')
    parser.add_argument('-dup', '--allow_duplicities', 
                        help='Providing number of processed neurons in file', 
                        type=int, required=False, dest='duplicities', default=False)
    args = parser.parse_args()

    save_normalized_and_deduplicated_data_to_csv(args.source, args.output, args.count, args.duplicities)


if __name__ == '__main__':
    cmd_control()

# 'c2pos5_points.csv'