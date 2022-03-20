# dbgpy

Debug print inspired by Rust's `dbg!` macro.

Example:

```python
from dbgpy import dbg
import numpy as np

arr = np.linspace(0, 10)

dbg(arr.shape)
```

Outputs
```
main.py:6: arr.shape = (50,)
```

