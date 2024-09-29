# Bud Excel Script Transpiler (Best)

Transpiler from Bud Excel Script (Bes) to Excel Formulas. The goal of Bes is to be a more readable format for larger Excel Formulas/projects. The workflow of Best is to write functions and define names in a Bes script and then add those names to your Excel Workbook, which can then be referenced in cell formulas. 

## Writing Bes Scripts
### Let Statements
To start with a basic example, suppose you want to define a name that points to some data you have put into some cells. In Excel you could do this with the name manager under the Formulas tab.

![alt text](<images/Name Manager Button.png>)

Then click "New" and enter the details of the name you want to define.

![alt text](<images/New Name Basic.png>)

In Bes, you could do this with a top-level `let` statement.

```Bes
let my_table = "Sheet!$A$1:$D$15";
```

You'll notice that the name is not quoted, but the expression for the name's value is. In Bes, quotes do not denote a string but an Excel expression. This is because the Bes transpiler (Best) does not parse the Excel expressions. It just constructs them and assigns them to names.

After you run Best to add your name to your workbook, you will now have a global name called `my_table` that can be referenced in cells or other Bes statements.

```Bes
let my_table_sum = "SUM(my_table)";
```

### Functions
In Excel you can use the `LAMBDA` function to create a function, and by storing that function into a defined name, you can then call that function in other contexts by that name. Therefore, functions are just defined names which use the Excel `LAMBDA` function. In Bes, there is special syntax for defining functions.

```Bes
fn max_of_3(a, b, c) {
    let max_so_far = if "a > b" {
        a
    } else {
        b
    };

    if "max_so_far > c" {
        max_so_far
    } else {
        c
    }
}
```

This function compiles to a defined name, `max_of_3` with a value of:

```
LAMBDA(a, b, c, LET(max_so_far, IF(a > b, a, b), IF(max_so_far > c, max_so_far, c)))
```

It is important to note that the body of the function is a block-*expression*. A block expression consists of 0 or more statements (`let` or `fn` so far) and an expression which is the return value. The if-*expression* uses block expressions as well. There is no such thing as an if-*statement*, which wouldn't make sense in a pure functional programming language. ("What's a pure functional programming language?" you ask? Watch this [CodeAesthetic video](https://www.youtube.com/watch?v=nuML9SmdbJ4&ab_channel=CodeAesthetic) to find out. The short version is "There shall be no state.". Outputs are always derived from the inputs deterministically. For better or for worse, Excel is a pure functional programming language, so we have to deal with it--or love it depending on who you are.)

### Exprs and Macros
We have talked about `let` statements which allow you to define global or local names and `fn` statements which are just `let` statements that use `LAMBDA`. Sometimes you want to write an expression that gets slotted in as-is rather than with a name. This is where `expr` statements come in. When you define an `expr`, Best compiles the expression into an Excel formula and then replaces the name with that formula wherever it appears surrounded by back-ticks. For example,

```Bes
expr tomorrow = "TODAY() + 1";
expr yesterday = "TODAY() - 1";
let two_days = "`tomorrow` - `yesterday`";
# Compiles to:
# (TODAY() + 1) - (TODAY() - 1)
```

(TODO Implement Macros)

`expr`s are the inline version of `let`. `macro`s are the inline version of `fn`. `macro`s in Bes have nothing to do with VBA macros. Each argument to the `macro` should be used in the `macro` as an `expr`.

```Bes
macro sum_multiply(a, b, c) {
    "(`a` + `b`) * `c`"
}

expr _e = "EXP(1)";
let two_plus_pi_times_e = "`sum_multiply(2, PI(), `_e`)`";
# Compiles to:
# (((2) + (PI())) * (EXP(1)))
```

### Importing
You can import other Bes scripts using an `import` statement at the top level.

```Bes
import other_script;
```

This will look for a file `other_script.bes` in the current directory. `let`s, `fn`s, `expr`s, `macro`s, and `import`s from `other_script.bes` will be compiled along-side those in the current script.

## Running Best
### Installing
Requirements:

* Java >= 11 (only the first time)
* Python 3 (I use Python 3.12)

First clone the repo:
```
git clone https://github.com/Budmeister/best.git
cd best
```

Then, either add `${BEST_ROOT}/bin` to the path or run it manually.

If it is on the path,
```
best <args>
```
Run it manually on Windows,
```
py $BEST_ROOT/bin/best.py <args>
```
Run it manually on Linux,
```
$BEST_ROOT/bin/best <args>
```

### Setup
The first time you run Best, it will prompt you before downloading the dependencies. If Java 11 is not installed, it will not be able to set up fully but will still offer to do the rest of the setup. The other dependnecies should download without problem.

* The language grammar is defined in ANLTR4 format, so the setup will download the ANLTR4 jar and run it to generate Python files.
* The Best core is meant to be run in a Python virtual environment, so the setup will create the virtual environment and install the dependencies in `requirements.txt`.
* Once the setup is complete or if setup was already complete, Best will run.

### Best CLI Arguments
The main use of Best is to compile a Bes script into defined names and add those names to a new workbook or an existing one. 

Use `-s` or `--script` to specify the Bes script.

Use `-i` or `--input` to specify a workbook to modify. (Optional)

Use `-o` or `--output` to specify a file to save the modified workbook to. (Optional) It will default to `input` if given or `BesBook.xlsx` otherwise.

Before the workbook is modified, a backup is saved to the backup directory specified by `-b` or `--backup-dir`. This defaults to `./backups` (from the directory where Best is called). Backups can be disabled with `--no-backup`.

