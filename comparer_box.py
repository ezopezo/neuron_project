import matplotlib.pyplot as plt
from math import sqrt, sin, radians, acos, degrees
import yielder as yld


def evaluate_growth_deviation(neuron):
    neuron, x_coords, y_coords = yld.harvest_neuron_points(neuron, file='c2pos5_points.csv')
    
    length_x_axis = x_coords[0]
    length_y_axis = y_coords[0]

    neuron_centr_ax_length = sqrt(length_x_axis**2 + length_y_axis**2) 
    angle_b = acos((neuron_centr_ax_length**2 + length_y_axis**2 - length_x_axis**2) / (2*neuron_centr_ax_length*length_y_axis))
    angle_a = radians(90) - angle_b
    
    deviation = list()

    for x, y in zip(x_coords, y_coords):
        height_triangle_x_ax = y*sin(angle_b)/sin(angle_a) 
        height_triangle_y_ax = x*sin(angle_a)/sin(angle_b)

        a_side = abs(height_triangle_x_ax - x)
        b_side = abs(height_triangle_y_ax - y)
        c_side = sqrt(a_side**2 + b_side**2)
        triangle_area = 0.5 * a_side * c_side * sin(angle_a)
        
        try:                                  
            height = 2*triangle_area/c_side
            if height_triangle_y_ax < y:
                deviation.append(round(height, 10))
            else:
                deviation.append(round(-height, 10))
        except ZeroDivisionError:
            deviation.append(0)

    return deviation


### Data collector
def collector(): # can be fused with collector test into one generator called with arguments of scaned data and tested data
    for i in range(1, 21):
        try:
            deviation = evaluate_growth_deviation(i)
            yield i , deviation
        except IndexError:
            print('value err')
            continue


def collector_test(): # testing collector for spliting file for compare test
    for i in range(20, 40):
        try:
            deviation = evaluate_growth_deviation(i)
            yield i , deviation
        except IndexError:
            print('value err')
            continue


### Plotting
def create_boxplots_from_pooled_heights_of_neuron_group():
    first_group_neuron_heights = list() ### pool of all heights form neuron dataset
    other_group_neuron_heights = list()

    for _ , neuron in collector():
        for height in neuron:
            first_group_neuron_heights.append(abs(height))

    for _ , neuron_other in collector_test():
        for height_other in neuron_other:
            other_group_neuron_heights.append(abs(height_other))

    data = [first_group_neuron_heights, other_group_neuron_heights]

    plt.boxplot(data) 
    plt.ylabel('microns')
    plt.xticks([1, 2], ['first', 'second'])
    plt.show() 



def create_boxplots_from_separate_neurons():
    first_set_of_neurons = list()
    other_set_of_neurons = list()
    num_ = list(' ')
    num_other = list(' ')

    for number, neuron in collector():
        first_set_of_neurons.append(neuron)
        num_.append(number)
    
    for number_other, neuron_other in collector_test():
        other_set_of_neurons.append(neuron_other)
        num_other.append(number_other)
    
    
    _, axs = plt.subplots(1, 2, sharey=True)
    plt.ylabel('microns')
    

    axs[0].boxplot(first_set_of_neurons)
    axs[0].set_title('first_group')
    axs[0].set(ylabel = 'microns', xlabel = 'number of neuron')
    axs[0].axhline(0, color='black', lw=0.5)
    plt.sca(axs[0])
    plt.xticks(range(len(num_)),  num_)

    axs[1].boxplot(other_set_of_neurons)
    axs[1].set_title('other_group')
    axs[1].set(xlabel = 'number of neuron')
    axs[1].axhline(0, color='black', lw=0.5)
    plt.sca(axs[1])
    plt.xticks(range(len(num_other)),  num_other)
    
    plt.show()


def create_boxplots_from_neuron_height_averages():
    average_height_first = list()
    average_height_other = list()
    for _, i in collector():
        average_height_first.append(sum(i)/len(i))

    for _, j in collector_test():
        average_height_other.append(sum(j)/len(j))
    
    plt.boxplot([average_height_first, average_height_other])
    plt.ylabel('microns')
    plt.axhline(0, color='black', lw=0.5)
    plt.title('...')
    plt.show() 


if __name__ == '__main__':
    #create_boxplots_from_pooled_heights_of_neuron_group()
    #create_boxplots_from_separate_neurons()
    #create_boxplots_from_neuron_height_averages()

