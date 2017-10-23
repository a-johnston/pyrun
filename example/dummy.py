def product(a:int, b:float, *args, **kwargs):
    """Literally just calculates a product lol
    :param a: first required positional argument
    :param b: second required positional argument
    """
    product = a * b
    for x in args:
        product *= x
    for x in kwargs.values():
        product *= x
    return product
