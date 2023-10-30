import json
import tkinter as tk
from tkinter import ttk
import os
from datetime import datetime

# Constants
PATHS_TO_CHECK = [
    os.path.join(os.environ['LOCALAPPDATA'], 'Microsoft', 'Edge Dev', 'User Data', 'Default', 'Workspaces', 'WorkspacesCache'),
    os.path.join(os.environ['LOCALAPPDATA'], 'Microsoft', 'Edge Canary', 'User Data', 'Default', 'Workspaces', 'WorkspacesCache'),
    os.path.join(os.environ['LOCALAPPDATA'], 'Microsoft', 'Edge', 'User Data', 'Default', 'Workspaces', 'WorkspacesCache')
]

COLOR_MAP = {
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

# Retrieve and parse workspaces from specified paths
def parse_workspaces(paths):
    workspace_dict = {}
    for path in paths:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as file:
                parsed_data = json.load(file)
            workspaces = parsed_data['workspaces']
            for workspace in workspaces:
                name = workspace['name']
                if name not in workspace_dict or (workspace.get('last_active_time', 0) > workspace_dict[name].get('last_active_time', 0)):
                    workspace_dict[name] = workspace
    return list(workspace_dict.values())

def populate_treeview(tree, workspaces):
    """Fill the treeview with workspace data."""
    for workspace in workspaces:
        color = workspace['color']
        name = workspace['name']
        count = workspace['count']
        id_val = workspace['id']
        connection_url = workspace['connectionUrl']
        last_active_time = workspace.get('last_active_time', "")
        if last_active_time:
            last_active_time = convert_timestamp_to_date(float(last_active_time))
        tree.insert('', 'end', values=(color, name, count, id_val, last_active_time, connection_url),
                    tags=(COLOR_MAP.get(workspace['color'], "#010101"),))

def on_treeview_click(event, tree, root):

    # Identify the row and column clicked
    item = tree.identify('item', event.x, event.y)
    col = tree.identify('column', event.x, event.y)

    # Mapping of column identifiers to their index
    col_identifier_to_index = {f"#{i + 1}": i for i in range(len(tree["columns"]))}

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

#  Main function to create and run the GUI
def main():
    final_workspaces = parse_workspaces(PATHS_TO_CHECK)

    # GUI setup
    root = tk.Tk()
    root.title("Workspaces Table")
    tree = ttk.Treeview(root, columns=('Color', 'Name', 'Tabs', 'ID', 'Last Active Time', 'Connection URL'), show='headings')
    # Setting up the tree headings
    for col in tree["columns"]:
        tree.heading(col, text=col, command=lambda c=col: treeview_sort_column(tree, c, False))
    tree.pack(fill=tk.BOTH, expand=1)
    populate_treeview(tree, final_workspaces)

    for _, hex_value in COLOR_MAP.items():
        tree.tag_configure(hex_value, background=hex_value)

    tree.bind('<Button-1>', lambda e: on_treeview_click(e, tree, root))

    root.mainloop()


if __name__ == "__main__":
        main()