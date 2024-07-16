import pandas as pd
from scipy.spatial.transform import Rotation
import matplotlib.pyplot as plt
import scipy.signal
import os

(_yaw, _pitch, _roll) = ('Yaw', 'Pitch', 'Roll')
HEADROTS_FOLDER = r'C:\Users\labsticc\Documents\Manips\Gauthier\Directivité\Enregistrement_Anechoique\HeadRots'

def get_df_suffixed_axes_labels(data_frame: pd.DataFrame) -> list[str]:
    return [axis for axis in data_frame.columns if any(map(lambda a: a in axis, [_yaw, _pitch]))]

def plot_head_rot(dataFrame: pd.DataFrame) -> None:
    plot_ypr(dataFrame, get_df_suffixed_axes_labels(dataFrame))
    plt.show()

def plot_head_rot_comparison(dataFrame_1: pd.DataFrame, dataFrame_2: pd.DataFrame, time_delay: float = 0., show_fig: bool = True, save_fig: bool = False, fig_name : str = 'figure') -> None:
    axes_labels_1 = get_df_suffixed_axes_labels(dataFrame_1)
    axes_labels_2 = get_df_suffixed_axes_labels(dataFrame_2)
    if any(axis in axes_labels_2 for axis in axes_labels_1):
        axes_labels_1 = [axis + '_x' for axis in axes_labels_1]
        axes_labels_2 = [axis + '_y' for axis in axes_labels_2]
    dataFrame_2['t'] = dataFrame_2['t'] - time_delay
    data_frame = pd.merge(dataFrame_1, dataFrame_2, on='t')
    plot_ypr(data_frame, [axes_labels_1[0], axes_labels_2[0], axes_labels_1[1], axes_labels_2[1]])
    plt.ylim([-150, 120])
    
    if save_fig:
        plt.savefig(fig_name)
    
    if show_fig:
        plt.show()

    plt.close()

def create_data_frame(fileName: str, suffix: str = '') -> pd.DataFrame:    
    quats = read_quaternions(fileName)
    quats = clean_quaternions(quats)
    df = create_quaternions_data_frame(quats)
    euler_df = create_ypr_data_frame(df, suffix)
    euler_df = filter_data_frame(euler_df, suffix)
    return euler_df

def read_quaternions(fileName: str) -> str:
    f = open(fileName)
    quats = f.read()
    f.close()
    return quats

def clean_quaternions(quats: str) -> list[str]:
    return quats.removesuffix(' _ ').split(' _ ')

def create_quaternions_data_frame(quats: str) -> pd.DataFrame:
    quatsSplit = [s.split(' ') for s in quats]
    columns = ['X', 'Y', 'Z', 'W']
    return pd.DataFrame(quatsSplit, columns = columns, dtype = float)

def create_ypr_data_frame(quat_df: pd.DataFrame, suffix: str = '') -> pd.DataFrame:
    rot = Rotation.from_quat(quat_df)
    rot_euler = rot.as_euler('xyz', degrees=True)
    euler_df = pd.DataFrame(data=rot_euler, columns=[_yaw + suffix, _pitch + suffix, _roll + suffix])
    period = 0.01
    t = [x * period for x in range(len(euler_df))]
    euler_df['t'] = pd.to_numeric(t)
    return euler_df

def filter_data_frame(df: pd.DataFrame, suffix: str = '') -> pd.DataFrame:
    (yaw, pitch, roll) = [axis + suffix for axis in [_yaw, _pitch, _roll]]
    b, a = scipy.signal.iirfilter(4, Wn=2.5, fs=100, btype="low", ftype="butter")
    yawOffset = df[yaw][0]
    pitchOffset = df[pitch][0]
    rollOffset = df[roll][0]
    df[yaw] = scipy.signal.lfilter(b, a, df[yaw] - yawOffset) + yawOffset
    df[pitch] = scipy.signal.lfilter(b, a, df[pitch] - pitchOffset) + pitchOffset
    df[roll] = scipy.signal.lfilter(b, a, df[roll] - rollOffset) + rollOffset
    return df
    
def plot_ypr(df: pd.DataFrame, axes: list[str]) -> None:
    ax = df.plot(x='t', y=axes)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Angle (°)")
    df.rename_axis()

def mean_angular_diff(original: pd.Series, repro: pd.Series) -> float:
    length = min(len(original), len(repro))
    original = original[:length]
    repro = repro[:length]
    return round((sum(abs(original - repro))) / length, 1)

def mean_angular_diffs(original: pd.DataFrame, repro: pd.DataFrame) -> tuple:
    yaw = mean_angular_diff(original.iloc[:,0], repro.iloc[:,0])
    pitch = mean_angular_diff(original.iloc[:,1], repro.iloc[:,1])
    return (yaw, pitch)

def write_visualization_md_file(sentences: pd.DataFrame) -> None:
    output = '|0|1|2|\n|:---:|:---:|:---:|\n'
    for r in range(0, len(sentences), 3):
        takes = sentences.iloc[r], sentences.iloc[r+1], sentences.iloc[r+2]
        output += '|'.join(list(map(lambda x: f'**{x.loc['ID']}** [{x.loc['d_Y']} ; {x.loc['d_P']}]' , takes))) + '\n'
        output += '|'.join(list(map(lambda x: f'![alt text]({os.path.basename(x.loc['fig_n'])}.png)' , takes))) + '\n'
    f = open(r'C:\Users\labsticc\Documents\Manips\Gauthier\Directivité\utils_manip_directivite\angular_difference_visualization.md', 'w')
    f.write(output)
    f.close()
    

def main() -> None:

    sentences = pd.read_csv(r'manip-dir-data\Phrases.csv')
    sentences = sentences.sort_values(by = ['D','A','M','T','N','Rec_N'])
    

    yaw_diffs = []
    pitch_diffs = []
    figure_names = []

    for i in range(len(sentences)):
        take = sentences.iloc[i]
        original_file = os.path.join(HEADROTS_FOLDER, f'{take['ID']}.txt')
        repro_file = os.path.join(HEADROTS_FOLDER, f'{take['ID']}_1.txt')

        original = create_data_frame(original_file, '_o')
        repro = create_data_frame(repro_file, '_r')
        fig_name = rf"C:\Users\labsticc\Documents\Manips\Gauthier\Directivité\Enregistrement_Anechoique\HeadRots_figs\{'_'.join(list(map(lambda x: str(x), take.iloc[:7])))}"
        plot_head_rot_comparison(dataFrame_1 = original, dataFrame_2 = repro, time_delay = 0, show_fig = False, save_fig = False, fig_name = fig_name)
        
        diff_yaw, diff_pitch = mean_angular_diffs(original, repro)
        yaw_diffs.append(diff_yaw)
        pitch_diffs.append(diff_pitch)
        figure_names.append(fig_name)
    sentences.insert(loc = 7, column = 'd_Y', value = yaw_diffs)
    sentences.insert(loc = 8, column = 'd_P', value = pitch_diffs)
    sentences.insert(loc = 9, column = 'fig_n', value = figure_names)
    write_visualization_md_file(sentences)

if __name__ == '__main__':
    main()

