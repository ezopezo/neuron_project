import csv
import matplotlib.pyplot as plt
from math import sqrt, sin, radians, acos, degrees
from copy import deepcopy
from statistics import median, mean
import numpy


def open_file_lazy(file):
    ''' Yielding number of neuron, x and y coordinates. Filtering duplicities of data'''
    with open(file, 'r') as f:
        r = csv.reader(f, delimiter=',')
        next(r)                                 # skip header
        x_crd, y_crd = None, None
        for i in r:                      
            if i[3] != x_crd and i[4] != y_crd: # filtering duplicities - yielding only unique points
                x_crd, y_crd = i[3], i[4]
                yield (i[1], x_crd, y_crd)      # TODO cast to int here
            else:
                continue

 
def create_bins(neuron, deviation_seq): # balance of data in bins?
    del deviation_seq[0] # removing zeros form beg. and end - not needed for averaging bins
    del deviation_seq[-1]

    identificator = [neuron]           # index 0 - neuron number

    splitted = numpy.array_split(numpy.array(deviation_seq), 25) # hard coded split
    bins = [sum(i) / len(i) for i in splitted]
    min_value = min(bins)
    max_value = max(bins)
    identificator.append(min(bins))    # index 1 - min bin value
    identificator.append(max(bins))    # index 2 - max bin value
    identificator.append(bins)         # index 3 - all bins of neuron
    return identificator


def evaluate_growth_deviation(neuron, x_coords, y_coords):
    # try to compute once for 1 neuron - class, computed property.
    length_x_axis = x_coords[0] # old max(x_coords) - not considernig end of central axis doest have to be max of y_cords or x_coords -> think about curly neuron
    length_y_axis = y_coords[0] # old max(y_coords) - should be zero?

    neuron_centr_ax_length = sqrt(length_x_axis**2 + length_y_axis**2) # axis connecting ends of neuron
    angle_b = acos((neuron_centr_ax_length**2 + length_y_axis**2 - length_x_axis**2) / (2*neuron_centr_ax_length*length_y_axis))
    angle_a = radians(90) - angle_b
    
    deviation = list()
    #print(degrees(angle_a), degrees(angle_b))

    for x, y in zip(x_coords, y_coords): # for every point of neuron avoiding duplicities in 
        # triangle for countuing missing coordinates on center neuron axis
        height_triangle_x_ax = y*sin(angle_b)/sin(angle_a) # good
        height_triangle_y_ax = x*sin(angle_a)/sin(angle_b)

        a_side = abs(height_triangle_x_ax - x)
        b_side = abs(height_triangle_y_ax - y)
        c_side = sqrt(a_side**2 + b_side**2)
        triangle_area = 0.5 * a_side * c_side * sin(angle_a)
        

        ### TODO need x,y for point where height touches central axis for evaluation what is under and what is above central axis. ### done
        # finding out if is point under the central axis (negative int) of above (positive int) for later comparing of shape.
        #triangle height => deviation of neuron from central axis ## if zero, app zero to list
        try:                                   # deviation may be important data product
            height = 2*triangle_area/c_side
            if height_triangle_y_ax < y:
                deviation.append(round(height, 10))
            else:
                deviation.append(round(-height, 10))
        except ZeroDivisionError:
            deviation.append(0)

    #prepared_bin = create_bins(deviation)
    #processing to create bins - every neuron divided to equal parts (one bin - average of certain subsequence of heights) for later cmopating - separate function

    
    identified_bins = create_bins(neuron, deviation)
    return identified_bins


def adjust_graph_axes(x_coords, y_coords, min_x, max_x, min_y, max_y):
    if x_coords < min_x: min_x = x_coords
    if x_coords > max_x: max_x = x_coords    
    if y_coords < min_y: min_y = y_coords
    if y_coords > max_y: max_y = y_coords
    return min_x, max_x, min_y, max_y


def normalizer(neuron, l):
    x_coords, y_coords = list(), list()

    for i in l:                     # obtain all neuron points
        if int(i[0]) == neuron: 
            x_coords.append(float(i[1]))
            y_coords.append(float(i[2]))
        elif int(i[0]) == neuron+1:
            break

    min_x = min(x_coords)           # find min for adjusting
    min_y = min(y_coords)

    for j, k in zip(x_coords, y_coords):
        x_crds_norm = j - min_x     # adjusting and yielding normalized points for 0,0 graph root
        y_crds_norm = k - min_y
        yield (neuron, x_crds_norm, y_crds_norm)



