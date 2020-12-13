import csv
import matplotlib.pyplot as plt
from math import sqrt, sin, radians, acos, degrees
from itertools import islice


def open_file_lazy(file):
    ''' Yielding number of neuron, x and y coordinates. Filtering duplicities of data'''
    with open(file, 'r') as f:
        r = csv.reader(f, delimiter=',')
        next(r)                                 # skip header
        x_crd, y_crd = None, None
        for i in r:                      
            if i[3] != x_crd and i[4] != y_crd: # filtering duplicities - yielding unique points
                x_crd, y_crd = i[3], i[4]
                yield (i[1], x_crd, y_crd) 
            else:
                continue


'''
def comparer(neuron, deviation): # 100% match should be with itself in duplicated file -> (1, 1, 100%)
    x_coords, y_coords = list(), list()
    compared_file = open_file_lazy('c2pos5_points.csv')
    normalized_oth_neur = normalizer(2, compared_file) # first number indicates first neuron in other_file - need to be incremented with respect of missing neurons
    for i in normalized_oth_neur:
        if int(i[0]) == 2:
            x_coords.append(float(i[1]))
            y_coords.append(float(i[2]))

    other_deviation = evaluate_growth_deviation(3, x_coords, y_coords)

    # normalizing length - i can compare only neurons with equal length

    # comparing
    print(len(deviation), len(other_deviation))
    for first, other in zip(deviation, other_deviation): # what about reverse?
        try:
            ratio = (other-first)/((other+first)/2)*100 # percentage difference formula
        except ZeroDivisionError:
            pass
        print('ratio: ', ratio, first, other)
'''
 
def create_bins(deviation_seq): # refactor!!!!!!!!!!!! important algorithm, awful implementation, problematic implementation - bad balanced end ...[33, 34, 35, 36], [37]]
    del deviation_seq[0] # removing zeros form beg. and end - not needed for averaging bins
    del deviation_seq[-1]
    bins = list()
    average = list()
    l = round(len(deviation_seq)/10) # therd coded pieces for now - should be based on shortest sequence of deviation from neuron 
    extended = len(deviation_seq) % l # how many last bins shoul be extendend by
    
    for i in range(1, 10+1): 
        bins.append(deviation_seq[i*l-l:i*l])

    last = deviation_seq[i*l:]
    print(bins)
    if last:
        for j in range(-len(last), 0):
            bins[j-1] += bins[j][:len(last)+j]
            del bins[j][:len(last)+j]
        bins[-1] += last

    print(bins)
    if bins[-1] == []: # shorten truthiness
        for k in range(-1, -len(bins[0]), -1):
            bins[k] += bins[k-1][-(len(bins[0])+k):]
            del bins[k-1][-(len(bins[0])+k):]
    print(bins)
    print(len(bins))
    #average.append(sum(deviation_seq[i*l:]) / len(deviation_seq[i*l:]))
    # print(average)
  


print(create_bins([0, 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,0]))


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
        try:
            height = 2*triangle_area/c_side
            if height_triangle_y_ax < y:
                deviation.append(round(height, 10))
            else:
                deviation.append(round(-height, 10))
        except ZeroDivisionError:
            deviation.append(0)

    #prepared_bin = create_bins(deviation)
    #processing to create bins - every neuron divided to equal parts (one bin - average of certain subsequence of heights) for later cmopating - separate function

    #print(deviation)
    #print(len(deviation))
    print()
    print('Neuron', neuron, 'deviation: ', sum(deviation) / len(deviation))
    
    return deviation


def adjust_graph_axes(x_coords, y_coords, min_x, max_x, min_y, max_y):
    if x_coords < min_x: min_x = x_coords
    if x_coords > max_x: max_x = x_coords    
    if y_coords < min_y: min_y = y_coords
    if y_coords > max_y: max_y = y_coords
    return min_x, max_x, min_y, max_y


def normalizer(neuron, l):
                         # skip header
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

    deviation = evaluate_growth_deviation(neuron, x_coords, y_coords)
    #comparer(neuron, deviation) # TODO solve and save negative numbers under the central axis - necessary for comparing (?)
    plt.axis([min_x, max_x+20, min_y, max_y+20]) #adjust axes
    #plt.axis([min(x_coords), max(x_coords), min(y_coords), max(y_coords)])
    plt.suptitle('Neuron {}'.format(neuron))
    plt.show()


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


if __name__ == '__main__':
    '''
    for i in range(1, 40):
        try:
            plotter(neuron = i)
        except:
            print('Number of neuron not found, trying another...')
            continue
    '''
    #plotter(neuron = 1)
    #tester()
    pass

