import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from utils_manip_directivite.analysis.extract_data import get_dataframe

def plot_results(df: pd.DataFrame, question: str):
    sns.set_theme()
    f, axs = plt.subplots(nrows = 2, ncols = 2, sharey = True)
    sns.boxplot(x = 'movement',
                y = question,
                hue = 'source',
                data = df.query('room == "SUAPS" and angle == "Front"'),
                ax = axs[0,0])
    sns.boxplot(x = 'movement',
                y = question,
                hue = 'source',
                data = df.query('room == "CLOUS" and angle == "Front"'),
                ax = axs[0,1])
    sns.boxplot(x = 'movement',
                y = question,
                hue = 'source',
                data = df.query('room == "SUAPS" and angle == "Side"'),
                ax = axs[1,0])
    sns.boxplot(x = 'movement',
                y = question,
                hue = 'source',
                data = df.query('room == "CLOUS" and angle == "Side"'),
                ax = axs[1,1])
    plt.show()

def main() -> None:
    df = get_dataframe(z_score = False)
    df = df.query('user > 1').sort_values(by=['source'])
    plot_results(df = df, question = 'answer_timbre')

if __name__ == '__main__':
    main()