import ast

class CodeValidator:
    ALLOWED_NODES = {ast.Expr, ast.Call, ast.Attribute, ast.Name, ast.Constant}
    
    @classmethod
    def validate(cls, code: str) -> bool:
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if type(node) not in cls.ALLOWED_NODES:
                    return False
            return True
        except:
            return False 