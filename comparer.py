import matplotlib.pyplot as plt
from math import sqrt, sin, acos, asin, cos
import yielder as yld
import visualizer as vis

###Calculating
def check_and_modify_data_for_comparation(neuron, file):
    '''Checking neuron presence, length, orientation (transpone if needed for normalization), 
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

        print('Processed neuron:', neuron, 'from file:', file)
    except IndexError:
        print('Neuron not found:', neuron, 'in file:', file)
        return False
    
    return (neuron, x_coords, y_coords)


def evaluate_growth_deviation(neuron, file):
    '''Counts proximity of neuron point from central axis of neuron 
    (connecting lowest and highest point of neuron). 
    Differentiates between below/above (+/-)'''
    comparation_data = check_and_modify_data_for_comparation(neuron, file)
    
    if comparation_data:
        neuron, x_coords, y_coords = comparation_data
    else:
        return False, False

    # deviation calculation
    neuron_centr_ax_length  = sqrt((x_coords[0] - x_coords[-1])**2 + (y_coords[0] - y_coords[-1])**2) # connecting most distant points of neuron
    deviation = list()                                # prepared instance of list for all deviations (distance of point from neuron central axis)

    # calculating of definition below/above
    height_of_triangle      = y_coords[0] if y_coords[0] > y_coords[-1] else y_coords[-1] # choosong from which end of neuron position (+/-) of point will be counted (avoiding case y_coords[0] == 0)
    angle_a                 = asin(height_of_triangle/neuron_centr_ax_length)      # angle between x axis and central axis
    side_along_central      = x_coords[0]/cos(angle_a)                             # side of triangle passing through or be identical with central axis          
    side_along_y            = side_along_central * sin(angle_a)                    # side of triangle passing through or be identical with y axis   

    
    for x, y in zip(x_coords, y_coords):
        bottom__point_len = sqrt((x - x_coords[-1])**2 + (y - y_coords[-1])**2)  # distance of bottom point of neuron and calculated point
        top__point_len = sqrt((x - x_coords[0])**2 + (y - y_coords[0])**2)       # distance of top point of neuron and calculated point
        try:
            # deviation calculation for each point
            angle_c = acos((bottom__point_len**2 + top__point_len**2 - neuron_centr_ax_length**2)/(2*bottom__point_len*top__point_len))   # angle for area calculation
            area = (bottom__point_len*top__point_len*sin(angle_c))/2        # area of triangle x,y point - bottom point - top point of neuron
            height = 2*area/neuron_centr_ax_length                          # height of triangle represents deviation from central axis

            # calculating of definition below/above for each point
            y_position = side_along_y - (y_coords[0] - y)                   # calculating of subtraction of each y_coordinate with first y point and subtract from side of triangle passing through or be identical with y axis   
            side_along_central_for_new_base = y_position / sin(angle_a)     # subtratcting previous value from 
            base_on_y_level = sqrt((side_along_central_for_new_base**2) - (y_position**2)) # calculating base of new triangle: 

            if x < base_on_y_level: deviation.append(height) # if base (distance from y axis to central axis) is higher than x position (distance form y axis to point) of point, point is "above" - positive float
            else:                   deviation.append(-height)

        except ZeroDivisionError: # if point is first or last (division err naturally)
            deviation.append(0)
        except ValueError: # if point is on central axis
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
    
    plt.boxplot(groups_neuron_heights)
    plt.axhline(0, color='black', lw=0.5)
    plt.ylabel('microns')

    custom_description(plt, file, file2, custom_des)

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

    try:
        if args.filename and args.filename2 and args.option == 'separated':
            args_ = (args.neuron_first, ) + (args.neuron_second, )
            print(args_)
            create_boxplots_from_separate_neurons(*args_, file=args.filename, file2=args.filename2, mode=args.mode, custom_des=args.description)
        elif args.filename and args.filename2 and args.option == 'pooled':
            args_ = (args.neuron_first, ) + (args.neuron_second, )
            create_boxplots_from_pooled_heights_of_neuron_group(*args_, file=args.filename, file2=args.filename2, mode=args.mode, custom_des=args.description)
        elif args.filename and args.filename2 and args.option == 'averaged':
            args_ = (args.neuron_first, ) + (args.neuron_second, )
            create_boxplots_from_neuron_height_averages(*args_, file=args.filename, file2=args.filename2, mode=args.mode, custom_des=args.description)
        else:
            print('Wrong usage. Check command line arguments.')
    except TypeError:
        print('Wrong usage. Check command line arguments.')


if __name__ == '__main__':
    execute_commands()
