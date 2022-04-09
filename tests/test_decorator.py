from xyzflow import task, Parameter


@task(cacheable=False)
def power(a, n):
    print("hi")
    return a**n

@task(cacheable=True, task_name="HolyPower")
def power2(a, n, logger):
    print(f"hi: {logger}")
    logger.info("Example log")
    print("hi")
    return a**n*2

@task()
def calc( a, b ):
    return a+b

def test_decorator():
    a = Parameter(value=3, name="test")
    b = a + a
    c = power(b, n=a)
    assert c() == (3+3)**3
    c = power2(b, n=a)
    assert c() == (3+3)**3*2

    v = calc( 3, 5 )
    v2 = v + 1
    assert v2() == 9
    assert v2() == 9



