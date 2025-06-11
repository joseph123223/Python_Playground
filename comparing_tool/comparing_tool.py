import sys

def compare_files(file1, file2):
    with open(file1, 'r', encoding='utf-8') as f1, open(file2, 'r', encoding='utf-8') as f2:
        lines1 = f1.readlines()
        lines2 = f2.readlines()

    max_len = max(len(lines1), len(lines2))
    differences = 0

    print(f"\nComparing '{file1}' and '{file2}':\n")
    for i in range(max_len):
        line1 = lines1[i].rstrip() if i < len(lines1) else "<No line>"
        line2 = lines2[i].rstrip() if i < len(lines2) else "<No line>"

        if line1 != line2:
            differences += 1
            print(f"Line {i + 1}:")
            print(f"  File 1: {line1}")
            print(f"  File 2: {line2}\n")

    if differences == 0:
        print("The files are identical.")
    else:
        print(f"Found {differences} different line(s).")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python file_compare.py file1.txt file2.txt")
        sys.exit(1)

    compare_files(sys.argv[1], sys.argv[2])
