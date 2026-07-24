from scpi_pkg.scdataMulti import scdataMulti
import inspect

sig = inspect.signature(scdataMulti)
print("scdataMulti Parameters:")
print("=" * 70)
for name, param in sig.parameters.items():
    default = param.default if param.default != inspect.Parameter.empty else "(required)"
    print(f"{name:30} default: {default}")
