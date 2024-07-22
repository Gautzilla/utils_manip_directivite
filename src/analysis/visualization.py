import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from extract_data import get_dataframe

def plot(df: pd.DataFrame):
    sns.set_theme()
    sns.catplot(x = 'movement',
                y = 'plausibility',
                col = 'angle',
                hue = 'source',
                data = df)
    plt.show()

def main() -> None:
    df = get_dataframe()
    plot(df)

if __name__ == '__main__':
    main()