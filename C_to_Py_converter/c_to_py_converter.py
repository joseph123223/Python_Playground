import re
import numpy as np

def convert_c_array_to_numpy_array(file_path, var_name="robinW_kInnoPs2Nps"):
    with open(file_path, 'r') as f:
        content = f.read()

    pattern = rf"{re.escape(var_name)}\s*\[.*?\]\s*=\s*\{{(.*?)\}};"
    match = re.search(pattern, content, re.DOTALL)

    if not match:
        raise ValueError(f"Variable '{var_name}' not found in file.")

    array_str = match.group(1)

    array_str = re.sub(r'//.*', '', array_str)
    array_str = array_str.replace('{{', '[').replace('}}', ']')
    array_str = array_str.replace('{', '[').replace('}', ']')


    try:
        parsed_array = eval(array_str)
    except Exception as e:
        raise SyntaxError(f"Failed to parse array: {e}")

    return np.array(parsed_array)

if __name__ == "__main__":
    input_file = "robinW_table.h"
    output_file = "robinW_kInnoPs2Nps.npy"

    data = convert_c_array_to_numpy_array(input_file)
    print("Loaded shape:", data.shape)

    np.save(output_file, data)
    print(f"Saved to {output_file}")
