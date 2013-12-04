import matplotlib
from matplotlib import pyplot as plt
from matplotlib import patches as pch
import numpy as np
import os

'''
Program:
1. Get student activity data: This is the 'GetStudentActivity' function. Edit it so it suits the source of your data. The function explains the format in which to put the data.
2. Call any of the 2 plot generating functions. One is for individual plots, the other is for aggregate plots

Settings have been grouped below, to allow easy editing of output path and various plot behaviors.
'''


### Settings ###
################
output_path = "C:/output_plots/" # Where should the outputs be stored? Must keep the trailing slash.

color_map = {
    'video_first_visit': (0,0,1), # Pure blue
    'video_revisit_another': (0.3,0.3,1), # lighter blue
    'video_revisit_same': (0.7,0.7,1), # lightest blue
    'assignment_first_visit': (0,1,0), # Pure green
    'assignment_revisit': (0.5,1,0.5), # lighter green
    'assignment_submission': (0,0.5,0), # Dark green
    'quiz_first_visit': (1,0,1), # Pure magenta
    'quiz_revisit': (1,0.5,1), # Lighter magenta
    'quiz_submission': (0.6,0,0.6), # Dark magenta
    'forum_read': (0.8,0.8,0.3), # Brownish-yellow
    'forum_post': (1,1,0), # Pure yellow
    'new_session': (0,0,0), # Black
}

new_session_threshold = 3*60 # If the difference between two successive events is greater than this number of minutes, insert a new session delimiter

min_row_size = 20; # We try to prettify the plot by making it approximately square. However, we need to set minimum and maximum row sizes
max_row_size = 100;

matplotlib.rcParams['font.size'] = 8

### End Settings

def GetStudentActivity():
    '''
    This function must return a dictionary (student_id: student_activity_array)
    student_activity_array must be a list if dictionaries. Each dictionary is a single activity point (event), with the following fields:
        - ts: The timestamp of the event
        - type: The event type
    '''
    student_activity = {
        1: [
            {'ts': 1350861176, 'type': 'video_first_visit'},
            {'ts': 1350862176, 'type': 'video_revisit_same'},
            {'ts': 1350871176, 'type': 'video_first_visit'},
            {'ts': 1350872176, 'type': 'video_revisit_another'},
            {'ts': 1350873176, 'type': 'video_revisit_same'},
            {'ts': 1350874176, 'type': 'assignment_first_visit'},
            {'ts': 1350875176, 'type': 'assignment_revisit'},
            {'ts': 1350881176, 'type': 'forum_read'},
            {'ts': 1350881276, 'type': 'forum_post'},
            {'ts': 1350882676, 'type': 'video_first_visit'},
        ],
    }
    
    student_activity[2] = []
    for i in range(100):
        offset = 100000*i
        for a in student_activity[1]:
            student_activity[2].append({'ts': a['ts']+offset, 'type': a['type']})
    
    return student_activity

