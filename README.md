This README provides instructions and information on how to set up, use, and understand the Sokoban Solver using NuXmv via Python.

Sokoban is a classic puzzle game where the player pushes boxes onto designated storage locations within a warehouse maze.
This solver uses the NuXmv model checker to automatically find solutions for given Sokoban levels.

Note:  The file "sokoban_solver.py" is the regular solver, and the file "iterative_solver.py", is a solver that uses an iterative way.

HOW TO RUN THE CODES:
1. Download the files to your computer.
2. In the file "sokoban_solver.py" and in the file "iterative_solver.py" change the variables: 
  2.1. nuxmv_position - the path to your nuxmv.exe file in your computer.
  2.2. input_file - the path to a txt file containg a valid XSB format board, without extra spaces or lines
  2.3. output_file - the path to the output file (the file doesn't have to exist)
3. In the file "part3.py" change the variables:
   3.1. model_dir - a directory containing .smv file you want to measure time for
   3.2. nuxmv_directory - the directory where the nuxmv.exe file is at in your computer
4. Enjoy!
