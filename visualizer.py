import matplotlib.pyplot as plt
import argparse
import yielder as yld


### Plotting
def plot_single_neuron(neuron, file, pad, custom_des, transpone):
    '''Plot single chosen neuron from dataset or produce sequence of chosen neurons. '''
    min_x, max_x, min_y, max_y = float('inf'), float('-inf'), float('inf'), float('-inf') # for graph adjusting
    
    neuron, x_coords, y_coords = yld.harvest_neuron_points(neuron, file)

    if len(x_coords) < 3 and len(y_coords) < 3 and x_coords and y_coords:
        print('Neuron', neuron,'is too short for processing! Contains only', len(x_coords), 'point(s).')
        return False
    else:
        try:
            min_x, _, min_y, _ = yld.find_min_and_max_values(x_coords, y_coords, min_x, max_x, min_y, max_y)
            neuron, x_crds_norm, y_crds_norm = yld.normalize_point_data(neuron, min_x, min_y, file, transpone)
            print('Processed neuron:', neuron, 'from file:', file)
        except ValueError:
            print('Neuron not found:', neuron, 'in file:', file)
            return False   

    plt.plot(x_crds_norm, y_crds_norm)
    plt.axis([0-pad, max(x_crds_norm)+pad, 0-pad, max(y_crds_norm)+pad]) 
    plt.xlabel('microns')
    plt.ylabel('microns')

    if custom_des:
        title_ = input("Write graph title: ")
        plt.title(title_)
    else:
        plt.title('Neuron {}'.format(neuron))

    plt.show()



def plot_neurons_sequentially(from_num, to_num, file, pad, custom_des, transpone):
    '''Invoke plot_single_neuron for sequential plotting of choosen range of neurons. '''
    for neuron in range(from_num, to_num+1):
        plot_single_neuron(neuron, file, pad, custom_des, transpone)
  

def plot_range_of_neurons(*args, file, mode, pad):
    '''Plot range or group of neurons together on graph. '''
    if mode == 'range': 
        group = range(*(args[0], args[1] + 1)) # for range including last neuron
    elif mode == 'group':
        group = args
    else:
        print('Wrong usage. Check range numbers.')
        return False

    min_x, max_x, min_y, max_y = yld.iterate_for_min_and_max_values(group, file)

    for neuron in group:
        try:
            _, x_crds, y_crds = yld.normalize_point_data(neuron, min_x, min_y, file, transpone=False)
            plt.plot(x_crds, y_crds)
        except ValueError:
            continue

    plt.axis([0-pad, max_x-min_x+pad, 0-pad, max_y-min_y+pad]) # adjust axes with provided padding + data are non-normalized (max-min)
    plt.xlabel('microns')
    plt.ylabel('microns')
    title_ = input("Write graph title: ")
    plt.title(title_)
    plt.show()


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


def plot_both_groups_neurons(*args, file, file2, mode, pad, custom_des):
    '''Plotting neurons from two files for comparation. '''
    group = mode_decider(args, mode)
    
    _, axs = plt.subplots(1, 2, sharex=True, sharey=True)
    min_x, min_y = float('inf'), float('inf')
    max_x_, max_y_ = float('-inf'), float('-inf')
        
    for number, file_name in enumerate((file, file2)):
        min_x, _, min_y, _ = yld.iterate_for_min_and_max_values(group[number], file_name)
        for neuron in group[number]:
            try:
                neuron, x_crds, y_crds = yld.normalize_point_data(neuron, min_x, min_y, file_name, transpone=False)
                axs[number].plot(x_crds, y_crds)

                max_x_ = max(x_crds) if max(x_crds) > max_x_ else max_x_        # max needed from semi-normalized data
                max_y_ = max(y_crds) if max(y_crds) > max_y_ else max_y_    
            except ValueError:
                continue

        if custom_des:
            name = input('Write description for ' + str(number+1) + '. group of neurons: ')
            axs[number].set_title(name)
        else:
            axs[number].set_title(file_name)

        if number == 0: axs[number].set(ylabel = 'microns', xlabel = 'microns') # exclude y label for second graph
        else:           axs[number].set(xlabel = 'microns')

        plt.sca(axs[0])
        min_x, min_y = float('inf'), float('inf')       # reinitialize min values for second group

    plt.axis([0-pad, max_x_+pad, 0-pad, max_y_+pad])    # adjust axes with provided padding
    plt.show()


# Control
def cmd_control():
    '''Command line user interface. '''
    parser = argparse.ArgumentParser(description='Providing arguments for selective neuron graph plotting.')
    parser.add_argument('-f', '--filename', 
                        help='Csv source of data. Structure: second column neuron number, third and fourth x,y coordinates.', 
                        type=str, required=True, dest='filename')
    parser.add_argument('-f2', '--filename2', 
                        help='Second csv source of data. Structure: second column neuron number, third and fourth x,y coordinates.', 
                        type=str, required=False, dest='filename2')
    parser.add_argument('-m', '--mode', 
                        help='Options: [ single | burst | range | group ]', 
                        type=str, required=True, dest='mode')
                        ####                    
    parser.add_argument('-n', '--neuron_first', 
                        help='Neurons from first file. Modes: [ single (int) | burst (from int, to int) | range (from int, to int) | group (arbitrary int(s)) ]', 
                        nargs='*', type=int, required=True, dest='neuron_first')
    parser.add_argument('-n2', '--neuron_other', 
                        help='Neurons from second file. Modes: [ range (from int, to int) | group (arbitrary int(s)) ]', 
                        nargs='*', type=int, dest='neuron_second')
                        ####
    parser.add_argument('-t', '--transpone', 
                        help='Transpone neuron for burst or single mode from / to \\ if needed.', 
                        type=bool, required=False, dest='transpone', default=False)
    parser.add_argument('-p', '--padding', 
                        help='Adjusting space around neuron(s) in graph. Default=20px', 
                        type=int, required=False, dest='padding', default=20)
    parser.add_argument('-d', '--description', 
                        help='Choosing custom description.', 
                        type=bool, required=False, dest='description', default=False)

    return parser


def execute_commands():
    '''Executing cmd user input. '''

    parser = cmd_control()
    args = parser.parse_args()

    try:
        if args.filename and args.filename2:
            args_ = (args.neuron_first, ) + (args.neuron_second, )
            plot_both_groups_neurons(*args_, file=args.filename, file2=args.filename2, mode=args.mode, pad=args.padding, custom_des=args.description)

        else:
            if args.mode == 'single':
                plot_single_neuron(*args.neuron_first, args.filename, args.padding, args.description, args.transpone)
            elif args.mode == 'burst' and len(args.neuron_first) == 2 and args.neuron_first[0] < args.neuron_first[1]:
                plot_neurons_sequentially(*args.neuron_first, args.filename, args.padding, args.description, args.transpone)
            elif args.mode == 'range' and len(args.neuron_first) == 2 and args.neuron_first[0] < args.neuron_first[1]:
                plot_range_of_neurons(*args.neuron_first, file=args.filename, mode=args.mode, pad=args.padding) # decription always
            elif args.mode == 'group':
                args_ = tuple(args.neuron_first)
                plot_range_of_neurons(*args_, file=args.filename, mode=args.mode, pad=args.padding) # decription always
            else:
                print('Wrong usage. Check command line arguments.')
    except TypeError:
        print('Wrong usage. Check command line arguments.')


if __name__ == "__main__":
    execute_commands()