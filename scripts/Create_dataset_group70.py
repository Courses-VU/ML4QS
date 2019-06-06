import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def plot_dataset(dataset, folder):
    plt.plot(dataset.loc[:, ["gFx", "gFy", "gFz"]])
    plt.legend(("gFx", "gFy", "gFz"))
    plt.ylabel("g-force")
    plt.xlabel("Time (s)")
    plt.savefig(folder + "g_force.png")
    plt.close()

    plt.plot(dataset.loc[:, ["ax", "ay", "az"]])
    plt.legend(("ax", "ay", "az"))
    plt.ylabel("Acceleration (m/s" + r'$^2$' + ")")
    plt.xlabel("Time (s)")
    plt.savefig(folder + "lin_acc.png")
    plt.close()

    plt.plot(dataset.loc[:, ["wx", "wy", "wz"]])
    plt.legend(("wx", "wy", "wz"))
    plt.ylabel("Rotation (rad/s)")
    plt.xlabel("Time (s)")
    plt.savefig(folder + "gyro.png")
    plt.close()

    plt.plot(dataset.loc[:, "p"])
    plt.ylabel("Pressure (hPa)")
    plt.xlabel("Time (s)")
    plt.savefig(folder + "pressure.png")
    plt.close()

    plt.plot(dataset.loc[:, ["Bx", "By", "Bz"]])
    plt.legend(("Bx", "By", "Bz"))
    plt.ylabel("Magnetic force (" + r'$\mu$' + 'T)')
    plt.xlabel("Time (s)")
    plt.savefig(folder + "magnetic.png")
    plt.close()

    plt.plot(dataset.loc[:, ["Azimuth", "Pitch", "Roll"]])
    plt.legend(("Azimuth", "Pitch", "Roll"))
    plt.ylabel("Inclination (degrees)")
    plt.xlabel("Time (s)")
    plt.savefig(folder + "inclination.png")
    plt.close()

    plt.plot(dataset.loc[:, "Gain"])
    plt.ylabel("Sound intensity (dB)")
    plt.xlabel("Time (s)")
    plt.savefig(folder + "sound.png")
    plt.close()

def make_empty_dataset(min_t, max_t, cols, delta_t):
    timestamps = np.arange(0, max_t - min_t, delta_t)
    empty_dataset = pd.DataFrame(index=timestamps, columns=cols)

    return empty_dataset


def create_dataset(df_raw, delta_t, labels):
    min_t = min(df_raw.time)
    max_t = max(df_raw.time)
    cols = df_raw.drop(["time"], axis=1).columns

    empty_dataset = make_empty_dataset(min_t, max_t, cols, delta_t)

    for i in range(0, len(empty_dataset.index)):
        relevant_rows = df_raw[
            (df_raw["time"] - min_t >= i * delta_t) &
            (df_raw["time"] - min_t < (i + 1) * delta_t)
            ]

        for col in empty_dataset.columns:
            if len(relevant_rows) > 0:
                empty_dataset.loc[empty_dataset.index[i], col] = np.average(relevant_rows[col])
            else:
                raise ValueError("No relevant rows.")

    empty_dataset = add_labels(empty_dataset, labels, delta_t, min_t, max_t)

    return empty_dataset


def add_labels(dataset, labels, delta_t, min_t, max_t):
    labels_list = np.unique(labels.activity)
    for label in labels_list:
        dataset["label_" + label] = 0

    for i in range(0, len(dataset.index)):
        for j in range(0, len(labels.index)):
            if (i * delta_t >= labels.time_1[j]) & (i * delta_t < labels.time_2[j]):
                dataset.loc[dataset.index[i], "label_" + labels.activity[j]] = 1

    return dataset


def preprocess(data):
    df_raw = data.drop(["Unnamed: 18"], axis=1)
    df_raw = df_raw[df_raw.Gain != "-∞"]
    df_raw = df_raw.astype("float64")

    return df_raw


def main():
    # Variables
    delta_t = 0.25

    data = pd.read_csv("../data/first_data")
    labels = pd.read_csv("../data/intervals.csv", sep="\t")
    df_raw = preprocess(data)

    dataset = create_dataset(df_raw, delta_t, labels)

    plot_dataset(dataset, "../output/")

    dataset.to_csv("../data/processed_data.csv")


if __name__ == '__main__':
    main()