def GenerateStudentActivityPlots(student_activity):
    if not os.path.exists(output_path): os.makedirs(output_path)
    individual_student_plots_path = output_path + "individual/"
    if not os.path.exists(individual_student_plots_path): os.makedirs(individual_student_plots_path)

    for sid in student_activity.keys():
        activity_ = sorted(student_activity[sid], key = lambda x: x['ts'])
        activity = [] # This will have all items in activity_ plus session_start delimiters
        last_ts = 0
        for a in activity_:
            if 'ts' not in a.keys() or 'type' not in a.keys():
                raise Exception("Each student activity element must contain a 'ts' field and a 'type' field.")
            if a['type'] not in color_map.keys():
                raise Exception("Activity type '{}' does not have an entry in the color map.".format(a['type']))    
            
            if a['ts'] - last_ts > 60*new_session_threshold: # Add a 'new_session' delimiter if necessary    
                activity.append({'ts': a['ts'], 'type': 'new_session'})
            
            activity.append(a)
            last_ts = a['ts']
        
        row_size = np.ceil(np.sqrt(5*len(activity)))
        if row_size < min_row_size: row_size = min_row_size
        if row_size > max_row_size: row_size = max_row_size
        n_rows = np.ceil(1.0*len(activity)/row_size)
        
        fig_width = 3.75 + (1.0/16)*row_size
        fig_height = 3.75 + (5.0/16)*n_rows
        
        plt.figure(figsize=(fig_width, fig_height))
        plt.hold(True)
        
        ai = 0
        for a in activity:
            height = 0.95 if a['type'] == 'new_session' else 0.85
            width = 1
            x = ai%row_size
            y = -int(ai/row_size)-1
            plt.gca().add_patch( pch.Rectangle([x,y], width, height, color = color_map[a['type']]) )
            ai += 1
        
        plt.title("Student {}'s Activity".format(sid))
        plt.axis([0,row_size, -n_rows, 0])
        plt.axis('off')
        plt.savefig(individual_student_plots_path + "{}.png".format(sid), box_inches='tight')
        plt.close()
    
def GenerateAggregatedActivityPlots(student_activity):
    if not os.path.exists(output_path): os.makedirs(output_path)
    aggregated_plots_path = output_path + "aggregated/"
    if not os.path.exists(aggregated_plots_path): os.makedirs(aggregated_plots_path)
    
    aggregates = {2: {}, 3: {}, 4: {}}
    
    for sid in student_activity.keys():
        activity = student_activity[sid]
        for n in aggregates.keys():
            if len(activity) >= n:
                for i in range(len(activity)-n):
                    key = "#".join([activity[ai]['type'] for ai in range(i,i+n)])
                    if key not in aggregates[n].keys(): aggregates[n][key] = 0
                    aggregates[n][key] += 1
    
    for n in aggregates.keys():
        
        if len(aggregates[n].keys()) <= 2:
            subplot_dims = [1,2]
            figsize=(5,2.5)
        elif len(aggregates[n].keys()) <= 4:
            subplot_dims = [2,2]
            figsize=(5,4)
        elif len(aggregates[n].keys()) <= 6:
            subplot_dims = [2,3]
            figsize=(7,4)
        elif len(aggregates[n].keys()) <= 9:
            subplot_dims = [3,3]
            figsize=(7,5)
        elif len(aggregates[n].keys()) <= 12:
            subplot_dims = [3,4]
            figsize=(8,5)
        elif len(aggregates[n].keys()) <= 15:
            subplot_dims = [3,5]
            figsize=(9,5)
        elif len(aggregates[n].keys()) == 16:
            subplot_dims = [4,4]
            figsize=(8,6)
        else:
            subplot_dims = [4,5]
            figsize=(9,6)
        
        total_num_tuples = sum(aggregates[n].values())
        plt.figure(figsize = figsize)
        
        selected_keys = sorted(aggregates[n].keys(), key = lambda k: aggregates[n][k], reverse=True)[:20]
        for index in range(len(selected_keys)):
            k = selected_keys[index]
            plt.subplot(subplot_dims[0], subplot_dims[1], index+1)
            
            plt.hold(True)
            plt.title("{}: {}%".format(index+1, 0.01*int(10000*aggregates[n][k]/total_num_tuples)))
            events = k.split("#")
            for ei in range(len(events)):
                plt.gca().add_patch( pch.Rectangle([ei, 0], 1, 1, color = color_map[events[ei]]) )
                plt.text(5, 0.9 - 0.15*ei, events[ei], size=6)
            plt.axis([0,15,0,1])
            plt.axis('off')
            
        plt.savefig(aggregated_plots_path + "{}.png".format(n))
        plt.close()
        
if __name__ == "__main__":
    student_activity = GetStudentActivity()
    GenerateStudentActivityPlots(student_activity)
    GenerateAggregatedActivityPlots(student_activity)