import jax
import jax.numpy as jnp
from dbgpy import dbg


def test_jax_no_compile():
    print()

    def addone(x):
        dbg(x)
        return x + 1

    x = jnp.array([1, 2, 3])
    y = addone(x)
    print(y)


def test_jax_compile_time():
    print()

    @jax.jit
    @jax.vmap
    def addone(x: jax.Array):
        dbg(x)
        return x + 1

    x = jnp.array([1, 2, 3])
    y = addone(x)
    print(y)


def test_jax_multiline_array():
    print()

    arr = jnp.ones((3, 3))
    dbg(arr)


