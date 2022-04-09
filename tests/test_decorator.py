from xyzflow import task, Parameter


@task(cacheable=False)
def power(a, n):
    print("hi")
    return a**n

@task(cacheable=True)
def power2(a, n, logger):
    print(f"hi: {logger}")
    logger.info("Example log")
    print("hi")
    return a**n*2

def test_decorator():
    a = Parameter(value=3, name="test")
    b = a + a
    c = power(b, n=a)
    assert c() == (3+3)**3
    c = power2(b, n=a)
    assert c() == (3+3)**3*2




