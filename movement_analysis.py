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

def plot_head_rot_comparison(dataFrame_1: pd.DataFrame, dataFrame_2: pd.DataFrame, timeDelay: float = 0., save_fig: bool = False, fig_name : str = 'figure') -> None:
    axes_labels_1 = get_df_suffixed_axes_labels(dataFrame_1)
    axes_labels_2 = get_df_suffixed_axes_labels(dataFrame_2)
    if any(axis in axes_labels_2 for axis in axes_labels_1):
        axes_labels_1 = [axis + '_x' for axis in axes_labels_1]
        axes_labels_2 = [axis + '_y' for axis in axes_labels_2]
    dataFrame_2['t'] = dataFrame_2['t'] - timeDelay
    data_frame = pd.merge(dataFrame_1, dataFrame_2, on='t')
    plot_ypr(data_frame, [axes_labels_1[0], axes_labels_2[0], axes_labels_1[1], axes_labels_2[1]])
    plt.ylim([-150, 120])
    
    if save_fig:
        plt.savefig(fig_name)
    else:
        plt.show()

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


def main() -> None:

    for i in range(0,6):

        take_1 = os.path.join(HEADROTS_FOLDER, f'{i}.txt')
        take_2 = os.path.join(HEADROTS_FOLDER, f'{i}_1.txt')

        take_1_df = create_data_frame(take_1, '_o')
        take_2_df = create_data_frame(take_2, '_r')
        plot_head_rot_comparison(take_1_df, take_2_df, 0.3, False, rf"C:\Users\User\Documents\Gaut\PostDoc\Manips\Directivité\MesuresMouvement\quaternion_speed\window_{i}.png")

    #PlotHeadRotComparison(original, repro, '_ori', '_rep')

    
    #PlotHeadRot(repro)

if __name__ == '__main__':
    main()

