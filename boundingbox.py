import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from scipy.spatial.transform import Rotation as R
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# test 1
def generate_prism(n, r, h):
    angles = np.linspace(0, 2 * np.pi, int(n), endpoint=False)
    x = r * np.cos(angles)
    y = r * np.sin(angles)
    z_bottom = np.zeros(int(n))
    z_top = np.full(int(n), h)

    vertices = np.column_stack([np.tile(x, 2), np.tile(y, 2), np.hstack([z_bottom, z_top])])
    faces = []
    for i in range(int(n)):
        faces.append([i, (i + 1) % int(n), (i + 1) % int(n) + int(n), i + int(n)])
    faces.append(list(range(int(n))))  # 底面
    faces.append(list(range(int(n), 2 * int(n))))  # 顶面

    return vertices, faces


def get_bounding_box(vertices):
    min_corner = vertices.min(axis=0)
    max_corner = vertices.max(axis=0)
    center = (min_corner + max_corner) / 2
    return min_corner, max_corner, center


def plot_prism(n, r, h, rx, ry, rz):
    plt.close('all')  # 释放旧图形
    fig = plt.figure(figsize=(6, 6))
    ax = fig.add_subplot(111, projection='3d')
    vertices, faces = generate_prism(n, r, h)

    rotation = R.from_euler('xyz', [rx, ry, rz], degrees=True)
    rotated_vertices = rotation.apply(vertices)
    prism_center = rotated_vertices.mean(axis=0)

    min_corner, max_corner, box_center = get_bounding_box(rotated_vertices)

    poly3d_faces = [[rotated_vertices[idx] for idx in face] for face in faces]
    ax.add_collection3d(Poly3DCollection(poly3d_faces, facecolors='cyan', edgecolors='k', linewidths=1, alpha=0.5))

    box_faces = [
        [min_corner, [max_corner[0], min_corner[1], min_corner[2]], [max_corner[0], max_corner[1], min_corner[2]],
         [min_corner[0], max_corner[1], min_corner[2]]],
        [min_corner, [min_corner[0], min_corner[1], max_corner[2]], [max_corner[0], min_corner[1], max_corner[2]],
         [max_corner[0], min_corner[1], min_corner[2]]],
        [max_corner, [min_corner[0], max_corner[1], max_corner[2]], [min_corner[0], min_corner[1], max_corner[2]],
         [max_corner[0], min_corner[1], max_corner[2]]],
        [max_corner, [max_corner[0], min_corner[1], max_corner[2]], [max_corner[0], min_corner[1], min_corner[2]],
         [max_corner[0], max_corner[1], min_corner[2]]]
    ]
    ax.add_collection3d(Poly3DCollection(box_faces, facecolors='orange', edgecolors='r', linewidths=1, alpha=0.3))

    ax.scatter(*prism_center, color='blue', label='Prism Center', s=100)
    ax.scatter(*box_center, color='red', label='Bounding Box Center', s=100)

    ax.set_xlim([min_corner[0] - 1, max_corner[0] + 1])
    ax.set_ylim([min_corner[1] - 1, max_corner[1] + 1])
    ax.set_zlim([min_corner[2] - 1, max_corner[2] + 1])
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.legend()

    info_label.config(text=f"Edges: {n}\nPrism Center: {prism_center}\nBox Center: {box_center}")

    return fig


def update_plot(*args):
    global canvas
    n = int(n_slider.get())
    r = r_slider.get()
    h = h_slider.get()
    rx = rx_slider.get()
    ry = ry_slider.get()
    rz = rz_slider.get()
    fig = plot_prism(n, r, h, rx, ry, rz)
    if 'canvas' in globals():
        canvas.figure = fig
        canvas.draw()


root = tk.Tk()
root.title("3D Prism Bounding Box")

frame = ttk.Frame(root)
frame.pack(side=tk.LEFT, padx=10, pady=10)

n_slider = ttk.Scale(frame, from_=3, to=20, orient='horizontal')
n_slider.set(5)
r_slider = ttk.Scale(frame, from_=1, to=10, orient='horizontal')
r_slider.set(3)
h_slider = ttk.Scale(frame, from_=5, to=30, orient='horizontal')
h_slider.set(10)
rx_slider = ttk.Scale(frame, from_=0, to=360, orient='horizontal')
rx_slider.set(0)
ry_slider = ttk.Scale(frame, from_=0, to=360, orient='horizontal')
ry_slider.set(0)
rz_slider = ttk.Scale(frame, from_=0, to=360, orient='horizontal')
rz_slider.set(0)

for widget, label in zip([n_slider, r_slider, h_slider, rx_slider, ry_slider, rz_slider],
                         ["Edges (n)", "Radius (r)", "Height (h)", "Rotate X", "Rotate Y", "Rotate Z"]):
    ttk.Label(frame, text=label).pack()
    widget.pack()
    widget.config(command=update_plot)  # 绑定更新事件

info_label = ttk.Label(frame, text="")
info_label.pack()

canvas_frame = ttk.Frame(root)
canvas_frame.pack(side=tk.RIGHT)
fig = plot_prism(5, 3, 10, 0, 0, 0)
canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
canvas.get_tk_widget().pack()

root.mainloop()
