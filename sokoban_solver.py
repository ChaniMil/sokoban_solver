import subprocess


def find_symbol_position(filename, symbol):
    """
    This function gets an input file - 2d xsb format board and a symbol,
    and returns a list of all the positions the symbol is at
    :param filename - xsb format board of sokoban
    :param symbol - a specific symbol in the sxb board
    :return a list with all the positions of the symbol in the file
    """
    with open(filename, 'r') as file:
        # read the contents of the file
        lines = file.readlines()
        lst = []
        # iterate through each row and column
        for row_idx, line in enumerate(lines):
            for col_idx, char in enumerate(line):
                if char == symbol:
                    lst += [[row_idx, col_idx]]
    return lst


def replace_ij(file_path, x, y, m, n):
    """
    Call this function on all of the positions of the board
    :param file_path: a specific file we wrote that handles the transitions in the smv in a general way
    :param x: the index of the current row
    :param y: the index of the current column
    :param m: number of rows in the board
    :param n: number of columns in the board
    :return: the changed content of the file that handles the transitions for the x,y place in the board
    """
    # Read the contents of the file
    with open(file_path, 'r') as file:
        content = file.read()

    new_content = content.replace('b[i][j]', 'b' + str(x) + str(y))
    new_content = new_content.replace('b[i][j-1]', 'b' + str(x) + str(y - 1) if y - 1 >= 0 else 'OUT_OF_BOUNDS')
    new_content = new_content.replace('b[i][j+1]', 'b' + str(x) + str(y + 1) if y + 1 < n else 'OUT_OF_BOUNDS')
    new_content = new_content.replace('b[i-1][j]', 'b' + str(x - 1) + str(y) if x - 1 >= 0 else 'OUT_OF_BOUNDS')
    new_content = new_content.replace('b[i+1][j]', 'b' + str(x + 1) + str(y) if x + 1 < m else 'OUT_OF_BOUNDS')
    new_content = new_content.replace('b[i][j-2]', 'b' + str(x) + str(y - 2) if y - 2 >= 0 else 'OUT_OF_BOUNDS')
    new_content = new_content.replace('b[i][j+2]', 'b' + str(x) + str(y + 2) if y + 2 < n else 'OUT_OF_BOUNDS')
    new_content = new_content.replace('b[i-2][j]', 'b' + str(x - 2) + str(y) if x - 2 >= 0 else 'OUT_OF_BOUNDS')
    new_content = new_content.replace('b[i+2][j]', 'b' + str(x + 2) + str(y) if x + 2 < m else 'OUT_OF_BOUNDS')
    new_content = new_content.replace('i', str(x))
    new_content = new_content.replace('j', str(y))
    return new_content


def erase_lines_with_pattern(file_path):
    """
    This function corrects smv file so that commands that are not logical are erased
    :param file_path: a smv file with all the transitions
    :return: NONE, changes the file
    """
    # Patterns to search for
    pattern = 'OUT_OF_BOUND'

    # Open the file for reading and writing
    with open(file_path, 'r+') as file:
        lines = file.readlines()  # Read all lines into a list
        # Rewind the file pointer to the beginning
        file.seek(0)
        # Iterate over each line in the list
        for line in lines:
            # Check if the line contains any of the specified patterns
            if pattern in line:
                continue  # Skip writing this line
            # If the line does not contain any of the specified patterns, write it back to the file
            file.write(line)
        file.truncate()


