import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from utils_manip_directivite.analysis.extract_data import get_dataframe

def plot(df: pd.DataFrame):
    sns.set_theme()
    sns.catplot(x = 'movement',
                y = 'answer_timbre',
                col = 'angle',
                hue = 'source',
                data = df)
    plt.show()

def main() -> None:
    df = get_dataframe()
    df = df.query('user > 1')
    plot(df)

if __name__ == '__main__':
    main()