import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def plot_CC(chart_obj, text=""):
    if isinstance(chart_obj, tuple):
        fig, axis = plt.subplots(2,1)
        plot_single(chart_obj[0], axis[0], 0)
        plot_single(chart_obj[1], axis[1], 1)
    else:
        fig, axis = plt.subplots(1,1)
        plot_single(chart_obj, axis, 0)

    fig.tight_layout(rect=[0, 0.05, 1, 1])
    fig.text(0.5, 0.01, text, ha="center", va="bottom", fontsize=15, fontweight="bold")

    plt.show()

def plot_single(chart_obj, axis, n):
    axis.plot(chart_obj.index, chart_obj.cl,color="blue",
        linestyle="--",
        linewidth=0.75,
        markersize=5)
    axis.plot(chart_obj.index, chart_obj.lcl,color="red",
        linestyle="-",
        linewidth=0.75,
        markersize=5)
    axis.plot(chart_obj.index, chart_obj.ucl,color="red",
        linestyle="-",
        linewidth=0.75,
        markersize=5)

    axis.plot(chart_obj.index, chart_obj.data,color="black",
        linestyle="-",
        linewidth=1.5,
        marker="o",
        markersize=3)
    if chart_obj.has_pattern:
        for mask in chart_obj.patterns:
            axis.plot(chart_obj.index[mask], chart_obj.data[mask],color="darkorange",
                linestyle="-",
                linewidth=2,
                marker="o",
                markersize=4)
    axis.plot(chart_obj.index[chart_obj.outside], chart_obj.data[chart_obj.outside],color="red",
        linestyle="",
        linewidth=1.5,
        marker="o",
        markersize=5)
    
    axis.grid(axis="x")               
    axis.set_xlim(left=chart_obj.index[0], right=chart_obj.index[-1])
    axis.set_title(chart_obj.type_full)
    axis.set_ylabel(chart_obj.yaxis)



    













