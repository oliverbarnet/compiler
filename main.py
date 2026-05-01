def tokenize(filename):
    with open(filename, "r") as file:
        lines = file.readlines()
    lines_2 = []
    for line in lines: lines_2.append(line.split("\n")) if line != "\n" else None
    lines_3 = []
    for line in lines_2:
        if "" in line: line.pop(line.index(""))
        lines_3.append(line[0].split(" "))
    return lines_3

class Compiler:
    def __init__(self, filename, debug_mode=False):
        self.filename = filename
        self.variables = {}
        self.raised_errors = []
        self.tokenized = self.tokenize()
        self.debug_mode = debug_mode

    def base_err(self, message, id=None, type="ValueError"):
        if type == "ValueError":
            try: raise ValueError(f"\033[31mERR: {message}\033[0m")
            except ValueError as e:
                print(e)
                return id

    def raise_err(self, c, target=None):
        if c == "undefined variable" or c == "ERR0": self.raised_errors.append(self.base_err(f"Variable '{target}' not defined.", 0))
        if c == "variable 'let' redefine" or c == "ERR1": self.raised_errors.append(self.base_err("Cannot use keyword 'let' to re-define a variable.", 1))
        if c == "variable define without 'let'" or c == "ERR2": self.raised_errors.append(self.base_err("Cannot define variable without keyword 'let'.", 2))
        if c == "printing raw integer" or c == "ERR3": self.raised_errors.append(self.base_err(f"Cannot 'print' raw integer ({target}), must be in string form or in variable form."))
        if c == "cannot name variable an integer" or c == "ERR4": self.raised_errors.append(self.base_err(f"A variable cannot be named an integer ({target})."))
        if c == "variable not defined when printing" or c == "ERR5": self.raised_errors.append(self.base_err(f"Variable {target} not defined (printing)."))
    
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

        val = int(val) if val in "1234567890" else val.strip("\"").strip("\'")
        if name in self.variables and is_let: self.raise_err("variable 'let' redefine")
        if name not in self.variables and is_let: self.variables[name] = val

        if name in self.variables and not is_let: self.variables[name] = val
        if name not in self.variables and not is_let: self.raise_err("variable define without 'let'")

    def get_variable(self, name):
        if name in self.variables: return self.variables[name]
        if name not in self.variables: self.raise_err("undefined variable", name)

    def check_syntax(self, line, target_type):
        if target_type == "variable declaration":
            l = line[0]
            name = line[1]
            equals = line[2]
            val = line[3]
            if l == "let" and type(name) == str and equals == "=" and type(val) in [int, str]: return True
        return False
    
    def out(self, value, debug_mode=None, line=-1):
        if debug_mode == None: debug_mode = self.debug_mode
        return [line, value] if debug_mode else value

    def parse(self, debug_mode=None):
        if debug_mode == None: debug_mode = self.debug_mode
        output = []
        for index, line in enumerate(self.tokenized):
            first = line[0]

            # new var
            # 'let x = 2'
            if first == "let":
                if self.check_syntax(line, "variable declaration"):
                    self.new_variable(True, line[1], line[3])

            # print text
            # 'print "hi"' or 'print var'
            
            # 'print "hello world"'
            if first == "print":
                fixed_line = " ".join(line)
                if "\"" in fixed_line:
                    fixed_line = fixed_line.split("\"")
                    fixed_line[:] = [item.strip() for item in fixed_line if item != ""]
                    out = fixed_line[1]

                    output.append(self.out(out, debug_mode, index))
                else:
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
                

        return output

    def debug(self, show_tokenized=None):
        if show_tokenized == None: show_tokenized = self.debug_mode
        return [self.filename, self.variables, self.raised_errors, self.tokenized] if show_tokenized else [self.filename, self.variables, self.raised_errors]
filename = "test.txt"
compiler = Compiler(filename, False)

out, dbg = compiler.parse(), compiler.debug()

for o in out: print(o)
print(dbg)
