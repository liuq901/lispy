import copy
import operator

def check(tokens):
    top = cnt = 0
    for token in tokens:
        if cnt == 0:
            top += 1
        if token == '(':
            cnt += 1
        elif token == ')':
            if cnt == 0:
                raise SyntaxError('Unpaired ")"')
            cnt -= 1
    if cnt > 0:
        raise SyntaxError('Unpaired "("')
    if top != 1:
        raise SyntaxError('Need exactly one top-level item')

def parse_token(tokens):
    if tokens[0] == '(':
        table = []
        tokens = tokens[1:]
        while tokens[0] != ')':
            term, tokens = parse_token(tokens)
            table.append(term)
        return False if table == [] else table, tokens[1:]
    try:
        atom = int(tokens[0])
    except ValueError:
        if tokens[0] == 't':
            atom = True
        elif tokens[0] == 'nil':
            atom = False
        else:
            atom = tokens[0]
    return atom, tokens[1:]

def parse(code):
    tokens = code.replace('(', ' ( ').replace(')', ' ) ').split()
    top = cnt = 0
    check(tokens)
    top, rest = parse_token(tokens)
    assert rest == []
    return top

def check_arg(name, expected, got):
    if expected != got:
        raise TypeError(f'{name} expected {expected} arguments, got {got}')

def function(name, param, body, env):
    def wrapper(*args):
        check_arg(name, len(param), len(args))
        new_env = copy.deepcopy(env)
        new_env.update(dict(zip(param, args)))
        return evaluate(body, new_env)
    return wrapper

def evaluate(code, env):
    assert code != []
    if isinstance(code, list):
        if code[0] == 'quote':
            check_arg('quote', 1, len(code[1:]))
            return code[1]
        elif code[0] == 'setq':
            check_arg('setq', 2, len(code[1:]))
            if not isinstance(code[1], str):
                raise TypeError(f'{code[1]} is not a symbol')
            env[code[1]] = evaluate(code[2], env)
            return env[code[1]]
        elif code[0] == 'defun':
            check_arg('defun', 3, len(code[1:]))
            if not isinstance(code[1], str):
                raise TypeError(f'{code[1]} is not a symbol')
            code[2] = to_list(code[2])
            if not isinstance(code[2], list):
                raise TypeError(f'arguments not a table')
            env[code[1]] = function(code[1], code[2], code[3], env)
            return code[1]
        elif code[0] == 'if':
            check_arg('if', 3, len(code[1:]))
            if evaluate(code[1], env):
                return evaluate(code[2], env)
            else:
                return evaluate(code[3], env)
        else:
            func = evaluate(code[0], env)
            args = [evaluate(x, env) for x in code[1:]]
            result = func(*args)
            return False if result == [] else result
    if isinstance(code, str):
        if code not in env:
            raise NameError(f'Cannot find symbol {code}')
        return env[code]
    return code

def format_(result):
    if isinstance(result, list):
        return f'({" ".join(format_(x) for x in result)})'
    if isinstance(result, bool):
        return {True: 'T', False: 'NIL'}[result]
    if isinstance(result, str):
        return result.upper()
    return str(result)

def to_list(x):
    if x == False:
        return []
    return x

def list_(*args):
    return list(args)

def main():
    env = {
        '+': operator.add,
        '-': operator.sub,
        '*': operator.mul,
        '/': operator.floordiv,
        'and': operator.and_,
        'or': operator.or_,
        'not': operator.not_,
        '<': operator.lt,
        '<=': operator.le,
        '>': operator.gt,
        '>=': operator.ge,
        '=': operator.eq,
        '/=': operator.ne,
        'car': lambda x: to_list(x)[0],
        'cdr': lambda x: to_list(x)[1:],
        'cons': lambda x, y: [x] + to_list(y),
        'append': lambda x, y: to_list(x) + to_list(y),
        'list': list_,
        'atom': lambda x: not isinstance(x, list),
        'null': lambda x: x == False,
        'equal': lambda x, y: x == y,
        'first': lambda x: to_list(x)[0],
        'last': lambda x: [to_list(x)[-1]],
        'abs': abs,
    }

    print('Simple LISP interpreter')
    print('Type "exit" to exit')
    while True:
        try:
            code = input('> ')
            print(code)
            if code == 'exit':
                break
            code = code.lower()
            code = parse(code)
            result = evaluate(code, env)
            result = format_(result)
            print(result)
        except AssertionError as e:
            raise e
        except Exception as e:
            print(f'{e.__class__.__name__}: {e}')

if __name__ == '__main__':
    main()
