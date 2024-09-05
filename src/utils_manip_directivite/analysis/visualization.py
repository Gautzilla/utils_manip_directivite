import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from utils_manip_directivite.analysis.extract_data import get_dataframe

Y_LABELS = {
    'answer_plausibility': 'Plausibility',
    'answer_timbre': 'Timbre',
    'answer_angle': 'Angle',
    'answer_movement': 'Movement'
}

def plot_global_ratings(df: pd.DataFrame, question: str):
    sns.set_theme()
    f, axs = plt.subplots(nrows = 2, ncols = 4, sharex = True, sharey = True) 
    f.supylabel('Plausibility score')
    f.supxlabel('Source')
    df = df.sort_values(by = ['angle', 'distance', 'stimulus'])
    angle = ['Front','Front','Side','Side']
    distance = ['1','4','1','4']
    room = ['CLOUS','SUAPS']
    for y in range(2):
        for x in range(4):
            sns.violinplot(
                y = question,
                x = 'source',
                hue = 'stimulus',
                data = df.query(f'room == "{room[y]}" & angle == "{angle[x]}" & distance == {distance[x]}'),
                ax = axs[y][x],
                dodge = True   
            )
            axs[y][x].legend(title = 'Stimulus')
            axs[y][x].get_legend().remove()
            axs[y][x].set_title(f'{angle[x]} - {distance[x]} m')
            axs[y][x].set_xlabel('')
            axs[y][x].set_ylabel('')

    for i, ax in enumerate(axs):
        ax[-1].text(1.5, .5, ['Classroom', 'Sports\nhall'][i])
    
    """
    
    for ax in axs:
        ax.set_xlabel('Base facing angle')
        leg_handles = ax.get_legend_handles_labels()[0]
        ax.legend(leg_handles, ['Static', 'Dynamic'], title='Movement')
    plt.subplots_adjust(wspace = .1, right = .95) 
    """
    plt.subplots_adjust(left = .05, bottom = .07, right = .95, top = .95, wspace = .05, hspace = .07) 
    plt.legend(bbox_to_anchor=(.05, 0), loc="lower left",
                bbox_transform=f.transFigure, ncol=4)
    plt.show()
    #plt.savefig(r"C:\Users\User\Desktop\plausibility_ThMD.svg")

def plot_ratings_range(df: pd.DataFrame):

    df = df.sort_values(by = ['source','stimulus'])
    dependant_variables = ['answer_plausibility','answer_timbre']
    ylabels = ['Plausibility score', 'Timbre score']
    f, axs = plt.subplots(nrows = 1, ncols = 2, sharey = False)
    sns.set_theme()
    for i, ax in enumerate(axs):
        sns.boxplot(
            y = dependant_variables[i], 
            x = 'source',
            hue = 'stimulus',
            data = df,
            dodge = True,
            ax = ax,
        )
        ax.set_ylabel(ylabels[i])
        ax.get_legend().remove()
           
    plt.legend(bbox_to_anchor=(.5, .9), loc="lower center",
                bbox_transform=f.transFigure, ncol=4)
    plt.subplots_adjust(wspace = .27, right = .95)
    #plt.show()
    plt.savefig(r"C:\Users\User\Desktop\quartiles.svg")

def plot_source_stimulus(df: pd.DataFrame, question: str):
    sns.set_theme()
    df = df.sort_values(['source','stimulus'])
    sns.pointplot(
        data = df,
        y = question,
        x = 'source',
        hue = 'stimulus',
        dodge = True,
        linestyles = ['','','',''],
        markers = [(4,1,0),(4,1,45),(3,1,0),(3,1,180)],
        capsize = .05,
        err_kws = {'linewidth': 2},
    )
    plt.ylabel(f'{Y_LABELS[question]} z-score')
    plt.legend().set_title('Stimulus')
    plt.show()    
    # plt.savefig(rf"C:\Users\User\Desktop\{Y_LABELS[question]}_SxSt.svg")

