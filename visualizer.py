import csv
import matplotlib.pyplot as plt
import argparse


def open_file_lazy(file):
    ''' Yielding number of neuron, x and y coordinates. '''
    with open(file, 'r') as f:
        r = csv.reader(f, delimiter=',')
        next(r)                                 # skip header
        yield from r
        

def filter_point_data(file):
    '''Filtering point duplicities - yielding only unique points.'''

    x_crd, y_crd = None, None
    for i in open_file_lazy(file):                      
        if i[3] != x_crd and i[4] != y_crd: 
            x_crd, y_crd = i[3], i[4]
            yield (int(i[1]), float(x_crd), float(y_crd))
        else:
            continue


def normalize_point_data(neuron, file, mode):
    '''Normalizing points for specific graph.'''

    source = filter_point_data(file)
    x_coords, y_coords = list(), list()

    for i in source:                        # harvest all neuron points
        if i[0] == neuron: 
            x_coords.append(i[1])
            y_coords.append(i[2])
        elif i[0] > neuron:
            break

    if mode == 'all':
        return neuron, x_coords, y_coords   # return non-adjusted data for ploting all neurons
    
    if mode == 'single':
        min_x = min(x_coords)               # find min of neuron for 0,0 graph adjusting
        min_y = min(y_coords)

        x_crds_norm = [j - min_x for j in x_coords]         
        y_crds_norm = [k - min_y for k in y_coords]
        return neuron, x_crds_norm, y_crds_norm     # normalized for 0,0 graph axes


def plotter(neuron, file, pad=20):
    '''Plot single chosen neuron from dataset or sequence of chosen neurons. '''

    neuron, x_crds_norm, y_crds_norm = normalize_point_data(neuron, file, mode='single')
    plt.plot(x_crds_norm, y_crds_norm)
    plt.axis([0, max(x_crds_norm)+pad, 0, max(y_crds_norm)+pad]) # adjust axes - hardcoded outside padding
    plt.suptitle('Neuron {}'.format(neuron))
    plt.show()


def plot_neurons_sequentially(from_num, to_num, file, pad=20):
    '''Chose neurons to plot them sequentially. '''

    for neuron in range(from_num, to_num):
        try:
            plotter(neuron, file, pad)
            print('Passed: ', neuron)
        except ValueError:
            print('Not found: ', neuron)
            continue   


def adjust_graph_axes(x_coords, y_coords, min_x, max_x, min_y, max_y):
    '''Obtaining min and max values from data for optimal graph framing. '''

    if min(x_coords) < min_x: min_x = min(x_coords)
    if max(x_coords) > max_x: max_x = max(x_coords)   
    if min(y_coords) < min_y: min_y = min(y_coords)
    if max(y_coords) > max_y: max_y = max(y_coords)
    return min_x, max_x, min_y, max_y


def plot_range_of_neurons(*args, file, mode, pad=20):
    '''Plot range or group of neurons together. '''
    
    if mode == 'range' and len(args) == 2:
        group = range(*args)
    elif mode == 'group':
        group = args
    else:
        print('Wrong usage.')

    min_x, max_x, min_y, max_y = float('inf'), float('-inf'), float('inf'), float('-inf') # for graph adjusting

    for neuron in group:
        try:
            neuron, x_crds, y_crds = normalize_point_data(neuron, file, mode='all')
            plt.plot(x_crds, y_crds)
            min_x, max_x, min_y, max_y = adjust_graph_axes(x_crds, y_crds, min_x, max_x, min_y, max_y)
            print('Sucessfully plotted: ', neuron)
        except ValueError:
            print('Not found: ', neuron)
            continue

    plt.axis([min_x-pad, max_x+pad, min_y-pad, max_y+pad]) # adjust axes with provided padding
    title = input("Write graph title: ")
    plt.suptitle(title)
    plt.show()


if __name__ == "__main__":
    def cli_control():
        parser = argparse.ArgumentParser(description='Providing arguments for selective neuron graph plotting.')
        parser.add_argument('Filename', help='csv source of data, second column neuron number, third and fourth x,y coordinates required', type=str)
        parser.add_argument('Mode', help='', type=str)
        parser.add_argument('Padding', help='', type=int)

        args = parser.parse_args()

        # first - vis neuron_num
        #plotter(1, file='c2pos5_points.csv')

        # second - vis all_seq
        #plot_neurons_sequentially(1, 40, file='c2pos5_points.csv', pad=20)
        
        # third - visualisation group - range or group
        plot_range_of_neurons(1, file='c2pos5_points.csv', mode='group', pad=200)
