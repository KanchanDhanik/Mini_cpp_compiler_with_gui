class SemanticAnalyzer:
    def __init__(self, symbol_table):
        self.symbol_table = symbol_table
        self.errors = []
        self.warnings = []
        
    def analyze(self, ast):
        self.errors = []
        self.warnings = []
        
        for node in ast:
            if node[0] == 'function':
                self.symbol_table.enter_scope(node[2])
                self.check_function(node)
                self.symbol_table.exit_scope()
            elif node[0] == 'declaration':
                self.check_declaration(node)
                
        return len(self.errors) == 0
        
    def check_function(self, node):
        _, return_type, func_name, params, body = node
        
        # Add parameters to symbol table
        for p_type, p_name in params:
            if p_name:
                self.symbol_table.add_symbol(p_name, p_type)
                
        # Check function body
        for stmt in body:
            if stmt[0] == 'declaration':
                self.check_declaration(stmt)
            elif stmt[0] == 'return':
                self.check_return(stmt, return_type)
                
    def check_declaration(self, node):
        _, var_type, var_name, expr = node
        
        if expr:
            # Check expression types
            expr_type = self.infer_expression_type(expr)
            if expr_type and expr_type != var_type:
                self.errors.append(f"Type error: Cannot assign {expr_type} to {var_type} variable '{var_name}'")
                
    def check_return(self, node, expected_type):
        _, expr = node
        if expr:
            expr_type = self.infer_expression_type(expr)
            if expr_type != expected_type:
                self.errors.append(f"Return type mismatch: Expected {expected_type}, got {expr_type}")
        elif expected_type != 'void':
            self.errors.append(f"Non-void function must return a value")
                
    def infer_expression_type(self, expr_node):
        if expr_node[0] == 'literal':
            return expr_node[1]  # 'int', 'float', etc.
        elif expr_node[0] == 'variable':
            symbol = self.symbol_table.lookup(expr_node[1])
            return symbol['type'] if symbol else None
        elif expr_node[0] == 'assignment':
            return self.infer_expression_type(expr_node[1])
        elif expr_node[0] == 'binary_op':
            left_type = self.infer_expression_type(expr_node[2])
            right_type = self.infer_expression_type(expr_node[3])
            
            # For arithmetic operations, promote to float if either is float
            if expr_node[1] in ['+', '-', '*', '/']:
                if 'float' in [left_type, right_type]:
                    return 'float'
                return 'int'
            return 'bool'  # For comparisons
        elif expr_node[0] == 'unary_op':
            return self.infer_expression_type(expr_node[2])
            
        return None