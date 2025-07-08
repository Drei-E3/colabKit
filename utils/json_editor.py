import streamlit as st

st.title("🧩 Config Editor")

# Initialize default data if not already set
if "root_rows" not in st.session_state:
    st.session_state["root_rows"] = [
        {"key": "project name", "type": "normal", "value": ""},
        {"key": "colab path", "type": "normal", "value": ""},
        {"key": "gdrive path", "type": "normal", "value": ""}
    ]

# Helper: Locate nested rows by path
def get_rows_by_path(rows, path):
    if path == "root":
        return rows
    keys = path.split("_child")
    current = rows
    for key in keys[1:]:  # Skip "root"
        index = int(key.split("_")[-1])  # Extract index like box_0
        current = current[index]["children"]
    return current

# Callback: Add a new row
def add_row_callback(path):
    target = get_rows_by_path(st.session_state["root_rows"], path)
    target.append({"key": "", "type": "normal", "value": ""})

# JSON editor renderer
def render_editor(rows, path):
    to_delete = []

    for i, row in enumerate(rows):
        box_key = f"{path}_box_{i}"
        with st.container(border=True):
            cols = st.columns([2, 2, 1, 1])
            key = cols[0].text_input("Key", value=row.get("key", ""), key=f"{box_key}_key")
            dtype = cols[1].selectbox("Type", ["normal", "sub json"], 0 if row.get("type") == "normal" else 1, key=f"{box_key}_type")

            row["key"] = key
            row["type"] = dtype

            if dtype == "normal":
                val = cols[2].text_input("Value", value=row.get("value", ""), key=f"{box_key}_val")
                row["value"] = val
            else:
                if "children" not in row:
                    row["children"] = []
                render_editor(row["children"], path=f"{box_key}_child_{i}")

            if cols[3].button("❌", key=f"{box_key}_del"):
                to_delete.append(i)

    # Delete selected rows
    for i in reversed(to_delete):
        rows.pop(i)

    # Add new row button
    st.button("+ Add more", key=f"add_btn_{path}", on_click=add_row_callback, args=(path,))

# Build the final JSON output
def build_json(rows):
    result = {}
    for row in rows:
        key = row.get("key")
        if not key:
            continue
        if row["type"] == "normal":
            result[key] = row.get("value", "")
        elif row["type"] == "sub json":
            result[key] = build_json(row.get("children", []))
    return result

# Render the JSON form editor
render_editor(st.session_state["root_rows"], "root")

# Show formatted JSON result
st.markdown("### 🧾 Formatted JSON Output")
result_json = build_json(st.session_state["root_rows"])
st.json(result_json)

# Optional: Clear all data
if st.button("🧹 Clear All"):
    st.session_state["root_rows"] = [
        {"key": "project name", "type": "normal", "value": ""},
        {"key": "path", "type": "normal", "value": ""},
        {"key": "gdrive path", "type": "normal", "value": ""},
        {"key": "description", "type": "normal", "value": ""},
    ]