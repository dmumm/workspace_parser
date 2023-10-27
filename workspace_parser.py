import json
import tkinter as tk
from tkinter import ttk
import os

# Sorting function
def treeview_sort_column(tv, col, reverse):
    l = [(tv.set(k, col), k) for k in tv.get_children('')]
    l.sort(reverse=reverse)

    # rearrange items in sorted positions
    for index, (val, k) in enumerate(l):
        tv.move(k, '', index)

    # reverse sort next time
    tv.heading(col, command=lambda: treeview_sort_column(tv, col, not reverse))

# Determine the path to the WorkspaceCache file
workspace_cache_path = os.path.join(os.environ['LOCALAPPDATA'], 'Microsoft', 'Edge Dev', 'User Data', 'Default', 'Workspaces', 'WorkspacesCache')

# Read the JSON data from the file
with open(workspace_cache_path, 'r', encoding='utf-8') as file:
    parsed_data = json.load(file)

workspaces = parsed_data['workspaces']

# Create main window
root = tk.Tk()
root.title("Workspaces Table")

# Create treeview for table representation
tree = ttk.Treeview(root, columns=('Name', 'Count', 'ID', 'Connection URL'), show='headings')

tree.heading('Name', text='Workspace Name', command=lambda: treeview_sort_column(tree, 'Name', False))
tree.heading('Count', text='Tab Count', command=lambda: treeview_sort_column(tree, 'Count', False))
tree.heading('ID', text='ID', command=lambda: treeview_sort_column(tree, 'ID', False))

tree.heading('Connection URL', text='Connection URL', command=lambda: treeview_sort_column(tree, 'Connection URL', False))

tree.pack(fill=tk.BOTH, expand=1)



# Populate treeview with parsed data
color_map = {
    2: "#FF0000",  # Red
    3: "#00FF00",  # Green
    5: "#0000FF",  # Blue
    10: "#FFFF00",  # Yellow
    13: "#FF00FF",  # Magenta
    # ... add other mappings as needed
}

for workspace in workspaces:
    tree.insert('', 'end', values=(workspace['name'], workspace['count'], workspace['id'], workspace['connectionUrl']),
            tags=(color_map.get(workspace['color'], "#FFFFFF"),))  # Default to white if color not found in map

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
