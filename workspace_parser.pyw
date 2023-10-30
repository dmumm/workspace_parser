import json
import tkinter as tk
from tkinter import ttk
import os
from datetime import datetime

# Convert Unix timestamp to human-readable date-time
def convert_timestamp_to_date(timestamp):
    return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

# Sorting function
def treeview_sort_column(tv, col, reverse):
    # Fetch a sample item to determine the type of the data in the column
    sample_item = tv.set(tv.get_children('')[0], col)

    # Check if the sample item is numeric
    is_numeric = sample_item.replace('.', '', 1).isdigit()

    if is_numeric:
        # Sort as numbers
        l = [(float(tv.set(k, col)), k) for k in tv.get_children('')]
    else:
        # Sort as strings (case-insensitive)
        l = [(tv.set(k, col).lower(), k) for k in tv.get_children('')]

    l.sort(reverse=reverse)

    # rearrange items in sorted positions
    for index, (val, k) in enumerate(l):
        tv.move(k, '', index)

    # reverse sort next time
    tv.heading(col, command=lambda: treeview_sort_column(tv, col, not reverse))

# Determine the path to the WorkspaceCache files
paths_to_check = [
    os.path.join(os.environ['LOCALAPPDATA'], 'Microsoft', 'Edge Dev', 'User Data', 'Default', 'Workspaces', 'WorkspacesCache'),
    os.path.join(os.environ['LOCALAPPDATA'], 'Microsoft', 'Edge Canary', 'User Data', 'Default', 'Workspaces', 'WorkspacesCache'),
    os.path.join(os.environ['LOCALAPPDATA'], 'Microsoft', 'Edge', 'User Data', 'Default', 'Workspaces', 'WorkspacesCache')
]

# Dictionary to hold final workspaces after checking duplicates and last active time
workspace_dict = {}

# Parsing multiple paths
for path in paths_to_check:
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as file:
            parsed_data = json.load(file)

        workspaces = parsed_data['workspaces']

        for workspace in workspaces:
            name = workspace['name']

            # Check for duplicates and replace if newer
            if name not in workspace_dict or (workspace.get('last_active_time', 0) > workspace_dict[name].get('last_active_time', 0)):
                workspace_dict[name] = workspace

# Convert the dictionary to a list for iteration
final_workspaces = list(workspace_dict.values())


# Create main window
root = tk.Tk()
root.title("Workspaces Table")

# Create treeview for table representation
tree = ttk.Treeview(root, columns=('Color', 'Name', 'Count', 'ID', 'Last Active Time', 'Connection URL'), show='headings')

tree.heading('Color', text='Color', command=lambda: treeview_sort_column(tree, 'Color', False))
tree.heading('Name', text='Workspace Name', command=lambda: treeview_sort_column(tree, 'Name', False))
tree.heading('Count', text='Tab Count', command=lambda: treeview_sort_column(tree, 'Count', False))
tree.heading('ID', text='ID', command=lambda: treeview_sort_column(tree, 'ID', False))
tree.heading('Last Active Time', text='Last Active Time', command=lambda: treeview_sort_column(tree, 'Last Active Time', False))
tree.heading('Connection URL', text='Connection URL', command=lambda: treeview_sort_column(tree, 'Connection URL', False))

tree.pack(fill=tk.BOTH, expand=1)



# Populate treeview with parsed data
color_map = {
    0: "#69a1fa", # Blue
    1: "#58d3db",  # Teal
    2: "#a4cc6c",  # Green
    3: "#cf87da",  # Violet
    4: "#ee5fb7", # Pink
    5: "#ffbf72",  # Orange
    6: "#df8e64",  # Brown
    7: "#9e9b99", # Gray
    8: "#e9835e", # Red
    9: "#dfdfdf", # Light Gray
    10: "#b28fff",  # Purple
    11: "#5ae0a0", # Dark Green
    12: "#FFFFFF", # No color
    13: "#c7dced",  # Light Blue
}

# Populate treeview with final workspaces
for workspace in final_workspaces:
    color = workspace['color']
    name = workspace['name']
    count = workspace['count']
    id_val = workspace['id']
    connection_url = workspace['connectionUrl']
    # Using the get method allows for a default value if the key doesn't exist
    last_active_time = workspace.get('last_active_time', "")
    if last_active_time:  # if timestamp exists
        last_active_time = convert_timestamp_to_date(float(last_active_time))

    tree.insert('', 'end', values=(color, name, count, id_val, last_active_time, connection_url),
                tags=(color_map.get(workspace['color'], "#FFFFFF"),))


for color, hex_value in color_map.items():
    tree.tag_configure(hex_value, background=hex_value)

# Mapping of column identifiers to their index
col_identifier_to_index = {f"#{i+1}": i for i in range(len(tree["columns"]))}

def on_treeview_click(event):

    # Identify the row and column clicked
    item = tree.identify('item', event.x, event.y)
    col = tree.identify('column', event.x, event.y)

    if not col:
        return

    # TODO: debug
    print(f"Clicked column identifier: {col}")

    if col == "#0":
        value = tree.item(item, 'text')
    else:
        # Retrieve the column's index based on its identifier
        col_index = col_identifier_to_index[col]

        # Get the value from the clicked cell
        value = tree.item(item, 'values')[col_index]

    # Copy the value to the clipboard
    root.clipboard_clear()
    root.clipboard_append(value)
    root.update()  # Required to finalize the clipboard update

# Bind the function to the treeview
tree.bind('<Button-1>', on_treeview_click)

# Start the main GUI loop
root.mainloop()
