import sys
import os

sys.path.append(os.path.abspath("apps/api"))

try:
    import src.main
    print("SUCCESS: src.main imported correctly!")
except Exception as e:
    import traceback
    traceback.print_exc()
