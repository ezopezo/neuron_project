import matplotlib.pyplot as plt
from math import sqrt, sin, radians, acos, degrees
import yielder as yld
import visualizer as vis

###Calculating
def check_and_modify_data_for_comparation(neuron, file):
    '''Checking neuron presence, length, orientation (transpone if needed for noramlization), 
    normalize and produce data for calculation of deviations. '''
    try:
        neuron, x_coords, y_coords = yld.harvest_neuron_points(neuron, file)
        if len(x_coords) < 3 and len(y_coords) < 3 and x_coords and y_coords:
            print('Neuron', neuron,'is too short for processing! Contains only', len(x_coords), 'point(s).')
            return False
        else:
            transpone = False # orientation /
            if not(x_coords[0] - x_coords[-1] > 0 and y_coords[0] - y_coords[-1] > 0): 
                transpone = True # orientation \ - sending data for transponation of neuron to / orientation


        neuron, x_coords, y_coords = yld.normalize_point_data(neuron, min(x_coords), min(y_coords), file, transpone)

        length_x_axis = x_coords[0] if x_coords[0] > x_coords[-1] else x_coords[-1] # in case of different neuron orientation (see mock revrev)
        length_y_axis = y_coords[0] if y_coords[0] > y_coords[-1] else y_coords[-1]

        print('Processed neuron:', neuron, 'from file:', file)
    except IndexError:
        print('Neuron not found:', neuron, 'in file:', file)
        return False
    
    return (neuron, length_x_axis, length_y_axis, x_coords, y_coords)


def evaluate_growth_deviation(neuron, file):
    '''Counts proximity of neuron point from central axis of neuron 
    (connecting lowest and highest point of neuron). 
    Differentiates between below/above (+/-)'''
    comparation_data = check_and_modify_data_for_comparation(neuron, file)
    
    if comparation_data:
        neuron, length_x_axis, length_y_axis, x_coords, y_coords = comparation_data
    else:
        return False, False

    neuron_centr_ax_length = sqrt(length_x_axis**2 + length_y_axis**2) # connecting most distant points of neuron
    # angles of triangle x axis / y axis / neuron central axis 
    angle_b = acos((neuron_centr_ax_length**2 + length_y_axis**2 - length_x_axis**2) / (2*neuron_centr_ax_length*length_y_axis))
    angle_a = radians(90) - angle_b # subtracted from x axis / y axis right angle
    deviation = list() # prepared instance of list for all deviations (distance of point from neuron central axis)
    
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
                deviation.append(round(height, 6)) # above neuron central axis - positive
            else:
                deviation.append(round(-height, 6)) # below neuron central axis - negative
        except ZeroDivisionError: # if c side is 0 deviation == 0 (point is on central axis or first/last point)
            deviation.append(0)

    return neuron, deviation


### Plotting
## Helper funcs
def custom_description(plt, file, file2, custom_des):
    '''Custom description for pooled and averaged graphs.'''
    if custom_des:
        first_group_description = input('Write description for first group: ')
        second_group_description = input('Write description for second group: ')
        title_ = input("Write graph title: ")
        plt.title(title_)
        plt.xticks([1, 2], [first_group_description, second_group_description])
    elif not custom_des and file != file2:
        plt.xticks([1, 2], [file, file2])
    else:
        plt.xticks([1, 2], ['First group', 'Second group'])

    return plt 


## Plotting data
def create_boxplots_from_separate_neurons(*args, file, file2, mode, custom_des):
    '''Plot boxplots representing deviations of each point of neuron 
    from central axis (connecting lowest and highest point of neuron). '''
    group = vis.mode_decider(args, mode)

    package_of_neurons = list()
    neuron_xticks = [' ']                # empty string for first xtick
    _, axs = plt.subplots(1, 2, sharey=True)

    for number, file_name in enumerate((file, file2)):
        for neuron in group[number]:
            neuron, deviation = evaluate_growth_deviation(neuron, file_name)
            if neuron and deviation:
                package_of_neurons.append(deviation)
                neuron_xticks.append(neuron)
            else:
                continue

        axs[number].boxplot(package_of_neurons)
        axs[number].set(ylabel = 'microns', xlabel = 'number of neuron')
        axs[number].axhline(0, color='black', lw=0.5)
        if custom_des:
            descr = input(f'Write description for group {number+1}: ')
            axs[number].set_title(descr)
        else:
            axs[number].set_title(file_name)
        plt.sca(axs[number])
        plt.xticks(range(len(neuron_xticks)), neuron_xticks)

        package_of_neurons.clear() # clearing for next iteration
        neuron_xticks = [' ']

    plt.show()


def create_boxplots_from_pooled_heights_of_neuron_group(*args, file, file2, mode, custom_des):
    '''Plot boxplots from all deviations from central axis 
    of each point from chosen group of neurons. '''
    group = vis.mode_decider(args, mode)

    groups_neuron_heights = list(), list()

    for number, file_name in enumerate((file, file2)):
        for neuron in group[number]:
            neuron, deviation = evaluate_growth_deviation(neuron, file_name)
            if neuron and deviation:
                for single_height in deviation:
                    groups_neuron_heights[number].append(single_height)
            else:
                continue

    plt.boxplot(groups_neuron_heights)
    plt.axhline(0, color='black', lw=0.5)
    plt.ylabel('microns')

    custom_description(plt, file, file2, custom_des)

    plt.show() 


def create_boxplots_from_neuron_height_averages(*args, file, file2, mode, custom_des):
    '''Plot boxplots deviations average calculated from each neuron 
    from chosen group of neurons. '''
    group = vis.mode_decider(args, mode)

    groups_neuron_heights = list(), list()

    for number, file_name in enumerate((file, file2)):
        for neuron in group[number]:
            neuron, deviation = evaluate_growth_deviation(neuron, file_name)
            if neuron and deviation:
                groups_neuron_heights[number].append(sum(deviation)/len(deviation))
            else:
                continue

    custom_description(plt, file, file2, custom_des)
    
    plt.boxplot(groups_neuron_heights)
    plt.ylabel('microns')
    plt.axhline(0, color='black', lw=0.5)
    plt.show() 


###Control
def cmd_control():
    '''Command line user interface. Inherited from visualizer and extended for comparer. '''
    parser = vis.cmd_control()

    parser.add_argument('-o', '--option', 
                        help='Options: [ separate | pooled | averaged ]', 
                        type=str, required=True, dest='option')

    args = parser.parse_args()

    return args


def execute_commands():
    '''Executing cmd user input. '''
    args = cmd_control()

    #try:
    if args.filename and args.filename2 and args.option == 'separated':
        args_ = (args.neuron_first, ) + (args.neuron_second, )
        create_boxplots_from_separate_neurons(*args_, file=args.filename, file2=args.filename2, mode=args.mode, custom_des=args.description)
    elif args.filename and args.filename2 and args.option == 'pooled':
        args_ = (args.neuron_first, ) + (args.neuron_second, )
        create_boxplots_from_pooled_heights_of_neuron_group(*args_, file=args.filename, file2=args.filename2, mode=args.mode, custom_des=args.description)
    elif args.filename and args.filename2 and args.option == 'averaged':
        args_ = (args.neuron_first, ) + (args.neuron_second, )
        create_boxplots_from_neuron_height_averages(*args_, file=args.filename, file2=args.filename2, mode=args.mode, custom_des=args.description)
    else:
        print('Wrong usage. Check command line arguments.')
    #except TypeError:
    #    print('Wrong usage. Check command line arguments.')


if __name__ == '__main__':
    execute_commands()
    pass