An alternate use for Best is to inspect a workbook that Excel will not open. A few actions are provided and can be run with `-d <action>`. If `-d` is specified, then Best does the action rather than compiling.

* `clear-bes-defs`: Removes definitions from the specified input workbook which were previously compiled by Best.
* `clear-defs`: Removes all definitions from the specified input workbook.
* `print-defs`: Prints all definitions in the workbook.
* `delete-backups`: Deletes the backup-dir.

To get more CLI information run `best -h`.

## FAQs
### Why not use VBA?
There are two reasons for using Best over VBA.

1. Because of VBA's extended capabilities, Excel documents containing VBA macros are considered suspicious and potentially a security risk. The output of Best is runnable in vanilla Excel, so you can distribute Excel documents more freely.
2. VBA does not run in the mobile or web versions of Excel. If you're making a budget spreadsheet, for example, you need to be able to access it from your phone while you're out.

### Why write a compiler in Python?
My favorite languages are Rust and Python. My rule of thumb is *if I care about performance, use Rust; if I want it to be easy to write, use Python.* Generally, you care about performance with a compiler (although not as much as with an interpreter), but if your program is running on Excel, you've already given up on performance. 

More importantly, it was a goal of mine that the compiler be able to save the output directly to an Excel workbook without the user needing to copy and paste individual functions into Excel, and `openpyxl` is one of the best ways to do it. There may be a similar Rust library for reading and writing Excel workbooks, but I doubt it would be as developed as `openpyxl`. 

## Extreme Example
Suppose you want to implement a formula for the Levenshtein distance between two strings. An [implementation](https://gist.github.com/ncalm/715a0507805ff1df95cde2a04a9709be) from [ncalm](https://gist.github.com/ncalm) looks like this:

```
LEV = LAMBDA(a,b,[ii],[jj],[arr],
    LET(
      i,IF(ISOMITTED(ii),1,ii),
      j,IF(ISOMITTED(jj),1,jj),
      a_i,MID(a,i,1),
      b_j,MID(b,j,1),
      init_array,MAKEARRAY(
              LEN(a)+1,
              LEN(b)+1,
              LAMBDA(r,c,IFS(r=1,c-1,c=1,r-1,TRUE,0))
              ),
      cost,N(NOT(a_i=b_j)),
      this_arr,IF(ISOMITTED(arr),init_array,arr),
      option_a,INDEX(this_arr,i+1-1,j+1)+1,
      option_b,INDEX(this_arr,i+1,j+1-1)+1,
      option_c,INDEX(this_arr,i+1-1,j+1-1)+cost,
      new_val,MIN(option_a,option_b,option_c),
      overlay,MAKEARRAY(
              LEN(a)+1,
              LEN(b)+1,
              LAMBDA(r,c,IF(AND(r=i+1,c=j+1),new_val,0))
              ),
      new_arr,this_arr+overlay,
      new_i,IF(i=LEN(a),IF(j=LEN(b),i+1,1),i+1),
      new_j,IF(i<>LEN(a),j,IF(j=LEN(b),j+1,j+1)),
      is_end,AND(new_i>LEN(a),new_j>LEN(b)),
      IF(is_end,new_val,LEV(a,b,new_i,new_j,new_arr))
      )
);
```

The same formula written in Bes looks like this:

```Bes
fn lev(a,b,[ii],[jj],[arr]) {
    # Setup initial parameters
    let i = if "ISOMITTED(ii)" { "1" } else { ii };
    let j = if "ISOMITTED(jj)" { "1" } else { jj };
    let a_i = "MID(a,i,1)";
    let b_j = "MID(b,j,1)";

    fn init_array_gen(r, c) {
        if "r = 1" {
            "c-1"
        } else if "c = 1" {
            "r-1"
        } else {
            "0"
        }
    }
    let init_array = "MAKEARRAY(
        LEN(a)+1,
        LEN(b)+1,
        init_array_gen
    )";

    # Calculate new array entry
    let cost = "N(NOT(a_i=b_j))";
    let this_arr = if "ISOMITTED(arr)" { init_array } else { arr };
    let option_a = "INDEX(this_arr, i+1-1, j+1)   + 1";
    let option_b = "INDEX(this_arr, i+1,   j+1-1) + 1";
    let option_c = "INDEX(this_arr, i+1-1, j+1-1) + cost";
    let new_val = "MIN(option_a, option_b, option_c)";
    
    fn overlay_gen(r, c) {
        if "AND(r=i+1,c=j+1)" {
            new_val
        } else {
            "0"
        }
    }
    let overlay = "MAKEARRAY(
        LEN(a)+1,
        LEN(b)+1,
        overlay_gen
    )";
    let new_arr = "this_arr + overlay";

    # Recurse
    let new_i = if "i=LEN(a)" {
        if "j=LEN(b)" {
            "i+1"
        } else {
            "1"
        }
    } else {
        "i+1"
    };
    let new_j = if "i<>LEN(a)" {
        "j"
    } else if "j=LEN(b)" {
        "j+1"
    } else {
        "j+1"
    };
    let is_end = "AND(new_i > LEN(a), new_j > LEN(b))";
    if is_end {
        new_val
    } else {
        "lev(a, b, new_i, new_j, new_arr)"
    }
}
```

More realistically, the former implementation will look like this in Excel:
```
LAMBDA(a,b,[ii],[jj],[arr],LET(i,IF(ISOMITTED(ii),1,ii),j,IF(ISOMITTED(jj),1,jj),...
```

Not very easy to debug, and you don't even get comments. 
