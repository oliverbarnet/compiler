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

    def goodbye(self):
        try: raise RuntimeError()
        except RuntimeError: pass

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
        if c == "incorrect if statement logic syntax" or c == "ERR9": self.raised_errors.append(self.base_err(f"Incorrect syntax for if statement logic. ({target})"))
        if c== "missing quotes at variable declaration" or c == "ERR10": self.raised_errors.append(self.base_err(f"Variable {target} is missing quotes at declaration."))

        self.goodbye()

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

    def is_print_concat(self, string):
        return len([item for item in string.split("\"")[1:] if item != ""]) > 1 or "+" in string

    def out(self, value, debug_mode=None, line=-1):
        if debug_mode == None: debug_mode = self.debug_mode
        return [line, value] if debug_mode else value

    def replace(self, string, index, replace, char="%"):
        s, count = list(string), []
        for i, character in enumerate(s):
            if character == char: count.append(i)
        s[count[index]] = replace
        return "".join(s)

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
        #      OR
        # 'let concat x = "hi " + name'
        elif first == "let":
            # regular cases
            if "concat" not in line:
                if len(line) == 4 or len(line) == 2:
                    if self.check_syntax(line, "variable dynamic declaration"):
                        self.new_variable(True, line[1], line[3])
                    elif self.check_syntax(line, "variable static declaration"):
                        self.new_variable(True, line[1], None)
                elif len(line) > 4:
                    fixed_line = " ".join(line)
                    # string ('let x = "hello world"')
                    if "\"" in fixed_line:
                        fixed_line = [item for item in fixed_line.split("\"") if item != ""]
                        try: self.new_variable(True, fixed_line[0].split(" ")[1], fixed_line[1])
                        except IndexError: self.raise_err("missing quotes at variable declaration", fixed_line[0].split(" ")[1])
                    # not string (vars or ints)
                    else:
                        args = fixed_line.split("=")[1].strip().split(" ")
                        first_num = args[0]
                        second_num = args[2]

                        # both variables
                        if first_num in self.variables and second_num in self.variables:
                            for arg_i, arg in enumerate(args):
                                if arg not in "+-*/": args[arg_i] = str(self.variables[arg])
                            final_varout = eval(" ".join(args))

                            self.new_variable(True, fixed_line.split(" ")[1], final_varout)
                        
                        # both numbers
                        elif self.is_int(first_num) and self.is_int(second_num):
                            final_varout = eval(" ".join(args))
                            self.new_variable(True, fixed_line.split(" ")[1], final_varout)
                        
                        # 'a' int, 'b' var
                        elif self.is_int(first_num) and second_num in self.variables:
                            for arg_i, arg in enumerate(args):
                                if arg in self.variables: args[arg_i] = str(self.variables[arg])
                            final_varout = eval(" ".join(args))
                            self.new_variable(True, fixed_line.split(" ")[1], final_varout)

                        # 'a' var, 'b' int
                        elif first_num in self.variables and self.is_int(second_num):
                            for arg_i, arg in enumerate(args):
                                if arg in self.variables: args[arg_i] = str(self.variables[arg])
                            final_varout = eval(" ".join(args))
                            self.new_variable(True, fixed_line.split(" ")[1], final_varout)

            # concat cases
            # 'let concat x = "hi " + name', name is defined
            elif line[1] == "concat":
                target = line[2]
                value = " ".join(line).split("=")[1].strip().split("+")
                for section_index, section in enumerate(value):
                    # string
                    if "\"" in section:
                        updated_val = [item for item in section.split("\"") if item != "" and item != " "][0]
                        value[section_index] = updated_val
                    
                    # variable
                    elif section.strip() in self.variables:
                        section = section.strip()
                        variable_value = self.variables[section]
                        # number 
                        if self.is_int(variable_value):
                            value[section_index] = str(variable_value).strip()
                        # string
                        else:
                            value[section_index] = variable_value.strip()
                final_out = ""
                for val in value: final_out += val
                self.new_variable(True, target, final_out)

        # get user input
        # 'input x "hello world"', 'x' must be defined as var
        # 'input x', 'x' must be defined as var
        elif first == "input":
            target = line[1]
            # 'input x'
            if len(line) == 2:
                value = input()
                self.new_variable(False, target, value)
            
            # 'input x "what is your name? "'
            else:
                prompt = " ".join(line).split("\"")[1].lstrip()
                value = input(prompt)
                self.new_variable(False, target, value)
                
        # print text
        # 'print "hi"' or 'print var' or 'print "hello world"'
        elif first == "print":
            fixed_line = " ".join(line)

            # has some type of string (concatenation or not)
            if "\"" in fixed_line:
                is_concat = self.is_print_concat(fixed_line)

                out = None
                # isn't concatenation, just string with spaces
                if not is_concat:
                    fixed_line = fixed_line.split("\"")
                    fixed_line = [item.strip() for item in fixed_line if item != ""]
                    out = fixed_line[1]
                
                # is a concatenation
                else:
                    out_args = fixed_line.split("print ")[1].split(", ")
                    s = [item for item in out_args[0].split("\"") if item != ""][0]
                    vars = fixed_line.split(", [")[1].rstrip("]").split(", ")
                    percent_index = 0
                    s_list = list(s)
                    for char_i, char in enumerate(s_list):
                        if char == "%":
                            corresponding_var = vars[percent_index]
                            if corresponding_var in self.variables:
                                corresponding_var_val = str(self.variables[corresponding_var])
                                s_list[char_i] = corresponding_var_val
                            else:
                                cleaned_string = corresponding_var.strip("\"")
                                s_list[char_i] = cleaned_string
                            percent_index += 1

                    out = "".join(s_list)
                output.append(self.out(out, debug_mode, index))
            
            # just variables
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
        
        watch_out = ["call", "if"]
        for index, line in enumerate(self.tokenized):
            first = line[0]
            # regular
            if first not in watch_out:
                try: o = self.parse_line(line, debug_mode, index)
                except KeyboardInterrupt: self.raise_err("keyboard interrupt during parsing")
                output.append(o) if o != [] else None
            
            # call n = x [a, b]
            elif first == "call":
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
                out = self.parse_line(fc_line, debug_mode, index)
                try: o = sum(out)
                except TypeError: o = " ".join(out).strip("[]")
                self.new_variable(False, target_name, o)
            
            # if x = 3: print x
            elif first == "if":
                args = " ".join(line).split(":")[0].split("if ")[1].split(" ")
                
                for arg_index, arg in enumerate(args):
                    # variable
                    if arg in self.variables:
                        s = str(self.variables[arg])
                        if self.is_int(s): args[arg_index] = str(s)
                        else: args[arg_index] = f"\"{str(s)}\""

                    # equals sign (turn into '==' for eval)
                    if arg == "=": args[arg_index] = "=="
                
                fixed_args = " ".join(args)
                arg_output, code, code_output = "", "", ""

                try: 
                    arg_output = eval(fixed_args)
                    code = " ".join(line).split(":")[1].strip().split(" ")
                    code_output = self.parse_line(code, debug_mode, index) if arg_output == True else None
                except SyntaxError as e: 
                    self.raise_err("incorrect if statement logic syntax", e)
                    self.goodbye()
                
                if code_output != None: output = code_output if code_output != None else None
        return output

    def debug(self, show_tokenized=None):
        if show_tokenized == None: show_tokenized = self.debug_mode
        return [[self.function_codes, self.function_parameters], self.filename, self.variables, self.raised_errors, self.tokenized] if show_tokenized else [[self.function_codes, self.function_parameters], self.filename, self.variables, self.raised_errors]
filename = "test.txt"
compiler = Compiler(filename, False)

out, dbg = compiler.parse(), compiler.debug()

for o in out: print(o[0])
print("idrk man")

#print(f"{dbg=}")