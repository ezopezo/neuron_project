import csv
import matplotlib.pyplot as plt
import argparse


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
        if data[3] != x_crd and data[4] != y_crd: 
            x_crd, y_crd = data[3], data[4]
            yield (int(data[1]), float(x_crd), float(y_crd))          
        else:
            continue


def normalize_point_data(neuron, file, mode):
    '''Normalizing points for specific graph.'''
    source = filter_point_data(file)
    x_crds, y_crds = list(), list()

    for data in source:                        # harvest all neuron points
        if data[0] == neuron: 
            x_crds.append(data[1])
            y_crds.append(data[2])
        elif data[0] > neuron:
            break

    if mode == 'all':
        return neuron, x_crds, y_crds   # return non-adjusted data for ploting all neurons
    
    if mode == 'single':
        min_x = min(x_crds)               # find min of neuron for 0,0 graph adjusting
        min_y = min(y_crds)

        x_crds_norm = [x - min_x for x in x_crds]         
        y_crds_norm = [y - min_y for y in y_crds]
        return neuron, x_crds_norm, y_crds_norm     # normalized for 0,0 graph axes


def plotter(neuron, file, pad=20):
    '''Plot single chosen neuron from dataset or produce sequence of chosen neurons. '''
    try:
        neuron, x_crds_norm, y_crds_norm = normalize_point_data(neuron, file, mode='single')
        print('Plotted neuron: ', neuron)
    except ValueError:
        print('Neuron with number ', neuron, 'not presented in file.')
        return False
    
    plt.plot(x_crds_norm, y_crds_norm)
    plt.axis([0, max(x_crds_norm)+pad, 0, max(y_crds_norm)+pad]) # adjust axes - hardcoded outside padding
    plt.suptitle('Neuron {}'.format(neuron))
    plt.show()


def plot_neurons_sequentially(from_num, to_num, file, pad=20):
    '''Invoke plotter for sequential plotting och choosen range of neurons. '''
    for neuron in range(from_num, to_num):
        try:
            plotter(neuron, file, pad)
        except ValueError:
            continue   


def adjust_graph_axes(x_coords, y_coords, min_x, max_x, min_y, max_y):
    '''Obtaining min and max values from data for optimal graph framing. '''
    if min(x_coords) < min_x: min_x = min(x_coords)
    if max(x_coords) > max_x: max_x = max(x_coords)   
    if min(y_coords) < min_y: min_y = min(y_coords)
    if max(y_coords) > max_y: max_y = max(y_coords)
    return min_x, max_x, min_y, max_y


def plot_range_of_neurons(*args, file, mode, pad):
    '''Plot range or group of neurons together on graph. '''
    if mode == 'range' and len(args) == 2 and args[0] < args[1]:
        group = range(*args)
    elif mode == 'group':
        group = args
    else:
        print('Wrong usage.')
        return False

    min_x, max_x, min_y, max_y = float('inf'), float('-inf'), float('inf'), float('-inf') # for graph adjusting

    for neuron in group:
        try:
            neuron, x_crds, y_crds = normalize_point_data(neuron, file, mode='all')
            plt.plot(x_crds, y_crds)
            min_x, max_x, min_y, max_y = adjust_graph_axes(x_crds, y_crds, min_x, max_x, min_y, max_y)
            print('Plotted neuron: ', neuron)
        except ValueError:
            print('Not found: ', neuron)
            continue

    plt.axis([min_x-pad, max_x+pad, min_y-pad, max_y+pad]) # adjust axes with provided padding
    title = input("Write graph title: ")
    plt.suptitle(title)
    plt.show()


def cli_control():
    parser = argparse.ArgumentParser(description='Providing arguments for selective neuron graph plotting.')
    parser.add_argument('-f', '--filename', help='Csv source of data. Structure: second column neuron number, third and fourth x,y coordinates.', type=str, required=True, dest='filename')
    parser.add_argument('-m', '--mode', help='Options: [ single | burst | range | group ]', type=str, required=True, dest='mode')
    parser.add_argument('-p', '--padding', help='Adjusting grapth neuron. Default=20', type=int, required=False, dest='padding', default=20)
    parser.add_argument('-n_first', '--neuron_f', help='Single neuron or first neuron of burst/range/group of neurons plotted.', type=int, required=True, dest='neuron_first')
    parser.add_argument('-n_other', '--neuron_s', help='Second neuron for burst/range, or arbitrary number of neurons for group mode.', nargs='*', type=int, dest='neuron_second')

    args = parser.parse_args()

    if args.mode == 'single':
        plotter(args.neuron_first, args.filename, args.padding)
    elif args.mode == 'burst' and args.neuron_second:
        plot_neurons_sequentially(args.neuron_first, args.neuron_second[0], args.filename, args.padding)
    elif args.mode == 'range':
        plot_range_of_neurons(args.neuron_first, args.neuron_second[0], file=args.filename, mode=args.mode, pad=args.padding)
    elif args.mode == 'group': # fix
        args_ = (args.neuron_first, ) + tuple(args.neuron_second)
        plot_range_of_neurons(*args_, file=args.filename, mode=args.mode, pad=args.padding)
    else:
        print('Wrong usage. Check command line arguments.')


if __name__ == "__main__":
    cli_control()
