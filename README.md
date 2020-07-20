# Step 2: Chair repartition problem

## Installation

1. Create a virtual environment (I personally use Anaconda):

```conda create --name chair-rep python=3.8```

2. Activate it:

```conda activate chair-rep```

3. Install the requirements:

```pip install -r requirements.txt```

## How to read my work?

In code of the my solution to the problem is in the file `script.py`.

In the terminal,  by running the command below, you will get the expected solution of the problem:

```python script.py <path_to_the_txt_file>``` 

i.e. from the ROOT of the repository:

```python script.py rooms.txt```

To have better insights on my code, please open the `notebook/` folder and follow along the notebooks in this order:
- **1.explore_input_data.ipynb**: I discover the input date
- **2.solution_explanation.ipynb**: I explain in details the solution I found
- **3.complexity_evaluation.ipynb**: I evaluate the time and space complexity of my solution
- **4.additional_notebook.ipynb**: I deal with topics like: improvement of the code, other approaches of the problem...


At the root of the directory you also have a folder called `tests/` that performs tests on other inputs that I created and put under the folder `test_rooms/`. To run these tests, from the root directory you write the following command in the terminal from the ROOT of the repository:

```py.test```

Finally, if you use an IDE with a debugger, it will allow you to have a better visualization of the changes when running my algorithm. (ALERT SPOILER) My code moves elements in a 2D-plan. In the `script.py` file by:
1. Uncommenting the line 429 and giving a desired value to `k`
2. By setting a break point a the line 27
3. By watching the "variable" `console_print_of(apartment)`

You will see how the elements move in the plan.

**Enjoy!**

