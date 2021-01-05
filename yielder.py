import csv
import argparse

###Yielding, normalizing
def open_file_lazy(file):
    ''' Yielding number of neuron, x and y coordinates. '''
    with open(file, 'r') as f:
        r = csv.reader(f, delimiter=',')
        next(r)          # skip header
        yield from r


def filter_point_data(file):
    '''Filtering point duplicities - yielding only unique points.'''
    x_crd, y_crd = None, None
    for data in open_file_lazy(file):                      
        if data[3] != x_crd and data[4] != y_crd:  #TODO validation for missing data
            x_crd, y_crd = data[3], data[4]
            if __name__ == '__main__': #if yielder used directly yield all data
                yield data
            else:
                yield (int(data[1]), float(x_crd), float(y_crd))
        else:
            continue


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
            print('Plotted neuron:', neuron, 'from file:', file)
        except ValueError:
            print('Neuron not found:', neuron, 'in file:', file)
            continue
    
    return min_x, max_x, min_y, max_y


###Saving to new file
def save_normalized_and_deduplicated_data_to_csv(file):
    with open(file, 'w', newline='') as f:
        spamwriter = csv.writer(f, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for i in filter_point_data(file):
            spamwriter.writerow(i)

if __name__ == '__main__':
    save_normalized_and_deduplicated_data_to_csv('w.csv')