def run_nuxmv(model_filename, filename, nuxmv_position, ltl_optional=None):
    """
    This function creates an smv file and runs it on nuXmv
    :param model_filename: output file with the smv code
    :param filename: input file with the xsb format board
    :return: NONE, runs the code and writes the output
    """
    # find the dimensions of the board
    with open(filename, 'r') as file:
        first_line = file.readline().strip()
        n = len(first_line)
        # Increment the line count by 1, as we have already read the first line
        m = 1
        # Continue reading the rest of the lines to count the total number of lines
        for _ in file:
            m += 1
    # read input
    with open(filename, 'r') as file:
        content = file.read()

    # lines that will be written in the smv file
    deff = f"MODULE main\nDEFINE m := {m} ; n := {n} ;\n"
    var = "VAR\n    dr: {r, l, u, d, s};\n	i: 0..m+(-1);\n	j: 0..n+(-1);\n  right: boolean;\n  left: boolean;\n  down: boolean;\n  up: boolean;\n"
    # in the smv we define a variable bij for each position in the board,
    # that indicates how the board looks like in this position
    for i in range(m):
        for j in range(n):
            var += f"b{i}{j}: {{wall, target, flr, mantrg, bx, man, bxtrg}};\n"
    char_index = 0
    assign = "\nASSIGN\n"
    ltl = "\nLTLSPEC !F("
    char_mapping = {
        '#': "wall",
        '$': "bx",
        '.': "target",
        '@': "man",
        '+': "mantrg",
        '*': "bxtrg",
        '-': "flr"
    }
    for k in range(m):
        for l in range(n):
            char = content[char_index]
            while char == '\n' or char == ' ':  # Skip newline and space characters
                char_index += 1
                char = content[char_index]
            # replacing the symbols to letters because nuXmv handle it better
            char = char_mapping.get(char, char)
            # defining the init value as read from input
            assign += f"\tinit(b{k}{l}) := {char};\n"
            char_index += 1
            # the ltl is finally there are no boxes on floor in the board, it's defined here
            if k == m - 1 and l == n - 1:
                ltl += f"(b{k}{l} != bx));"
            else:
                ltl += f"(b{k}{l} != bx) & "
    # finding where the man is standing in the beginning
    try:
        i, j = find_symbol_position(filename, "@")[0][0], find_symbol_position(filename, "@")[0][1]
    except:
        i, j = find_symbol_position(filename, "+")[0][0], find_symbol_position(filename, "+")[0][1]
    # initiating the variables left
    assign += f"\tinit(i) := {i};\n\tinit(j) := {j};\n\tinit(dr) := s;\n\tinit(left) := FALSE;\n\tinit(right) := " \
              f"FALSE;\n\tinit(down) := FALSE;\n\tinit(up) := FALSE;\n\t "

    # reads a file with the transitions for i,j and dr
    with open('next_dr_ij.txt', 'r') as source_file:
        content = source_file.read()
    # variables that indicate where can the man move to
    up = "\ti = 0 | i = 1: FALSE;\n"
    down = "\ti = m+(-1): FALSE;\n"
    right = "\tj = n+(-1): FALSE;\n"
    left = "\tj = 0 | j = 1: FALSE;\n"
    for x in range(1, m):
        for y in range(1, n):
            up += f"\ti = {x} & j = {y} & (b{x - 1}{y} = flr | b{x - 1}{y} = target): TRUE;\n"
            if x <= m - 2:
                down += f"\ti = {x} & j = {y} & (b{x + 1}{y} = flr | b{x + 1}{y} = target): TRUE;\n"
            if y <= n - 2:
                right += f"\ti = {x} & j = {y} & (b{x}{y + 1} = flr | b{x}{y + 1} = target): TRUE;\n"
            left += f"\ti = {x} & j = {y} & (b{x}{y - 1} = flr | b{x}{y - 1} = target): TRUE;\n"
            if x != 1:
                up += f"\ti = {x} & j = {y} & (b{x - 1}{y} = bx | b{x - 1}{y} = bxtrg) & (b{x - 2}{y} != bx & b{x - 2}{y} != bxtrg & b{x - 2}{y} != wall): TRUE;\n"
            if x <= m - 3:
                down += f"\ti = {x} & j = {y} & (b{x + 1}{y} = bx | b{x + 1}{y} = bxtrg) & (b{x + 2}{y} != bx & b{x + 2}{y} != bxtrg & b{x + 2}{y} != wall): TRUE;\n"
            if y <= n - 3:
                right += f"\ti = {x} & j = {y} & (b{x}{y + 1} = bx | b{x}{y + 1} = bxtrg) & (b{x}{y + 2} != bx & b{x}{y + 2} != bxtrg & b{x}{y + 2} != wall): TRUE;\n"
            if y != 1:
                left += f"\ti = {x} & j = {y} & (b{x}{y - 1} = bx | b{x}{y - 1} = bxtrg) & (b{x}{y - 2} != bx & b{x}{y - 2} != bxtrg & b{x}{y - 2} != wall): TRUE;\n"
    tru = "\tTRUE: FALSE;\nesac;\n"
    txt = deff + var + assign + content + "next(up):= case\n" + up + tru + "next(down):= case\n" + down + tru + "next(right):= case\n" + right + tru + "next(left):= case\n" + left + tru

    # adding the board transitions, written in a b[i][j] in the file,
    # and replacing them to be for every index in bij format
    for x in range(m):
        for y in range(n):
            txt += replace_ij("next_board.txt", x, y, m, n)
    if ltl_optional is None:
        txt += ltl
    else:
        txt += ltl_optional
    with open(model_filename, "w") as f:
        f.write(txt)
    erase_lines_with_pattern(model_filename)
    print(f"Input saved to {model_filename}")

    # Run the smv file created, on nuXmv
    nuxmv_process = subprocess.Popen([nuxmv_position, model_filename],
                                     stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                     universal_newlines=True)
    output_filename = model_filename.split(".")[0] + ".out"

    stdout, _ = nuxmv_process.communicate()

    # Save output to file
    with open(output_filename, "w") as f:
        f.write(stdout)
    print(f"Output saved to {output_filename}")
    return output_filename


if __name__ == '__main__':
    nuxmv_position = "C:\\Users\\Owner\\OneDrive\\שולחן העבודה\\אימות פורמלי\\proj\\nuXmv.exe"
    input_file = "your_input_path"  # put your input file path here
    output_file = "your_output_path"  # out the output file path here
    run_nuxmv(output_file, input_file, nuxmv_position)
    # running all the input boards - our examples
    # for i in range(1, 8):
        # run_nuxmv(f"outputs\\smv_input{i}.smv", f"inputs\\input{i}.txt", nuxmv_position)
