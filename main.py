class Compiler:
    def __init__(self, filename, debug_mode=False):
        self.filename = filename
        self.variables = {}
        self.raised_errors = []
        self.function_parameters = {}
        self.function_codes = {}
        self.debug_mode = debug_mode
        self.tokenized = self.tokenize()

    def is_int(self, x):
        return False if False in [True if item in "1234567890" else False for item in x] else True

    def base_err(self, message, id=None, type="ValueError"):
        if type == "ValueError":
            try: raise ValueError(f"\033[31mERR: {message}\033[0m")
            except ValueError as e:
                print(e)
                return id

    def s_to_l(self, s):
        return [item.strip() for item in s.strip("[]").split(",")]

    def raise_err(self, c, target=None):
        if c == "undefined variable" or c == "ERR0": self.raised_errors.append(self.base_err(f"Variable '{target}' not defined.", 0))
        if c == "variable 'let' redefine" or c == "ERR1": self.raised_errors.append(self.base_err("Cannot use keyword 'let' to re-define a variable.", 1))
        if c == "variable define without 'let'" or c == "ERR2": self.raised_errors.append(self.base_err("Cannot define variable without keyword 'let'.", 2))
        if c == "printing raw integer" or c == "ERR3": self.raised_errors.append(self.base_err(f"Cannot 'print' raw integer ({target}), must be in string form or in variable form."))
        if c == "cannot name variable an integer" or c == "ERR4": self.raised_errors.append(self.base_err(f"A variable cannot be named an integer ({target})."))
        if c == "variable not defined when printing" or c == "ERR5": self.raised_errors.append(self.base_err(f"Variable {target} not defined (printing)."))
        if c == "variable not defined when doing arithmetic" or c == "ERR6": self.raised_errors.append(self.base_err(f"Variable {target} not defined (arithmetci)."))
        if c == "arithmetic sign not recognized" or c == "ERR7": self.raised_errors.append(self.base_err(f"Operator {target} not recognized when doing arithmetic."))
        if c == "undefined function called" or c == "ERR8": self.raised_errors.append(self.base_err(f"Function {target} not defined at time of call."))
        try: raise RuntimeError()
        except RuntimeError: pass

    def tokenize(self):
        with open(self.filename, "r") as file:
            lines = file.readlines()
        lines_2 = []
        for line in lines: lines_2.append(line.split("\n")) if line != "\n" else None
        lines_3 = []
        for line in lines_2:
            if "" in line: line.pop(line.index(""))
            lines_3.append(line[0].split(" "))
        return lines_3

    def new_variable(self, is_let, name, val):
        if name in "1234567890": self.raised_err("cannot name variable an integer", name)

        if val != None:
            val = int(val) if str(val) in "1234567890" else str(val).strip("\"").strip("\'")
        if name in self.variables and is_let: self.raise_err("variable 'let' redefine")
        if name not in self.variables and is_let: self.variables[name] = val

        if name in self.variables and not is_let: self.variables[name] = val
        if name not in self.variables and not is_let: self.raise_err("variable define without 'let'")

    def check_syntax(self, line, target_type):
        if target_type == "variable dynamic declaration":
            try: l, name, equals, val = line[0], line[1], line[2], line[3]
            except IndexError: return False
            if l == "let" and type(name) == str and equals == "=" and type(val) in [int, str] and len(line) == 4: return True
        elif target_type == "variable static declaration":
            l, name = line[0], line[1]
            if l == "let" and type(name) == str and len(line) == 2: return True
        return False

    def out(self, value, debug_mode=None, line=-1):
        if debug_mode == None: debug_mode = self.debug_mode
        return [line, value] if debug_mode else value

    def parse_line(self, line, debug_mode=False, index=-1):
        first = line[0]
        output = []

        # function declaration
        # fn x [a, b]: print a + b
        if first == "fn":
            name = line[1]
            fixed_line = " ".join(line)
            vars = self.s_to_l(f"[{fixed_line.split("[")[1].split("]")[0]}]")
            function = fixed_line.split(":")[1].lstrip()
            self.function_parameters[name] = vars
            self.function_codes[name] = function

        # assigning new value to variable
        # x = 3
        elif first in self.variables:
            value = line[2]
            self.new_variable(False, first, value)

        # variable arithmetic
        # 'math x = 3 + 3'
        elif first == "math":
            target, a, op, b = line[1], line[3], line[4], line[5]
            if op not in "+-*/": self.raise_err("arithmetic sign not recognized", op)

            # both 'a' and 'b' are variables
            if a in self.variables and b in self.variables:
                value = eval(f"{self.variables[a]} {op} {self.variables[b]}")
                self.new_variable(False, target, value)
            else:
                # neither are variables
                if a not in self.variables and b not in self.variables:
                    # neither are integers
                    if not self.is_int(a) and not self.is_int(b):
                        self.raise_err("variable not defined when doing arithmetic", a)
                        self.raise_err("variable not defined when doing arithmetic", b)
                    # one not an integer
                    elif not self.is_int(a) or not self.is_int(b):
                        if not self.is_int(a): self.raise_err("variable not defined when doing arithmetic", a)
                        else: self.raise_err("variable not defined when doing arithmetic", b)
                    elif self.is_int(a) and self.is_int(b):
                        value = eval(f"{a} {op} {b}")
                        self.new_variable(False, target, value)

                # one is a variable
                elif a in self.variables or b in self.variables:
                    # 'a' is int, 'b' is var
                    if self.is_int(a) and b in self.variables:
                        value = eval(f"{a} {op} {self.variables[b]}")
                        self.new_variable(False, target, value)
                    # 'a' is var, 'b' is int
                    elif a in self.variables and self.is_int(b):
                        value = eval(f"{self.variables[a]} {op} {b}")
                        self.new_variable(False, target, value)

        # new var
        # 'let x = 2'
        # let x
        # 'let x = "hello world"'
        elif first == "let":
            if len(line) == 4 or len(line) == 2:
                if self.check_syntax(line, "variable dynamic declaration"):
                    self.new_variable(True, line[1], line[3])
                elif self.check_syntax(line, "variable static declaration"):
                    self.new_variable(True, line[1], None)
            elif len(line) > 4:
                fixed_line = " ".join(line).split("\"")
                fixed_line[:] = [item for item in fixed_line if item != ""]
                self.new_variable(True, fixed_line[0].split(" ")[1], fixed_line[1])


        # print text
        # 'print "hi"' or 'print var' or 'print "hello world"'
        elif first == "print":
            fixed_line = " ".join(line)
            if "\"" in fixed_line:
                fixed_line = fixed_line.split("\"")
                fixed_line[:] = [item.strip() for item in fixed_line if item != ""]
                out = fixed_line[1]

                output.append(self.out(out, debug_mode, index))
            else:
                if len(line) == 2:
                    out = line[1]

                    # string without quotes, isn't variable
                    if out not in self.variables:
                        self.raise_err("variable not defined when printing", out)
                    # string without quotes, is a variable
                    elif out in self.variables:
                        val = self.variables[out]
                        output.append(self.out(val, debug_mode, index))
                    # raw integer without quotes
                    elif out in "1234567890":
                        self.raise_err("printing raw integer", out)
                else:
                    out = " ".join(line).split("print ")[1].split(" ")
                    for i, o in enumerate(out):
                        if o in self.variables: out[i] = str(self.variables[o])
                    x = eval(" ".join(out))
                    output.append(self.out(x, debug_mode, index))
        return output

    def parse(self, debug_mode=None):
        debug_mode = self.debug_mode if debug_mode == None else None
        first, o, output = "", "", []
        for index, line in enumerate(self.tokenized):
            first = line[0]
            if first != "call": 
                o = self.parse_line(line, debug_mode, index)
                output.append(o) if o != [] else None
            # call n = x [a, b]
            else:
                target_name = line[1]
                function_name = line[3]
                args = self.s_to_l(" ".join(line).split("[")[1])
                if function_name in self.function_codes and function_name in self.function_parameters:
                    function_code = self.function_codes[function_name]
                    function_params = self.function_parameters[function_name]
                else:
                    self.raise_err("undefined function called", function_name)
                    break
                fc_line = function_code.split(" ")

                for i, item in enumerate(fc_line):
                    if item in function_params:
                        fc_line[i] = args[function_params.index(item)]
                o = sum(self.parse_line(fc_line, debug_mode, index))

                self.new_variable(False, target_name, o)
        return output

    def debug(self, show_tokenized=None):
        if show_tokenized == None: show_tokenized = self.debug_mode
        return [[self.function_codes, self.function_parameters], self.filename, self.variables, self.raised_errors, self.tokenized] if show_tokenized else [[self.function_codes, self.function_parameters], self.filename, self.variables, self.raised_errors]
filename = "test.txt"
compiler = Compiler(filename, False)

out, dbg = compiler.parse(), compiler.debug()

for o in out: print(o)

# print(dbg)