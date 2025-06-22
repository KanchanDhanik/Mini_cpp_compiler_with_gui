class CodeGenerator:
    def __init__(self, symbol_table):
        self.symbol_table = symbol_table
        self.code = []
        self.label_count = 0
        
    def generate(self, ast):
        self.code = []
        self.label_count = 0
        
        self.code.append(".data")
        self.code.append("format_int: .asciz \"%d\\n\"")
        self.code.append("format_float: .asciz \"%f\\n\"")
        self.code.append("")
        self.code.append(".text")
        self.code.append(".global main")
        self.code.append("")
        
        for node in ast:
            if node[0] == 'function':
                self.generate_function(node)
                
        return "\n".join(self.code)
        
    def generate_function(self, node):
        _, return_type, func_name, params, body = node
        
        self.code.append(f"{func_name}:")
        self.code.append("  push %rbp")
        self.code.append("  mov %rsp, %rbp")
        
        # Generate code for body
        for stmt in body:
            self.generate_statement(stmt)
            
        self.code.append("  mov %rbp, %rsp")
        self.code.append("  pop %rbp")
        self.code.append("  ret")
        self.code.append("")
        
    def generate_statement(self, node):
        if node[0] == 'declaration':
            self.generate_declaration(node)
        elif node[0] == 'if':
            self.generate_if(node)
        elif node[0] == 'return':
            self.generate_return(node)
            
    def generate_declaration(self, node):
        _, var_type, var_name, expr = node
        
        # Allocate space for variable
        self.code.append(f"  sub $8, %rsp  # Allocate space for {var_name}")
        
        if expr:
            # Generate expression and store result
            self.generate_expression(expr)
            self.code.append(f"  mov %rax, -8(%rbp)  # Store {var_name}")
            
    def generate_if(self, node):
        _, condition, body, else_body = node
        label_else = self.new_label()
        label_end = self.new_label()
        
        # Generate condition
        self.generate_expression(condition)
        self.code.append("  cmp $0, %rax")
        self.code.append(f"  je {label_else}")
        
        # Generate if body
        for stmt in body:
            self.generate_statement(stmt)
        self.code.append(f"  jmp {label_end}")
        
        # Generate else body if exists
        self.code.append(f"{label_else}:")
        if else_body:
            for stmt in else_body:
                self.generate_statement(stmt)
                
        self.code.append(f"{label_end}:")
        
    def generate_return(self, node):
        _, expr = node
        if expr:
            self.generate_expression(expr)
            self.code.append("  mov %rax, %rbx  # Return value")
        self.code.append("  jmp .function_exit")
        
    def generate_expression(self, expr_node):
        if expr_node[0] == 'literal':
            value = expr_node[2]
            if expr_node[1] == 'int':
                self.code.append(f"  mov ${value}, %rax")
            elif expr_node[1] == 'float':
                self.code.append(f"  mov ${value}, %xmm0")
                
        elif expr_node[0] == 'variable':
            var_name = expr_node[1]
            self.code.append(f"  mov -8(%rbp), %rax  # Load {var_name}")
            
        elif expr_node[0] == 'binary_op':
            op = expr_node[1]
            left = expr_node[2]
            right = expr_node[3]
            
            self.generate_expression(right)
            self.code.append("  push %rax")
            self.generate_expression(left)
            self.code.append("  pop %rbx")
            
            if op == '+':
                self.code.append("  add %rbx, %rax")
            elif op == '-':
                self.code.append("  sub %rbx, %rax")
            elif op == '*':
                self.code.append("  imul %rbx, %rax")
            elif op == '/':
                self.code.append("  idiv %rbx")
            elif op == '>':
                self.code.append("  cmp %rbx, %rax")
                self.code.append("  setg %al")
                self.code.append("  movzb %al, %rax")
            elif op == '<':
                self.code.append("  cmp %rbx, %rax")
                self.code.append("  setl %al")
                self.code.append("  movzb %al, %rax")
            elif op == '==':
                self.code.append("  cmp %rbx, %rax")
                self.code.append("  sete %al")
                self.code.append("  movzb %al, %rax")
                
        return "%rax"
        
    def new_label(self):
        self.label_count += 1
        return f".L{self.label_count}"