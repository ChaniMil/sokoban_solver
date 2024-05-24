from sokoban_solver import find_symbol_position, run_nuxmv
import time


def read_board_from_file(input_board):
    """
    This function reads the xsb board and returns the board as a 2d array
    :param input_board: input file with the board
    :return: the board as a 2d array
    """
    board = []
    with open(input_board, 'r') as file:
        for line in file:
            board.append(list(line.strip()))
    return board


def update_board(board, i, j, value):
    """
    This function is called on each index in the board,
    it updates the board after solving a box,
    so that all the steps taken are considered for the next iteration
    :param board: the xsb sokoban board
    :param i: row index in board
    :param j: column index in board
    :param value: the value to update in the board
    :return: the updated board
    """
    if value == 'flr':
        board[i][j] = '-'
    elif value == 'man':
        board[i][j] = '@'
    elif value == 'wall':
        board[i][j] = '#'
    elif value == 'target':
        board[i][j] = '.'
    elif value == 'bx':
        board[i][j] = '$'
    elif value == 'bxtrg':
        board[i][j] = '*'
    elif value == 'mantrg':
        board[i][j] = '+'


def process_changes(output_file, input_file):
    """
    This function is updating the board after each iteration,
    it puts a wall in the solved target, and updates the board as the iteration changed it
    :param output_file: the smv output after iteration
    :param input_file: the input file with the board to update
    :return: No solution in case the board isn't solvable, None otherwise
    """
    board = read_board_from_file(input_file)
    with open(output_file, 'r') as file:
        lines = file.readlines()
    # Ensure there are at least 27 lines in the file
    if len(lines) < 27:
        return 'No solution'
    # Check if line 27 contains the word "TRUE", line 27 is where the specification is at
    if "false" not in lines[26]:  # line 27 in file is lines[26] in 0-based indexing
        return 'No solution'
    for line in lines:
        line = line.strip()
        if '-- Loop starts here' in line:  # After this we don't need to update the board
            break
        if '=' in line:
            parts = line.split('=')
            if len(parts) == 2:
                left_part = parts[0].strip()
                right_part = parts[1].strip()
                if right_part in ['flr', 'man', 'wall', 'target', 'bx', 'man', 'mantrg', 'bxtrg']:
                    # Extract the variable name and parse i and j
                    variable = left_part
                    if len(variable) == 3 and variable[0] == 'b':
                        i = int(variable[1])
                        j = int(variable[2])
                        update_board(board, i, j, right_part)

        # Writing the updated board to the file
        with open(input_file, 'w') as file:
            for row in board:
                file.write(''.join(row) + '\n')


def iterative_solution(input_file, output_file, nuxmv_position):
    """
    This handles each iteration, we go through all the targets,
    and each iteration cover the specific target with the box
    after a box is covered we update the input in a way that the box on the target solved can't move
    after each iteration we update all the changes made in the board when solving the box
    :param input_file: the input with the board
    :param output_file: the file to write the input in
    :param nuxmv_position: nuxmv position in the computer
    :return: None
    """
    targets = find_symbol_position(input_file, ".") + find_symbol_position(input_file, "+")
    # We don't need iterations, cause there is only one target
    if len(targets) <= 1:
        start_time = time.time()
        run_nuxmv(output_file, input_file, nuxmv_position)
        stop_time = time.time()
        print("Time: ", stop_time - start_time)
    else:
        for i in range(len(targets)):
            print(targets)
            # The ltl is putting a box on the target
            ltl = f"LTLSPEC !F(b{targets[i][0]}{targets[i][1]} = bxtrg);"

            # Measure time
            start_time = time.time()
            run_nuxmv(output_file, input_file, nuxmv_position, ltl)
            stop_time = time.time()

            print(f"Iteration #{i+1}: ", stop_time-start_time)
            sol = process_changes(output_file.split(".")[0] + ".out", input_file)
            if sol == 'No solution':
                print(sol)
                return
            with open(input_file, 'r') as file:
                content = file.readlines()

            # Modify the specific position of the target covered with '#'
            row = targets[i][0]
            col = targets[i][1]
            line = list(content[row])
            line[col] = '#'
            content[row] = ''.join(line)

            # Write the modified content back to the file
            with open(input_file, 'w') as file:
                file.writelines(content)


if __name__ == "__main__":
    nuxmv_position = "C:\\Users\\Owner\\OneDrive\\שולחן העבודה\\אימות פורמלי\\proj\\nuXmv.exe"
    input_file = "inputs/input7.txt"
    output_file = "iterative_outputs/output_part4_7.smv"
    # save the original content in the file, cause we change it when solving
    with open(input_file, 'r') as file:
        original_content = file.read()
    iterative_solution(input_file, output_file, nuxmv_position)
    # writes back the original input
    with open(input_file, 'w') as file:
        file.write(original_content)
