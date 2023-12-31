import random


async def div_generator(start, end, flag):
    divisors = set()
    num = start
    for i in range(flag):
        s = random.randint(2, 10)
        if num * s >= end:
            break

        num *= s
        divisors.add(s)

    _ = random.choice(tuple(divisors))
    return (num, _, num // _)


captcha_data = {
    '+': (1, 20, True, None),
    '-': (1, 20, False, None),
    '*': (1, 10, True, None),
    '/': (1, 100, 3, div_generator)
}


async def generate_captcha():
    operation = random.choice(tuple(captcha_data.items()))
    if operation[1][3] is None:
        loperand = random.randint(operation[1][0], operation[1][1])
        roperand = random.randint(operation[1][0],
                                  operation[1][1] if operation[1][2] else loperand)
        e = f'{loperand} {operation[0]} {roperand}'
        val = eval(e)

    else:
        loperand, roperand, val = await operation[1][3](operation[1][0], operation[1][1], operation[1][2])
        e = f'{loperand} {operation[0]} {roperand}'

    return (e, str(val))
