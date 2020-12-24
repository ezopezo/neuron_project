import csv
import matplotlib.pyplot as plt


def open_file_lazy(file):
    ''' Yielding number of neuron, x and y coordinates. Filtering duplicities of data.'''
    with open(file, 'r') as f:
        r = csv.reader(f, delimiter=',')
        next(r)                                 # skip header
        x_crd, y_crd = None, None
        for i in r:                      
            if i[3] != x_crd and i[4] != y_crd: # filtering duplicities - yielding only unique points
                x_crd, y_crd = i[3], i[4]
                yield (int(i[1]), float(x_crd), float(y_crd))
            else:
                continue


def normalize_point_data(neuron, file, mode='all'):
    '''Normalizing points for specific graph.'''

    source = open_file_lazy(file)
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
        min_x = min(x_coords)               # find min for adjusting
        min_y = min(y_coords)

        x_crds_norm = [j - min_x for j in x_coords]         
        y_crds_norm = [k - min_y for k in y_coords]
        return neuron, x_crds_norm, y_crds_norm     # normalized for 0,0 graph axes


def plotter(neuron):
    '''Plot single chosen neuron from dataset. '''
    neuron, x_crds_norm, y_crds_norm = normalize_point_data(neuron, file='c2pos5_points.csv', mode='single')
    plt.plot(x_crds_norm, y_crds_norm)
    plt.axis([0, max(x_crds_norm)+20, 0, max(y_crds_norm)+20]) # adjust axes - hardcoded outside padding
    plt.suptitle('Neuron {}'.format(neuron))
    plt.show()


def adjust_graph_axes(x_coords, y_coords, min_x, max_x, min_y, max_y):
    '''Obtaining min and max values from data for optimal graph framing. '''
    if min(x_coords) < min_x: min_x = min(x_coords)
    if max(x_coords) > max_x: max_x = max(x_coords)   
    if min(y_coords) < min_y: min_y = min(y_coords)
    if max(y_coords) > max_y: max_y = max(y_coords)
    return min_x, max_x, min_y, max_y


def plotter_all(file):
    '''Plot all neurons. '''
    min_x, max_x, min_y, max_y = 1000,0,1000,0 # hardcoded for graph adjusting
    for neuron in range(1, 5000):
        try:
            neuron, x_crds, y_crds = normalize_point_data(neuron, file)
            plt.plot(x_crds, y_crds)
            min_x, max_x, min_y, max_y = adjust_graph_axes(x_crds, y_crds, min_x, max_x, min_y, max_y)
            print('Sucessfully plotted: ', neuron)
        except ValueError:
            print('Not found: ', neuron)
            continue
    plt.axis([min_x-20, max_x+20, min_y-20, max_y+20]) #adjust axes with hardocded padding
    title = input("Write graph title: ")
    plt.suptitle(title)
    plt.show()


if __name__ == "__main__":
    # first - vis neuron_num
    
    #plotter(1)

    # second - vis all_seq
    '''
    for i in range(1, 40):
        try:
            plotter(neuron = i)
            print('Passed: ', i)
        except ValueError:
            print('Not found: ', i)
            continue    
    '''
    # third - visualisation all_together
    plotter_all(file='c2pos5_points.csv')