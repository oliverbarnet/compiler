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
    def __init__(self, filename):
        self.filename = filename
        self.variables = {}
        self.raised_errors = []
        self.tokenized = self.tokenize()

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
        if name in self.variables and is_let: self.raise_err("variable 'let' redefine")
        if name not in self.variables and is_let: self.variables[name] = val

        if name in self.variables and not is_let: self.variables[name] = val
        if name not in self.variables and not is_let: self.raise_err("variable define without 'let'")

    def get_variable(self, name):
        if name in self.variables: return self.variables[name]
        if name not in self.variables: self.raise_err("undefined variable", name)

    def parse(self):
        output = ""
        for line in self.tokenized:
            first = line[0]

            # new var
            # 'let x = 2'
            if first == "let":
                name = line[1]
                equals = line[2]
                val = line[3]
                if name 

    def debug(self, show_tokenized=False):
        return [self.filename, self.variables, self.raised_errors, self.tokenized] if show_tokenized else [self.filename, self.variables, self.raised_errors]
filename = "test.txt"
compiler = Compiler(filename)
tokenized = compiler.tokenize()

compiler.parse()
