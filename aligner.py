import csv
import matplotlib.pyplot as plt
from math import sqrt, sin, radians, acos, degrees
from copy import deepcopy
from statistics import median, mean
import numpy
import visualizer as vs

# in progress

def detect_outliers_in_deviation(bins): # performing poorly on bins also on deviations
    outliers = list()
    threshold = 3
    mean_1 = numpy.mean(bins)
    std_1 = numpy.std(bins)
    
    for y in bins:
        z_score = (y - mean_1) / std_1 
        if numpy.abs(z_score) > threshold:
            outliers.append(y)
    #print(outliers)

 
def create_bins(neuron, deviation_seq): # balance of data in bins?
    del deviation_seq[0] # removing zeros form beg. and end - not needed for averaging bins
    del deviation_seq[-1]

    identificator = [neuron]           # index 0 - neuron number

    splitted = numpy.array_split(numpy.array(deviation_seq), 30) # hard coded split TODO mybe initially iterate both files to find lowest num of points and save it to JSON or TXT for overiding hardcoded value and erase it after calculations done?
    bins = [sum(i) / len(i) for i in splitted]                   # TODO excluding neurons which are represented less than (outlier value) points, for avoiding biased results


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

   
    #detect_outliers_in_deviation(deviation)
     #processing to create bins - every neuron divided to equal parts (one bin - average of certain subsequence of heights) for later cmopating - separate function
    identified_bins = create_bins(neuron, deviation)
    #print(identified_bins[4]) # outliers
    return deviation


def plotter(neuron):
    normalized_data = vs.normalize_point_data(neuron, file = 'c2pos5_points.csv', mode='single')
    identified_bins = evaluate_growth_deviation(normalized_data[0], normalized_data[1], normalized_data[2])
    return identified_bins


################# calculation of simmilarity
def collector(): # can be fused with collector test into one generator called with arguments of scaned data and tested data
    for i in range(1, 20):
        try:
            identified_bins = plotter(neuron = i)

            yield identified_bins
        except ValueError: # catching all for now
            continue


def collector_test(): # testing collector for spliting file for compare test
    for j in range(20, 40):
        try:
            identified_bins = plotter(neuron = j)
            yield identified_bins
        except ValueError:
            continue

def create_boxplots_from_collections():
    first_collection = list()
    second_collection = list()

    for i in collector():
        for k in i[3]:
            first_collection.append(abs(k))

    for j in collector_test():
        for l in j[3]:
            second_collection.append(abs(l))

    data = [first_collection, second_collection]

    plt.boxplot(data) 
    plt.show() 

#create_boxplots_from_collections()

def create_boxplots_from_separate_neurons():
    first_set_of_neurons = list()
    other_set_of_neurons = list()

    for i in collector():
        first_set_of_neurons.append(i)
    
    for j in collector_test():
        other_set_of_neurons.append(j)

    fig, axs = plt.subplots(1, 2)


    axs[0].boxplot(first_set_of_neurons)
    axs[0].set_title('first_group')

    axs[1].boxplot(other_set_of_neurons)
    axs[1].set_title('other_group')

    plt.show()

create_boxplots_from_separate_neurons()


########## comparation each - comformity, more sets.
biggest_point_distance = 0

def calculate_each_bin_distance(packed_bins, signature, orientation):
    global biggest_point_distance
    distance_seq = list()

    #distance_seq.append(signature)             # signature pair of neurons for direct [(first_neuron_num, second_neuron_num, -1, max)]
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
    distance_seq.insert(0, tuple((signature, orientation)))
    return distance_seq


def iterate_neuron_bin_sets():
    distance_seq_collection = list()
    distance_seq_reverse_collection = list()        # instance for reversing values of heights for mirror comparation

    for j in collector():
        for k in collector_test():
            signature = tuple((j[0], k[0]))             # signature pair of neurons for direct [(first_neuron_num, second_neuron_num)]
            reversed_k_neuron = [-i for i in k[3]]      # for mirror comparing

            distance_seq_collection.append(calculate_each_bin_distance(zip(j[3], k[3]), signature, orientation=1))                     # direct comparation
            distance_seq_reverse_collection.append(calculate_each_bin_distance(zip(j[3], reversed_k_neuron), signature, orientation=-1))  # mirror comparation
    
    return zip(distance_seq_collection, distance_seq_reverse_collection)


def filtering_direct__mirror_comparisons():
    packed_collections = iterate_neuron_bin_sets()

    for direct, mirror in packed_collections:
        if sum(direct[1:]) > sum(mirror[1:]):
            yield mirror
        else:
            yield direct


def calculate_percentage_of_simmilarity_bins(): # [(1, 1, -1), 98.2, 84.6,...] # 
    distance_percentage = list()
    for distance_collection_absolute in filtering_direct__mirror_comparisons():
        for index, distance in enumerate(distance_collection_absolute):
            if index == 0:
                distance_percentage.append(distance) # tuple with neuron identificators
            else:
                distance_percentage.append(100 - ((100*distance) / biggest_point_distance))

        yield distance_percentage
        distance_percentage.clear()


def pooled_similarity_of_neuron_with_other_group(percentage_of_sim):
    for signature, percentage in percentage_of_sim.items():
        #print(signature, percentage)
        pass


def calculate_percentage_of_simmilarity(): # [(1, 1, -1), 76.88] 
    percentage_of_sim = {i[0]: sum(i[1:]) / len(i[1:]) for i in calculate_percentage_of_simmilarity_bins()}         # {((first neuron, last neuron), orientation), average bins simmilarity}
    pooled_similarity_of_neuron_with_other_group(percentage_of_sim)
    sorted_similarity = {k: v for k, v in sorted(percentage_of_sim.items(), key=lambda item: item[1], reverse=True)} # sorted
    return sorted_similarity


def division_neurons_to_quartils():
    sorted_similarity = calculate_percentage_of_simmilarity()
    most_similar = max(sorted_similarity.values())
    less_similar = min(sorted_similarity.values())
    range_of_avg_percentages = most_similar - less_similar

    for signature, percentage in sorted_similarity.items():
        #if percentage < (range_of_avg_percentages *0.25) + less_similar:
        #print(signature, percentage)
        pass


    #print(most_similar, less_similar)


### TODO most oultliers - list of neurons with most outliers from their path # done thinking about outliers per 10 points

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
    #collector()         # first dataset
    #collector_test()    # second dataset

    #create_boxplots_from_collections()

    #division_neurons_to_quartils()

    def diagnostic():
        for i in range(1, 40):
            try:
                identified_bins = plotter(neuron = i)
                print('Passed: ', i)
            except ZeroDivisionError: # TODO  track zero division error
                print('Zero div error: ', i)
                continue
            except ValueError:
                print('Not found', i)
                continue

    #diagnostic()

    #plotter(neuron = 5)
    #plotter(neuron = 38)
    #tester()
    pass


