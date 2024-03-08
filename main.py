import os
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageSequence
import redis
import threading

def reset_progress_bars():
    progress_bar_fetch['value'] = 0
    progress_bar_delete['value'] = 0
    progress_label_fetch.config(text="", style='')
    progress_label_delete.config(text="", style='')

def fetch_data():
    reset_progress_bars()  # Reset progress bars
    key_pattern = entry.get()
    if key_pattern:
        keys = redis_client.keys(key_pattern)
        count = len(keys)
        data_text.delete(1.0, tk.END)
        data_text.insert(tk.END, f"Total keys found: {count}\n\n")
        progress_bar_fetch['maximum'] = count  # Set maximum value for progress bar
        progress_bar_fetch['style'] = 'green.Horizontal.TProgressbar'  # Change progress bar color to green
        for i, key in enumerate(keys, start=1):
            data_text.insert(tk.END, f"{key}\n")
            progress_bar_fetch['value'] = i  # Update progress bar value
            progress_bar_fetch.update()  # Force update of progress bar
            progress_label_fetch.config(text=f"Fetching... {i}/{count}", style='green.TLabel')  # Update counter label color
    else:
        data_text.delete(1.0, tk.END)
        data_text.insert(tk.END, "Please enter a key pattern.")

def delete_keys():
    key_pattern = entry.get()
    if key_pattern:
        keys = redis_client.keys(key_pattern)
        count = len(keys)
        progress_bar_delete['maximum'] = count  # Set maximum value for progress bar
        progress_bar_delete['style'] = 'red.Horizontal.TProgressbar'  # Change progress bar color to red
        for i, key in enumerate(keys, start=1):
            redis_client.delete(key)
            progress_bar_delete['value'] = i  # Update progress bar value
            progress_bar_delete.update()  # Force update of progress bar
            progress_label_delete.config(text=f"Deleting... {i}/{count}", style='red.TLabel')  # Update counter label color
        data_text.delete(1.0, tk.END)
        data_text.insert(tk.END, "Keys deleted successfully.")
    else:
        data_text.delete(1.0, tk.END)
        data_text.insert(tk.END, "Please enter a key pattern.")

def connect_to_redis():
    def connect():
        global redis_client
        host = host_entry.get()
        port = port_entry.get()
        ssl_enabled = ssl_var.get()  # Check if SSL is enabled
        try:
            if ssl_enabled:
                redis_client = redis.StrictRedis(host=host, port=int(port), db=0, ssl=True)
            else:
                redis_client = redis.StrictRedis(host=host, port=int(port), db=0)
            if redis_client.ping():
                status_label.config(text="Connected to Redis", foreground="green")
            else:
                status_label.config(text="Unable to connect to Redis", foreground="red")
        except Exception as e:
            status_label.config(text=f"Error: {str(e)}", foreground="red")
    
    # Create a thread to connect to Redis
    threading.Thread(target=connect, daemon=True).start()

# Function to update the animation
def update_animation(frame_num):
    gif_label.configure(image=frames[frame_num])  # Update the image
    frame_num = (frame_num + 1) % len(frames)
    root.after(100, update_animation, frame_num)  # Schedule the next update after 100 milliseconds

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Create the Tkinter window
root = tk.Tk()
root.title("Redis Data Viewer")

# Set the application icon
icon_path = resource_path(resource_path("Radish.ico"))
if os.path.exists(icon_path):
    root.iconbitmap(default=icon_path)

# Create a style for ttk widgets
style = ttk.Style()
style.theme_use('clam')

# Configure style for progress bars
style.configure('green.Horizontal.TProgressbar', foreground='green', background='green')
style.configure('green.TLabel', foreground='green')
style.configure('red.Horizontal.TProgressbar', foreground='red', background='red')
style.configure('red.TLabel', foreground='red')

# Create and pack widgets
frame = ttk.Frame(root, padding=10)
frame.grid(row=0, column=0, sticky="nsew")

host_label = ttk.Label(frame, text="Enter Redis Host:")
host_label.grid(row=0, column=3, padx=5, pady=5, sticky='e')

host_entry = ttk.Entry(frame, width=30)
host_entry.grid(row=0, column=4, padx=5, pady=5)

port_label = ttk.Label(frame, text="Redis Port:")
port_label.grid(row=0, column=5, padx=5, pady=5, sticky='e')

port_entry = ttk.Entry(frame, width=10)
port_entry.grid(row=0, column=6, padx=5, pady=5)

ssl_var = tk.BooleanVar()  # Variable to store SSL option
ssl_checkbox = ttk.Checkbutton(frame, text="Enable SSL", variable=ssl_var)
ssl_checkbox.grid(row=0, column=7, padx=5, pady=5)

connect_button = ttk.Button(frame, text="Connect", command=connect_to_redis)
connect_button.grid(row=0, column=8, padx=5, pady=5)

status_label = ttk.Label(frame, text="")
status_label.grid(row=0, column=9, padx=5, pady=5)

label = ttk.Label(frame, text="Enter key pattern:")
label.grid(row=1, column=3, padx=5, pady=5, sticky='e')

entry = ttk.Entry(frame, width=50)
entry.grid(row=1, column=4, padx=5, pady=5, columnspan=4, sticky='ew')

fetch_button = ttk.Button(frame, text="Fetch Data", command=fetch_data)
fetch_button.grid(row=1, column=8, padx=5, pady=5)

delete_button = ttk.Button(frame, text="Delete Keys", command=delete_keys)
delete_button.grid(row=1, column=9, padx=5, pady=5)

# Load the GIF frames using PIL
gif = Image.open(resource_path("peach-goma-trash-throw.gif"))
frames = [ImageTk.PhotoImage(frame.resize((100, 100))) for frame in ImageSequence.Iterator(gif)]

# Create a label to display the GIF
gif_label = tk.Label(frame, image=frames[0])
gif_label.grid(row=0, rowspan=2, column=0, columnspan=3, padx=5, pady=5, sticky='nsew')

# Create data_text widget
data_text = tk.Text(root, width=80, height=30)
data_text.grid(row=1, column=0, padx=5, pady=5, sticky='nsew')

# Configure scrollbar
scrollbar = ttk.Scrollbar(root, orient=tk.VERTICAL, command=data_text.yview)
scrollbar.grid(row=1, column=1, sticky='ns')
data_text.config(yscrollcommand=scrollbar.set)

# Create progress bars
progress_bar_fetch = ttk.Progressbar(root, orient='horizontal', mode='determinate', style='green.Horizontal.TProgressbar')
progress_bar_fetch.grid(row=2, column=0, padx=5, pady=5, sticky='ew')

progress_bar_delete = ttk.Progressbar(root, orient='horizontal', mode='determinate', style='red.Horizontal.TProgressbar')
progress_bar_delete.grid(row=3, column=0, padx=5, pady=5, sticky='ew')

# Create counter labels
progress_label_fetch = ttk.Label(progress_bar_fetch, text="", anchor=tk.CENTER)
progress_label_fetch.grid(row=2, column=3, padx=5, pady=5, sticky='ew')

progress_label_delete = ttk.Label(progress_bar_delete, text="", anchor=tk.CENTER)
progress_label_delete.grid(row=3, column=3, padx=5, pady=5, sticky='ew')

# Configure grid to make it responsive
root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(0, weight=1)

# Start the animation
update_animation(0)

# Run the Tkinter event loop
root.mainloop()
