import matplotlib.pyplot as plt
from math import sqrt, sin, radians, acos, degrees
import yielder as yld
import visualizer as vis


def evaluate_growth_deviation(neuron, file):
    '''Counts proximity of neuron point from central axis of neuron. 
    Differentiates between below/above (+/-)'''

    try:
        neuron, x_coords, y_coords = yld.harvest_neuron_points(neuron, file)
        neuron, x_coords, y_coords = yld.normalize_point_data(neuron, min(x_coords), min(y_coords), file)
        length_x_axis = x_coords[0]
        length_y_axis = y_coords[0]
        print('Processed neuron:', neuron, 'from file:', file)
    except ValueError:
        print('Neuron not found:', neuron, 'in file:', file)
        return False, False 

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
                deviation.append(round(height, 6))
            else:
                deviation.append(round(-height, 6))
        except ZeroDivisionError:
            deviation.append(0)

    return neuron, deviation


def mode_decider(args, mode):
    '''Process neuron argumets based on mode. '''
    if mode == 'range' and len(args[0]) == 2 and len(args[1]) == 2:
        first_source = (args[0][0], tuple(args[0])[1] + 1) # for range including last neuron
        second_source = (args[1][0], tuple(args[1])[1] + 1)
        group = range(*first_source), range(*second_source)
    elif mode == 'group':
        group = args
    else:
        print('Wrong usage. Check range numbers.')
        return False
    
    return group


### Plotting
def create_boxplots_from_separate_neurons(*args, file, file2, mode, custom_des):
    group = mode_decider(args, mode)

    package_of_neurons = list()
    neuron_ticks = [' ']                # empty string for first xtick
    _, axs = plt.subplots(1, 2, sharey=True)

    for number, file_name in enumerate((file, file2)):
        for neuron in group[number]:
            neuron, deviation = evaluate_growth_deviation(neuron, file_name)
            if neuron and deviation:
                package_of_neurons.append(deviation)
                neuron_ticks.append(neuron)
            else:
                continue

        axs[number].boxplot(package_of_neurons)
        axs[number].set_title(file_name)
        axs[number].set(ylabel = 'microns', xlabel = 'number of neuron')
        axs[number].axhline(0, color='black', lw=0.5)
        plt.sca(axs[number])
        plt.xticks(range(len(neuron_ticks)), neuron_ticks)

        package_of_neurons.clear() # clearing for next iteration
        neuron_ticks = [' ']

    plt.show()


def create_boxplots_from_pooled_heights_of_neuron_group(*args, file, file2, mode, custom_des):
    group = mode_decider(args, mode)

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

    if custom_des:
        first_group_description = input('Write description for first group: ')
        second_group_description = input('Write description for first group: ')
        plt.xticks([1, 2], [first_group_description, second_group_description])
    elif not custom_des and file != file2:
        plt.xticks([1, 2], [file, file2])
    else:
        plt.xticks([1, 2], ['First group', 'Second group'])

    plt.show() 


def create_boxplots_from_neuron_height_averages(*args, file, file2, mode, custom_des):
    group = mode_decider(args, mode)

    groups_neuron_heights = list(), list()

    for number, file_name in enumerate((file, file2)):
        for neuron in group[number]:
            neuron, deviation = evaluate_growth_deviation(neuron, file_name)
            if neuron and deviation:
                groups_neuron_heights[number].append(sum(deviation)/len(deviation))
            else:
                continue
    
    plt.boxplot(groups_neuron_heights)
    plt.ylabel('microns')
    plt.axhline(0, color='black', lw=0.5)
    plt.title('...')
    plt.show() 


def cmd_control():
    '''Command line user interface. Inherited from visualizer and extended for comparer. '''
    parser = vis.cmd_control()

    parser.add_argument('-o', '--option', 
                        help='Options: [ separate | pooled | averaged ]', 
                        type=str, required=True, dest='option')
    parser.add_argument('-t', '--title', 
                        help='Custom title', 
                        type=bool, required=False, dest='title', default=False)

    args = parser.parse_args()

    return args


def execute_commands():
    '''Executing cmd user input. '''
    args = cmd_control()

    try:
        if args.filename and args.filename2 and args.option == 'separate':
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
    except TypeError:
        print('Wrong usage. Check command line arguments.')


if __name__ == '__main__':
    execute_commands()