def plotter(neuron):
    l = open_file_lazy('c2pos5_points.csv')
    min_x, max_x, min_y, max_y = 1000,0,1000,0 # min and max axes # may be None - defined for masking with adjus_graph_axes() function
    x_coords, y_coords = list(), list()

    normalized_data = normalizer(neuron, l)

    for i in normalized_data:
        
        if int(i[0]) == neuron:
            x_coords.append(float(i[1]))
            y_coords.append(float(i[2]))
            min_x, max_x, min_y, max_y = adjust_graph_axes(float(i[1]), float(i[2]), min_x, max_x, min_y, max_y)
      
    plt.plot(x_coords, y_coords)
    plt.plot([x_coords[-1], x_coords[0]], [y_coords[-1], y_coords[0]]) # plot neuron center axis corrected form min/max approach
    #x_coords.clear() # needed for serial evaluation of all neurons
    #y_coords.clear()
    collection_first = list
    identified_bins = evaluate_growth_deviation(neuron, x_coords, y_coords)

    #comparer(neuron, deviation) # TODO solve and save negative numbers under the central axis - necessary for comparing (?) #done 
    plt.axis([min_x, max_x+20, min_y, max_y+20]) #adjust axes
    #plt.axis([min(x_coords), max(x_coords), min(y_coords), max(y_coords)])
    plt.suptitle('Neuron {}'.format(neuron))
    ##plt.show()
    return identified_bins

def tester():
    # mock neuron
    x_crds = [12, 8, 2]
    y_crds = [15, 4, 2]

    x_crds_norm = list()
    y_crds_norm = list()

    min_x = min(x_crds)
    max_x = max(x_crds)
    min_y = min(y_crds)
    max_y = max(y_crds)
    neuron = 3

    for x, y in zip(x_crds, y_crds): # normalisation for 0,0 starting graph
        x_crds_norm.append(x - min_x)
        y_crds_norm.append(y - min_y)

    plt.plot(x_crds_norm, y_crds_norm)
    plt.plot([0, x_crds_norm[0]], [0, y_crds_norm[0]])
    evaluate_growth_deviation(neuron, x_crds_norm, y_crds_norm)
    plt.plot([6, 6],[7.8, 2]) ## xx yy #hard coded for now
    plt.plot([6, 1.53],[2, 2]) ## xx yy
    plt.axis([0, x_crds_norm[0], 0, y_crds_norm[0]])
    
    plt.show()


def collector(): # can be fused with collector test into one generator called with arguments of scaned data and tested data
    for i in range(1, 6):
        try:
            identified_bins = plotter(neuron = i)
            yield identified_bins
        except:
            #print('Number of neuron not found, trying another...')
            continue



def collector_test(): # testing collector for spliting file for compare test
    for i in range(4, 10):
        try:
            identified_bins = plotter(neuron = i)
            yield identified_bins
        except:
            #print('Number of neuron not found, trying another...')
            continue


biggest_point_distance = 0

def calculate_each_bin_distance(packed_bins, signature):
    global biggest_point_distance
    distance_seq = list()

    distance_seq.append(signature)             # signature pair of neurons for direct [(first_neuron_num, second_neuron_num)]
    for first, other in packed_bins:
        if (first < 0 and other < 0) or (first > 0 and other > 0):
            distance = abs(first - other)
            distance_seq.append(distance)
            if biggest_point_distance < distance: # TODO separate to other function
                biggest_point_distance = distance
        else:
            distance = abs(first) + abs(other)
            distance_seq.append(distance)
            if biggest_point_distance < distance:
                biggest_point_distance = distance
    
    return distance_seq


def iterate_neuron_bin_sets():
    distance_seq_collection = list()
    distance_seq_reverse_collection = list()        # instance for reversing values of heights for miror comparation

    for j in collector():
        for k in collector_test():
            signature = tuple((j[0], k[0]))             # signature pair of neurons for direct [(first_neuron_num, second_neuron_num)]
            reversed_k_neuron = [-i for i in k[3]]      # for mirror comparing

            distance_seq_collection.append(calculate_each_bin_distance(zip(j[3], k[3]), 
                                                            signature + tuple((1,))))                       # direct comparation
            distance_seq_reverse_collection.append(calculate_each_bin_distance(zip(j[3], reversed_k_neuron), 
                                                                    signature + tuple((-1, ))))  # mirror comparation
    
    return zip(distance_seq_collection, distance_seq_reverse_collection)


def filtering_direct__mirror_comparisons():
    packed_collections = iterate_neuron_bin_sets()

    for direct, mirror in packed_collections:
        if sum(direct[1:]) > sum(mirror[1:]):
            yield mirror
        else:
            yield direct


def calculate_percentage_of_simmilarity_bins(): # [(1, 1), 98.2, 84.6,...]
    distance_percentage = list()
    for distance_collection_absolute in filtering_direct__mirror_comparisons():
        for index, distance in enumerate(distance_collection_absolute):
            if index == 0:
                distance_percentage.append(distance) # tuple with neuron identificators
            else:
                distance_percentage.append(100 - ((100*distance) / biggest_point_distance))

        yield distance_percentage
        distance_percentage.clear()

if __name__ == '__main__':
    #collector()         # first dataset
    #collector_test()    # second dataset
    for i in calculate_percentage_of_simmilarity_bins():
        print(i)
    #comparer()
    '''
    for i in range(1, 40):
        try:
            identified_bins = plotter(neuron = i)
        except:
            #print('Number of neuron not found, trying another...')
            continue
    '''
    #plotter(neuron = 9)
    #tester()
    pass