def plot_angle_stimulus_distance(df: pd.DataFrame, question: str):
    sns.set_theme()
    df = df.sort_values(['source','stimulus'])
    distances = ['1', '4']
    f, axs = plt.subplots(ncols = 2, nrows = 1, sharey = True, sharex = True)
    for i, ax in enumerate(axs):
        sns.pointplot(
            data = df.query(f'distance == {distances[i]}'),
            y = question,
            x = 'angle',
            hue = 'stimulus',
            dodge = True,
            linestyles = ['','','',''],
            markers = [(4,1,0),(4,1,45),(3,1,0),(3,1,180)],
            capsize = .05,
            err_kws = {'linewidth': 2},
            ax = ax
        )
        ax.get_legend().set_title('Stimulus')
        ax.get_legend().remove()
        ax.set_xlabel('Angle')
        ax.set_ylabel(f'{Y_LABELS[question]} z-score')
        ax.set_title(f'{distances[i]} m')
    
    plt.legend(bbox_to_anchor=(.5, 1.), loc="upper center",
                bbox_transform=f.transFigure, ncol=4)
    plt.subplots_adjust(wspace = .1, right = .95, top = .85)
    # plt.show()    
    plt.savefig(rf"C:\Users\User\Desktop\{Y_LABELS[question]}_AxStxD.svg")

def plot_source_angle_stimulus(df: pd.DataFrame, question: str):
    sns.set_theme()
    df = df.sort_values(['source','stimulus'])
    angles = ['Front', 'Side']
    f, axs = plt.subplots(ncols = 2, nrows = 1, sharey = True, sharex = True)
    for i, ax in enumerate(axs):
        sns.pointplot(
            data = df.query(f'angle == "{angles[i]}"'),
            y = question,
            x = 'source',
            hue = 'stimulus',
            dodge = True,
            linestyles = ['','','',''],
            markers = [(4,1,0),(4,1,45),(3,1,0),(3,1,180)],
            capsize = .05,
            err_kws = {'linewidth': 2},
            ax = ax
        )
        ax.get_legend().set_title('Stimulus')
        ax.get_legend().remove()
        ax.set_xlabel('Source')
        ax.set_ylabel(f'{Y_LABELS[question]} good answer ratio')
        ax.set_title(f'{angles[i]}')
    
    plt.legend(bbox_to_anchor=(.5, 1.), loc="upper center",
                bbox_transform=f.transFigure, ncol=4)
    plt.subplots_adjust(wspace = .1, right = .95, top = .85)
    plt.ylim(0., 1.)
    # plt.show()    
    plt.savefig(rf"C:\Users\User\Desktop\{Y_LABELS[question]}_AxStxD.svg")

def plot_room_source_angle(df: pd.DataFrame, question: str):
    sns.set_theme()
    df = df.sort_values(['source','stimulus'])
    sources = ['Human', 'Loudspeaker']
    rooms = ['Classroom', 'Sports hall']
    angles = ['Front', 'Side']
    f, axs = plt.subplots(ncols = 2, nrows = 1, sharey = True, sharex = True)
    for i, ax in enumerate(axs):
        sns.pointplot(
            data = df.query(f'source == "{sources[i]}"'),
            y = question,
            x = 'room',
            hue = 'angle',
            dodge = True,
            linestyles = ['',''],
            markers = [(4,1,0),(4,1,45)],
            capsize = .05,
            err_kws = {'linewidth': 2},
            ax = ax
        )
        ax.get_legend().set_title('Angle')
        ax.get_legend().remove()
        ax.set_xlabel('Room')
        ax.set_xticks([0,1])
        ax.set_xticklabels(rooms)
        ax.set_ylabel(f'{Y_LABELS[question]} z-score')
        ax.set_title(f'{sources[i]}')
    
    plt.legend(bbox_to_anchor=(.5, 1.), loc="upper center",
                bbox_transform=f.transFigure, ncol=4)
    plt.subplots_adjust(wspace = .1, right = .95, top = .85)
    # plt.show()    
    plt.savefig(rf"C:\Users\User\Desktop\{Y_LABELS[question]}_RxSxA.svg")

def main() -> None:
    # Export text as text (not path) in svg exports.
    plt.rcParams['svg.fonttype'] = 'none'

    df = get_dataframe(z_score = True)
    df = df.query('user > 1').sort_values(by=['source'])

    plot_source_stimulus(df = df, question = 'answer_timbre')

if __name__ == '__main__':
    main()