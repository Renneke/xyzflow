from xyzflow import task, Parameter


@task(cache_location=".xyz", cacheable=False)
def power(a, n):
    return a**n

@task(cache_location=".xyz123", cacheable=True)
def power2(a, n, logger):
    logger.write("Example log")
    return a**n*2

def test_decorator():
    a = Parameter(value=3, description="test")
    b = a + a
    c = power(b, n=a)
    assert c().result == (3+3)**3
    c = power2(b, n=a)
    assert c().result == (3+3)**3*2




